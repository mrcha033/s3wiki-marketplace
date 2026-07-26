# Private integration boundary

## Codex

The `s3-research-memory` Codex plugin references the user-created registered app
identified by:

```text
asdk_app_6a58e7a411988191a74fda9cfcf6b604
```

The marketplace carries only the `.app.json` mapping. It does not copy, rehost,
or claim to distribute the central MCP implementation. Installing the private
plugin does not grant access to an account that cannot use the registered app.

## Claude Code

Claude Code cannot use the OpenAI app ID. Its plugin manifest declares the
central Streamable HTTP endpoint directly:

```text
https://s3wiki.yonsei.ac.kr/mcp
```

The Authorization header references `S3RM_MCP_TOKEN` from the user's environment.
The token value must never be committed.

## S3 Research Memory policy

The slide skill may use retrieved lessons or evidence as inputs, but it must not
create a parallel database or write directly to MediaWiki. Use the central MCP
service and its documented write/authentication policy. Never place MCP tokens,
private wiki exports, or raw evidence dumps in this repository.

## Validation boundary

Private marketplace installation proves only that the plugin packages are
discoverable and installable. MCP connectivity, write authorization, and deck
quality require separate runtime and user-acceptance checks.
