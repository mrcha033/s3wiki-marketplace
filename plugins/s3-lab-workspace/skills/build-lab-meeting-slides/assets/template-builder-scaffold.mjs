#!/usr/bin/env node

// Deck-specific authoring starts from the validated template starter. INPUT_PPTX
// resolves to template-starter.pptx; keep this import/export spine intact so
// template-fidelity QA can prove exact clone/edit.
import fs from "node:fs/promises";
import crypto from "node:crypto";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const requiredEnv = [
  "INPUT_PPTX",
  "OUTPUT_PPTX",
  "LABDECK_CONFIG",
  "LABDECK_SLIDE_PLAN",
  "LABDECK_TEMPLATE_MAP",
];
for (const name of requiredEnv) {
  if (!process.env[name]) throw new Error(`missing required environment variable ${name}`);
}

const [config, plan, frameMap] = await Promise.all([
  fs.readFile(process.env.LABDECK_CONFIG, "utf8").then(JSON.parse),
  fs.readFile(process.env.LABDECK_SLIDE_PLAN, "utf8").then(JSON.parse),
  fs.readFile(process.env.LABDECK_TEMPLATE_MAP, "utf8").then(JSON.parse),
]);
const projectRoot = await fs.realpath(process.cwd());
if (!config || typeof config !== "object" || Array.isArray(config)) {
  throw new Error("LABDECK_CONFIG must contain a JSON object");
}
if (config.deck?.authoring_mode === "html-assisted-native" && !process.env.LABDECK_NATIVE_REBUILD_MANIFEST) {
  throw new Error("html-assisted-native authoring requires LABDECK_NATIVE_REBUILD_MANIFEST");
}
if (!Array.isArray(plan?.slides) || !Array.isArray(frameMap?.outputSlides)) {
  throw new Error("slide plan and template frame map must both contain slide arrays");
}

const configuredMinimumBodyPt = Number(config.style?.minimum_body_pt ?? 16);
if (!Number.isFinite(configuredMinimumBodyPt) || configuredMinimumBodyPt <= 0) {
  throw new Error("style.minimum_body_pt must be a finite positive number");
}
const PT_TO_CSS_PX = 96 / 72;
const minimumBodyPx = configuredMinimumBodyPt * PT_TO_CSS_PX;
const bodyTypeface = String(config.style?.body_font || "Arial");
const activePalette = config.style?.active_palette;
if (!activePalette || typeof activePalette !== "object" || Array.isArray(activePalette)) {
  throw new Error("style.active_palette must be a semantic color-token object");
}
const activePaletteTokens = ["background", "surface", "ink", "muted", "primary", "focus", "soft"];
const configuredPaletteTokens = Object.keys(activePalette).sort();
if (JSON.stringify(configuredPaletteTokens) !== JSON.stringify([...activePaletteTokens].sort())) {
  throw new Error(`style.active_palette must use exactly: ${activePaletteTokens.join(", ")}`);
}
const normalizedPalette = {};
for (const token of activePaletteTokens) {
  if (!/^#[0-9A-F]{6}$/iu.test(String(activePalette[token] || ""))) {
    throw new Error(`style.active_palette.${token} must be a six-digit hex color`);
  }
  normalizedPalette[token] = String(activePalette[token]).toUpperCase();
}
const paletteHashPayload = Object.fromEntries(
  Object.keys(normalizedPalette).sort().map((token) => [token, normalizedPalette[token]]),
);
const activePaletteHash = crypto
  .createHash("sha256")
  .update(JSON.stringify(paletteHashPayload))
  .digest("hex");
if (String(config.style?.active_palette_sha256 || "").toLowerCase() !== activePaletteHash) {
  throw new Error("style.active_palette_sha256 does not match the closed active palette");
}
const requirePaletteTokens = config.qa?.visual_contract?.require_palette_tokens !== false;
const allowedTextRoles = new Set(
  config.qa?.content_contract?.allowed_text_roles ?? [
    "figure-label",
    "axis-label",
    "legend",
    "callout",
    "annotation",
    "source",
    "metadata",
    "code",
    "table",
    "equation",
  ],
);
const allowedVisualRoles = new Set(
  config.qa?.visual_contract?.allowed_visual_roles ?? [
    "diagram-node",
    "connector",
    "data-mark",
    "axis",
    "plot",
    "table",
    "code",
    "image",
    "annotation",
    "boundary",
  ],
);

const presentation = await PresentationFile.importPptx(
  await FileBlob.load(process.env.INPUT_PPTX),
);
const slides = presentation.slides.items;
if (slides.length !== plan.slides.length || slides.length !== frameMap.outputSlides.length) {
  throw new Error(
    `starter/plan/frame-map slide counts differ: ${slides.length}/${plan.slides.length}/${frameMap.outputSlides.length}`,
  );
}

function findShapeByName(slide, name) {
  return slide.shapes.items.find((item) => item.name === name);
}

function contentValue(entry, ref) {
  if (entry.content && entry.content[ref] !== undefined) return entry.content[ref];
  if (entry[ref] !== undefined) return entry[ref];
  return undefined;
}

function allowedRewriteContentRefs(entry) {
  const allowed = new Set(["title_claim"]);
  if (String(entry?.template_frame?.role ?? "content").trim().toLowerCase() === "cover") {
    for (const field of ["subtitle", "meeting_subject"]) {
      allowed.add(field);
    }
  }
  return allowed;
}

function requireNonEmptyString(value, label) {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value;
}

function resolvePaletteColor(value, label, fallbackToken) {
  const raw = value === undefined || value === null || value === "" ? fallbackToken : String(value).trim();
  if (raw.toLowerCase() === "none") return "none";
  const token = raw.startsWith("$") ? raw.slice(1) : raw;
  if (Object.hasOwn(activePalette, token)) return activePalette[token];
  const normalized = raw.toUpperCase();
  const matchingToken = Object.entries(activePalette)
    .find(([, color]) => String(color).toUpperCase() === normalized)?.[0];
  if (matchingToken) {
    if (requirePaletteTokens) {
      throw new Error(`${label} must use semantic token ${matchingToken}, not raw hex ${raw}`);
    }
    return activePalette[matchingToken];
  }
  throw new Error(`${label} must use one of the active palette tokens: ${Object.keys(activePalette).join(", ")}`);
}

function normalizedLine(rawLine, label, fallbackToken = "primary") {
  const line = rawLine ?? {};
  if (typeof line !== "object" || Array.isArray(line)) {
    throw new Error(`${label} must be an object`);
  }
  return {
    ...line,
    fill: resolvePaletteColor(line.fill, `${label}.fill`, fallbackToken),
  };
}

function normalizeZone(zone, label) {
  if (!zone || typeof zone !== "object" || Array.isArray(zone)) {
    throw new Error(`${label} must be an object`);
  }
  const normalized = {};
  for (const key of ["x", "y", "w", "h"]) {
    const value = Number(zone[key]);
    const invalid = !Number.isFinite(value) || ((key === "w" || key === "h") ? value <= 0 : value < 0);
    if (invalid) {
      throw new Error(`${label}.${key} must be finite and ${key === "w" || key === "h" ? "positive" : "non-negative"}`);
    }
    normalized[key] = value;
  }
  return normalized;
}

function normalizePosition(position, label) {
  if (!position || typeof position !== "object" || Array.isArray(position)) {
    throw new Error(`${label} must be an object`);
  }
  const normalized = {};
  for (const key of ["left", "top", "width", "height"]) {
    const value = Number(position[key]);
    const invalid = !Number.isFinite(value) || ((key === "width" || key === "height") ? value <= 0 : value < 0);
    if (invalid) {
      throw new Error(`${label}.${key} must be finite and ${key === "width" || key === "height" ? "positive" : "non-negative"}`);
    }
    normalized[key] = value;
  }
  return normalized;
}

function sourceImageDimensions(bytes, extension, label) {
  if (extension === ".gif") {
    if (bytes.length < 10 || !["GIF87a", "GIF89a"].includes(bytes.subarray(0, 6).toString("ascii"))) {
      throw new Error(`${label} is not a valid GIF`);
    }
    return { width: bytes.readUInt16LE(6), height: bytes.readUInt16LE(8) };
  }
  if (extension === ".png") {
    const pngSignature = "89504e470d0a1a0a";
    if (bytes.length < 24 || bytes.subarray(0, 8).toString("hex") !== pngSignature) {
      throw new Error(`${label} is not a valid PNG`);
    }
    return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
  }
  if (extension === ".jpg" || extension === ".jpeg") {
    if (bytes.length < 4 || bytes[0] !== 0xff || bytes[1] !== 0xd8) {
      throw new Error(`${label} is not a valid JPEG`);
    }
    let cursor = 2;
    const sofMarkers = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]);
    while (cursor + 8 < bytes.length) {
      if (bytes[cursor] !== 0xff) {
        cursor += 1;
        continue;
      }
      const marker = bytes[cursor + 1];
      cursor += 2;
      if (marker === 0xd8 || marker === 0xd9) continue;
      if (cursor + 2 > bytes.length) break;
      const segmentLength = bytes.readUInt16BE(cursor);
      if (segmentLength < 2 || cursor + segmentLength > bytes.length) break;
      if (sofMarkers.has(marker) && segmentLength >= 7) {
        return {
          width: bytes.readUInt16BE(cursor + 5),
          height: bytes.readUInt16BE(cursor + 3),
        };
      }
      cursor += segmentLength;
    }
    throw new Error(`${label} has no readable JPEG size marker`);
  }
  throw new Error(`${label} has an unsupported image extension`);
}

function validateEditTargets(entry, mapEntry) {
  if (!Array.isArray(mapEntry?.editTargets)) {
    throw new Error(`slide ${entry.slide} frame map editTargets must be an array`);
  }
  const supportedActions = new Set(["keep", "rewrite", "add"]);
  const rewriteNames = new Set();
  let addCount = 0;
  for (const [index, target] of mapEntry.editTargets.entries()) {
    const label = `slide ${entry.slide} editTargets[${index}]`;
    if (!target || typeof target !== "object" || Array.isArray(target)) {
      throw new Error(`${label} must be an object`);
    }
    if (!supportedActions.has(target.action)) {
      throw new Error(`${label} has unsupported action ${JSON.stringify(target.action)}`);
    }
    if (target.action === "rewrite") {
      const sourceName = requireNonEmptyString(target.sourceName, `${label}.sourceName`);
      const contentRef = requireNonEmptyString(target.contentRef, `${label}.contentRef`);
      if (!allowedRewriteContentRefs(entry).has(contentRef)) {
        throw new Error(
          `${label}.contentRef ${JSON.stringify(contentRef)} is not an allowed role-bound visible-copy field`,
        );
      }
      if (rewriteNames.has(sourceName)) {
        throw new Error(`${label} duplicates rewrite target ${sourceName}`);
      }
      rewriteNames.add(sourceName);
    }
    if (target.action === "add") {
      addCount += 1;
      if (target.newPrimitiveAllowed !== true || target.mustNotOverlapInherited !== true) {
        throw new Error(
          `${label} must explicitly set newPrimitiveAllowed and mustNotOverlapInherited to true`,
        );
      }
      requireNonEmptyString(target.reason, `${label}.reason`);
      target.zone = normalizeZone(target.zone, `${label}.zone`);
    }
  }
  if (addCount > 1) {
    throw new Error(`slide ${entry.slide} has ${addCount} add actions; this scaffold supports one bounded insertion zone`);
  }
}

function rewriteInheritedTargets(slide, entry, mapEntry) {
  for (const target of mapEntry.editTargets.filter((item) => item.action === "rewrite")) {
    const value = contentValue(entry, target.contentRef);
    if (value === undefined || value === null) {
      throw new Error(
        `slide ${entry.slide} is missing content for inherited target ${target.sourceName} (${target.contentRef})`,
      );
    }
    const shape = findShapeByName(slide, target.sourceName);
    if (!shape) {
      throw new Error(`slide ${entry.slide} cannot resolve inherited shape name ${target.sourceName}`);
    }
    shape.text = String(value);
  }
}

function inside(inner, outer) {
  const right = inner.left + inner.width;
  const bottom = inner.top + inner.height;
  return (
    inner.left >= outer.x &&
    inner.top >= outer.y &&
    right <= outer.x + outer.w &&
    bottom <= outer.y + outer.h
  );
}

function normalizedTextStyle(rawStyle, defaultFontSizePt, defaults = {}, label = "native element text style") {
  const style = rawStyle ?? {};
  if (typeof style !== "object" || Array.isArray(style)) {
    throw new Error(`${label} must be an object`);
  }
  const { fontSizePt, fontSize, color, ...rest } = style;
  if (fontSizePt !== undefined && fontSize !== undefined) {
    throw new Error("set only one of fontSizePt (points) or fontSize (CSS pixels)");
  }
  let requestedPx;
  if (fontSizePt !== undefined) {
    const requestedPt = Number(fontSizePt);
    if (!Number.isFinite(requestedPt) || requestedPt <= 0) {
      throw new Error("fontSizePt must be a finite positive number");
    }
    requestedPx = requestedPt * PT_TO_CSS_PX;
  } else if (fontSize !== undefined) {
    requestedPx = Number(fontSize);
    if (!Number.isFinite(requestedPx) || requestedPx <= 0) {
      throw new Error("fontSize must be a finite positive CSS-pixel value");
    }
  } else {
    requestedPx = Number(defaultFontSizePt) * PT_TO_CSS_PX;
  }
  return {
    ...rest,
    ...defaults,
    fontSize: Math.max(minimumBodyPx, requestedPx),
    typeface: style.typeface || defaults.typeface || bodyTypeface,
    color: resolvePaletteColor(color, `${label}.color`, defaults.color || "ink"),
  };
}

async function addDeclaredElements(slide, entry, mapEntry) {
  const insertion = mapEntry.editTargets.find((item) => item.action === "add");
  const elements = entry.native_elements || [];
  if (!Array.isArray(elements)) {
    throw new Error(`slide ${entry.slide} native_elements must be an array`);
  }
  if (!insertion && elements.length) {
    throw new Error(`slide ${entry.slide} declares new elements but its frame map has no bounded insertion`);
  }
  const orderedElements = elements
    .map((spec, index) => ({ spec, index }))
    .sort((left, right) => Number(right.spec?.type === "line") - Number(left.spec?.type === "line") || left.index - right.index);
  for (const { spec, index } of orderedElements) {
    if (!spec || typeof spec !== "object" || Array.isArray(spec)) {
      throw new Error(`slide ${entry.slide} native_elements[${index}] must be an object`);
    }
    const label = `slide ${entry.slide} native_elements[${index}]`;
    if (spec.text !== undefined && !allowedTextRoles.has(String(spec.text_role || "").toLowerCase())) {
      throw new Error(`${label}.text_role must be one of: ${[...allowedTextRoles].join(", ")}`);
    }
    if (spec.type !== "text" && !allowedVisualRoles.has(String(spec.visual_role || "").toLowerCase())) {
      throw new Error(`${label}.visual_role must be one of: ${[...allowedVisualRoles].join(", ")}`);
    }
    if (spec.shadow !== undefined) {
      throw new Error(`${label} may not declare a decorative shadow`);
    }
    const position = normalizePosition(
      spec.position,
      `${label}.position`,
    );
    if (!inside(position, insertion.zone)) {
      throw new Error(`slide ${entry.slide} native_elements[${index}] escapes its inherited content zone`);
    }
    if (spec.type === "line") {
      if (spec.head !== undefined || spec.tail !== undefined) {
        throw new Error(
          `${label} free line arrowheads are not render-proven; use a native rightArrow shape or a project-specific attached connector`,
        );
      }
      slide.shapes.add({
        geometry: "line",
        name: spec.name || `s${entry.slide}-line-${index + 1}`,
        position,
        fill: "none",
        line: normalizedLine(spec.line || { style: "solid", width: 2 }, `${label}.line`),
      });
    } else if (spec.type === "text") {
      const item = slide.shapes.add({
        geometry: "textbox",
        name: spec.name || `s${entry.slide}-text-${index + 1}`,
        position,
        fill: "none",
        line: { style: "solid", fill: "none", width: 0 },
      });
      item.text = String(spec.text ?? "");
      item.text.style = normalizedTextStyle(spec.style, 16.5, {
        typeface: bodyTypeface,
        color: "ink",
        bold: Boolean(spec.style?.bold),
        alignment: spec.style?.alignment || "left",
      }, `${label}.style`);
    } else if (spec.type === "image") {
      const assetPath = requireNonEmptyString(spec.asset_path, `${label}.asset_path`);
      if (path.isAbsolute(assetPath)) {
        throw new Error(`${label}.asset_path must be project-relative`);
      }
      const resolvedAsset = await fs.realpath(path.resolve(projectRoot, assetPath));
      const projectPrefix = `${projectRoot}${path.sep}`;
      if (!resolvedAsset.startsWith(projectPrefix)) {
        throw new Error(`${label}.asset_path escapes the deck project`);
      }
      const extension = path.extname(resolvedAsset).toLowerCase();
      const contentTypes = new Map([
        [".gif", "image/gif"],
        [".jpeg", "image/jpeg"],
        [".jpg", "image/jpeg"],
        [".png", "image/png"],
      ]);
      const contentType = contentTypes.get(extension);
      if (!contentType) {
        throw new Error(`${label}.asset_path must be PNG, JPEG, or GIF`);
      }
      const alt = requireNonEmptyString(spec.alt, `${label}.alt`);
      requireNonEmptyString(spec.source_ref, `${label}.source_ref`);
      if (extension === ".gif") {
        requireNonEmptyString(spec.motion_ref, `${label}.motion_ref`);
      }
      const bytes = await fs.readFile(resolvedAsset);
      const dimensions = sourceImageDimensions(bytes, extension, `${label}.asset_path`);
      if (dimensions.width <= 0 || dimensions.height <= 0) {
        throw new Error(`${label}.asset_path has invalid dimensions`);
      }
      if (spec.fit !== "cover") {
        const sourceRatio = dimensions.width / dimensions.height;
        const frameRatio = position.width / position.height;
        const ratioDelta = Math.abs(sourceRatio - frameRatio) / sourceRatio;
        if (ratioDelta > 0.005) {
          throw new Error(
            `${label}.position aspect ratio must match its source image within 0.5% when fit is contain; use a source-matched frame so strict bbox QA remains exact`,
          );
        }
      }
      const blob = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
      const item = slide.images.add({
        blob,
        contentType,
        alt,
        fit: spec.fit === "cover" ? "cover" : "contain",
        position,
      });
      item.name = spec.name || `s${entry.slide}-image-${index + 1}`;
    } else if (spec.type === "shape") {
      const item = slide.shapes.add({
        geometry: spec.geometry || "rect",
        name: spec.name || `s${entry.slide}-shape-${index + 1}`,
        position,
        fill: resolvePaletteColor(spec.fill, `${label}.fill`, "none"),
        line: normalizedLine(spec.line || { style: "solid", width: 2 }, `${label}.line`),
      });
      if (spec.text !== undefined) {
        item.text = String(spec.text);
        item.text.style = normalizedTextStyle(spec.textStyle, configuredMinimumBodyPt, {
          typeface: bodyTypeface,
          color: "ink",
        }, `${label}.textStyle`);
      }
    } else {
      throw new Error(
        `slide ${entry.slide} native_elements[${index}] has unsupported type ${JSON.stringify(spec.type)}`,
      );
    }
  }
}

// This shipped scaffold intentionally exposes no arbitrary custom-builder hook:
// an unchecked callback could modify inherited chrome or escape the bounded
// insertion zone. Advanced authoring requires a separate project-specific
// builder plus an independent full-slide template-fidelity review.

for (let index = 0; index < slides.length; index += 1) {
  const slide = slides[index];
  const entry = plan.slides[index];
  const mapEntry = frameMap.outputSlides[index];
  if (entry.slide !== index + 1 || mapEntry.outputSlide !== index + 1) {
    throw new Error(`slide plan/frame-map order mismatch at output slide ${index + 1}`);
  }
  validateEditTargets(entry, mapEntry);
  rewriteInheritedTargets(slide, entry, mapEntry);
  await addDeclaredElements(slide, entry, mapEntry);
  const needsBody = mapEntry.editTargets.some((item) => item.action === "add");
  if (needsBody && !(entry.native_elements || []).length) {
    throw new Error(
      `slide ${entry.slide} needs a bounded native mechanism/content implementation. Add native_elements to slide-plan.json; do not ship an empty template frame.`,
    );
  }
}

const exported = await PresentationFile.exportPptx(presentation);
await exported.save(process.env.OUTPUT_PPTX);
