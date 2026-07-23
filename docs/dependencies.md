# Private dependency boundary

## `dev-6a58e7a411988191a74fda9cfcf6b604`

The current Codex plugin is a user-created remote app identified by:

```text
asdk_app_6a58e7a411988191a74fda9cfcf6b604
```

The local cache contains only an app manifest and ID, not portable application source. Therefore this marketplace does not copy, rehost, or claim to distribute that app. Consumers must provision it separately in the Codex environment where S3 Research Memory is enabled.

## S3 Research Memory

The slide skill may use retrieved lessons or evidence as user-supplied inputs, but it must not create a parallel database or write directly to MediaWiki. Use the central MCP service and its documented write/authentication policy. Never place MCP tokens, Authorization headers, private wiki exports, or raw evidence dumps in this repository.

## Validation boundary

Private marketplace installation proves only that the skill package is discoverable and installable. It does not prove MCP authentication, wiki write permissions, or the quality of a generated deck. Those are separate runtime and user-acceptance checks.
