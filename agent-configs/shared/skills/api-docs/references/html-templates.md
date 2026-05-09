# HTML Templates for API Documentation

## Table of Contents

- [Base HTML Structure](#base-html-structure)
- [Table Formats](#table-formats)
  - [Headers Table](#headers-table)
  - [Path/Query Parameters Table](#pathquery-parameters-table)
  - [Response Fields Table](#response-fields-table)
  - [Error Responses Tables](#error-responses-tables)
- [Sub-Object Documentation](#sub-object-documentation)
- [Authentication Sections](#authentication-sections)

---

## Base HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
    h1 { color: #1a1a1a; border-bottom: 2px solid #333; padding-bottom: 10px; }
    h2 { color: #333; margin-top: 30px; }
    h3 { color: #555; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; }
    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th { background-color: #f5f5f5; font-weight: bold; }
    code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
    pre { background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
    .endpoint { font-family: monospace; font-size: 14px; background: #e8e8e8; padding: 10px; border-radius: 4px; }
  </style>
</head>
<body>
<!-- Content here -->
</body>
</html>
```

---

## Table Formats

### Headers Table

```html
<table>
  <tr><th>Header</th><th>Required</th><th>Description</th></tr>
  <tr><td>Authorization</td><td>Yes</td><td>Bearer token for authentication</td></tr>
</table>
```

### Path/Query Parameters Table

```html
<table>
  <tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>
  <tr><td>workspaceId</td><td>UUID</td><td>Yes</td><td>The workspace identifier</td></tr>
</table>
```

### Response Fields Table

```html
<table>
  <tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td>UUID</td><td>Unique identifier</td></tr>
</table>
```

### Error Responses Tables

#### For Integrations API (API key auth)

```html
<table>
  <tr><th>Status</th><th>Error</th><th>Description</th></tr>
  <tr><td>400</td><td>Bad Request</td><td>Invalid request format</td></tr>
  <tr><td>401</td><td>Unauthorized</td><td>Missing/invalid API key</td></tr>
  <tr><td>403</td><td>Forbidden</td><td>API key deleted or lacks required permissions</td></tr>
  <tr><td>404</td><td>Not Found</td><td>Resource not found</td></tr>
  <tr><td>500</td><td>Internal Server Error</td><td>Unexpected server error</td></tr>
</table>
```

#### For Authenticated API (Bearer token)

```html
<table>
  <tr><th>Status</th><th>Error</th><th>Description</th></tr>
  <tr><td>400</td><td>Bad Request</td><td>Invalid request format</td></tr>
  <tr><td>401</td><td>Unauthorized</td><td>Missing/invalid authentication</td></tr>
  <tr><td>403</td><td>Forbidden</td><td>User not a workspace member or lacks permissions</td></tr>
  <tr><td>404</td><td>Not Found</td><td>Resource not found</td></tr>
  <tr><td>500</td><td>Internal Server Error</td><td>Unexpected server error</td></tr>
</table>
```

---

## Sub-Object Documentation

When a response contains nested objects:

### 1. Reference in Main Table

Set Type to `object` and Description to reference the sub-object table:

```html
<tr><td>procedureImage</td><td>object</td><td>Thumbnail image (see Squint Object Reference)</td></tr>
```

### 2. Create Separate Section

```html
<h3>Squint Object Reference Fields</h3>
<table>
  <tr><th>Field</th><th>Type</th><th>Description</th></tr>
  <tr><td>id</td><td>UUID</td><td>Unique identifier for the media object</td></tr>
  <tr><td>type</td><td>string</td><td>Media type: <code>image</code> or <code>video</code></td></tr>
</table>
```

---

## Authentication Sections

### Integrations API (API Key)

With specific permission:

```html
<h2>Authentication</h2>
<p>Requires a valid API key with <code>{permission}</code> permission. API keys use Bearer token format with the key in <code>prefix:secret</code> format.</p>
<pre>Authorization: Bearer &lt;prefix&gt;:&lt;secret&gt;</pre>
```

Without specific permission (workspace access only):

```html
<h2>Authentication</h2>
<p>Requires a valid API key with workspace access. API keys use Bearer token format with the key in <code>prefix:secret</code> format.</p>
<pre>Authorization: Bearer &lt;prefix&gt;:&lt;secret&gt;</pre>
```

### Authenticated API (Firebase JWT)

With specific permission:

```html
<h2>Authentication</h2>
<p>Requires a valid workspace scoped Bearer token with {permission} permission.</p>
<pre>Authorization: Bearer &lt;token&gt;</pre>
```

Without specific permission:

```html
<h2>Authentication</h2>
<p>Requires a valid workspace scoped Bearer token.</p>
<pre>Authorization: Bearer &lt;token&gt;</pre>
```
