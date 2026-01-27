---
name: api-docs
description: Generate external API documentation in HTML format for Squint APIs. Use when asked to document an API endpoint, create API docs for external consumers, or generate HTML documentation for endpoints. Output is Google Docs compatible.
---

# API Documentation Generator

Generate HTML API docs for Squint endpoints.

## Investigation Process

Before writing docs, gather information from the codebase:

1. **Find the router** - Search `api/src/infrastructure/routes/` for the relevant router file
2. **Identify the handler** - Find the handler function (e.g., `GetProceduresHandler`)
3. **Read the service** - Located in `api/src/infrastructure/services/` - understand request validation, query params, and response assembly
4. **Find response types** - Check imports from `@squintinc/datamodels-ts-cloud/v1` or look for Zod schemas
5. **Check repository** - In `api/src/infrastructure/repositories/` for SQL queries showing exact response shape
6. **Identify sub-objects** - Note nested objects that need separate field tables

## Documentation Structure

Each endpoint doc includes:

1. **Title**: `{HTTP_METHOD} {Endpoint Name} Endpoint`
2. **Endpoint path**: Full path pattern
3. **Description**: 1-2 sentences explaining what the endpoint does
4. **Authentication**: Bearer token requirement and required permission
5. **Request**: Headers table, Path/Query Parameters tables, Request Body (if applicable)
6. **Response**: Example JSON, Response Fields table, Sub-object tables
7. **Error Responses table**

## Field Type Conventions

| Code Type | Doc Type |
|-----------|----------|
| `string` (UUID format) | UUID |
| `string` | string |
| `number`, `int` | integer |
| `number` (decimal) | float |
| `boolean` | boolean |
| `Date`, `DateSchema` | ISO 8601 |
| `string[]` | string[] |
| `SomeType[]` | array |
| Nested object | object (reference sub-object table) |

## Authentication Patterns

### Integrations API (`/v1/integrations/...`)

For API key authentication, document as:
- "Requires a valid API key with `{permission}` permission"
- Format: `Authorization: Bearer <prefix>:<secret>`

### Authenticated API (`/v1/workspaces/...`)

For Firebase JWT authentication, document as:
- "Requires a valid workspace scoped Bearer token with {permission} permission"
- Format: `Authorization: Bearer <token>`

## JSON Example Guidelines

- Use realistic fake UUIDs (e.g., `f1e2d3c4-b5a6-7890-cdef-1234567890ab`)
- Use ISO 8601 timestamps (e.g., `2025-01-06T10:00:00.000Z`)
- Show `null` for nullable fields commonly null
- Include 1-2 items for arrays
- Show complete structure for nested objects

## Output Location

Write HTML files to `docs/api-docs/api/v1/`:

```
docs/api-docs/api/v1/
├── integrations/workspaces/   # /v1/integrations/workspaces/{workspaceId}/...
└── workspaces/                # /v1/workspaces/{workspaceId}/...
```

**Naming**: `{resource}.html` or `{resource}-{action}.html` (e.g., `tasks-create.html`)

## HTML Templates

See [references/html-templates.md](references/html-templates.md) for:
- Base HTML document structure
- Table formats (Headers, Parameters, Response Fields, Errors)
- Sub-object documentation patterns
- Authentication section formats

## Viewing Documentation

To preview HTML docs locally in VS Code/Cursor:
1. Install the [Live Preview](https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server) extension
2. Open any `.html` file
3. Click "Show Preview" or right-click → "Live Preview: Show Preview"
