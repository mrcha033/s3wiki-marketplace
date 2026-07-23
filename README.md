# S3 Research Memory Private Marketplace

Private Codex and Claude Code marketplace artifacts for S3 Research Memory workflows.

## Install

This repository is private. Authenticate to GitHub first, then register the repository as a marketplace source:

```bash
codex plugin marketplace add https://github.com/mrcha033/s3wiki-marketplace.git
codex plugin add build-lab-meeting-slides@s3wiki-marketplace
```

For Claude Code:

```bash
claude plugin marketplace add https://github.com/mrcha033/s3wiki-marketplace.git
claude plugin install build-lab-meeting-slides@s3wiki-marketplace
```

Do not publish this repository or its template assets. The supplied PPTX remains the visual source of truth and is retained only in the private plugin package.

## S3 Research Memory dependency

`build-lab-meeting-slides` does not bundle the `dev-6a58e7a411988191a74fda9cfcf6b604` remote app. That app is a separately provisioned Codex dependency and currently has no portable source tree in this repository. If it is available in the client, use its S3 Research Memory tools for optional evidence retrieval; the slide skill itself remains usable from local files and does not contain credentials.

The canonical service is the centrally operated MCP endpoint documented by the private `s3wiki` repository. Keep tokens in the caller environment or approved secret storage; never commit them here.

## Release contract

- Keep `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` synchronized.
- Keep `skills/build-lab-meeting-slides` and `plugins/build-lab-meeting-slides/skills/build-lab-meeting-slides` byte-identical.
- Run the bundled skill tests and both marketplace validators before publishing.
- Treat HTML as a disposable prototype; the final presentation must be rebuilt as editable native PPTX objects.
- Keep structural QA, visual review, and SHA-pinned user acceptance as separate claims.
