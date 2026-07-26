# S3 Research Memory Private Marketplace

Private Codex and Claude Code marketplace artifacts for S3 Research Memory workflows.
The marketplace exposes two independently installable plugins:

- `s3-research-memory`: the central research-memory MCP integration
- `build-lab-meeting-slides`: the editable lab-meeting deck workflow

## Install

This repository is private. Authenticate to GitHub first, then register the repository as a marketplace source:

```bash
codex plugin marketplace add https://github.com/mrcha033/s3wiki-marketplace.git
codex plugin add s3-research-memory@s3wiki-marketplace
codex plugin add build-lab-meeting-slides@s3wiki-marketplace
```

For Claude Code:

```bash
claude plugin marketplace add https://github.com/mrcha033/s3wiki-marketplace.git
claude plugin install s3-research-memory@s3wiki-marketplace
claude plugin install build-lab-meeting-slides@s3wiki-marketplace
```

Claude Code reads the central MCP connection from the plugin and expands
`S3RM_MCP_TOKEN` from the user environment at runtime. The repository never
contains the token value. After installing, start a new session and use `/mcp`
to confirm that `plugin:s3-research-memory:s3-research-memory` is connected.

Do not publish this repository or its template assets. The supplied PPTX remains the visual source of truth and is retained only in the private plugin package.

## S3 Research Memory integration

The Codex package maps the registered
`dev-6a58e7a411988191a74fda9cfcf6b604` app through `.app.json`. The Claude Code
package points to the same centrally operated MCP service through an inline
`mcpServers` declaration. Neither package copies the server implementation or
stores credentials.

`build-lab-meeting-slides` remains independently usable from local files. Install
`s3-research-memory` when the deck workflow should retrieve or save shared
lessons and evidence.

The canonical service is `https://s3wiki.yonsei.ac.kr/mcp`. Keep tokens in the
caller environment or approved secret storage; never commit them here.

## Release contract

- Keep `.agents/plugins/marketplace.json` and `.claude-plugin/marketplace.json` synchronized.
- Keep the Codex app ID and Claude MCP endpoint mapped to the same central service.
- Keep `skills/build-lab-meeting-slides` and `plugins/build-lab-meeting-slides/skills/build-lab-meeting-slides` byte-identical.
- Run the bundled skill tests and both marketplace validators before publishing.
- Treat HTML as a disposable prototype; the final presentation must be rebuilt as editable native PPTX objects.
- Keep structural QA, visual review, and SHA-pinned user acceptance as separate claims.
