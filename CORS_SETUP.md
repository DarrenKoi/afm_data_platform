# CORS Configuration Guide

## Overview

The AFM Data Platform Backend uses Flask-CORS to handle Cross-Origin Resource Sharing (CORS) for frontend-backend communication during development and production.

## Default Configuration

By default, the following origins are allowed for local development:

- `http://localhost:3000` - Default Vue.js dev server
- `http://localhost:3001` - Alternative port
- `http://localhost:3002` - Alternative port
- `http://localhost:5173` - Vite default port
- `http://localhost:8080` - Common alternative port
- `http://127.0.0.1:3000` - IP-based access
- `http://127.0.0.1:3001` - IP-based access
- `http://127.0.0.1:3002` - IP-based access
- `http://127.0.0.1:5173` - IP-based access
- `http://127.0.0.1:8080` - IP-based access

## Adding Custom Origins

### Using Environment Variable

Set the `CORS_ORIGINS` environment variable with comma-separated origins:

```bash
# Windows Command Prompt
set CORS_ORIGINS=http://localhost:4000,http://localhost:4200,http://192.168.1.100:3000
python index.py

# Windows PowerShell
$env:CORS_ORIGINS="http://localhost:4000,http://localhost:4200,http://192.168.1.100:3000"
python index.py

# Linux/Mac/WSL
export CORS_ORIGINS="http://localhost:4000,http://localhost:4200,http://192.168.1.100:3000"
python index.py
```

### Modifying index.py

Add your custom origins to the `default_origins` list in `index.py`:

```python
default_origins = [
    # ... existing origins ...
    'http://localhost:4000',  # Your custom port
    'http://192.168.1.100:3000',  # Local network access
]
```

## CORS Headers

The backend allows the following headers in CORS requests:

- `Content-Type`
- `Authorization`
- `X-Requested-With`
- `Accept`

## Allowed Methods

All standard HTTP methods are allowed:

- `GET`
- `POST`
- `PUT`
- `DELETE`
- `OPTIONS`
- `PATCH`

## Credentials

The backend supports credentials (cookies, authorization headers) in CORS requests with `supports_credentials=True`.

## Debugging CORS Issues

1. **Check the console output** when starting the backend. It displays all allowed origins:

```
=== CORS Configuration ===
Allowed origins: ['http://localhost:3000', 'http://localhost:3001', ...]
Allowed methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
Allowed headers: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
Supports credentials: True
========================
```

2. **Browser Developer Tools**: Check the Network tab for CORS-related errors. Look for:
   - `Access-Control-Allow-Origin` header in responses
   - Preflight `OPTIONS` requests
   - Error messages about blocked requests

3. **Common Issues**:
   - **Missing port**: Make sure to include the port number in the origin (e.g., `http://localhost:3001`, not just `http://localhost`)
   - **Protocol mismatch**: Use `http://` for local development, not `https://`
   - **Trailing slash**: Don't include trailing slashes in origins

## Production Configuration

For production, you should:

1. Set `FLASK_ENV=production`
2. Specify only the actual frontend domains in `CORS_ORIGINS`
3. Consider using a reverse proxy (nginx) to handle CORS instead

Example production setup:

```bash
export FLASK_ENV=production
export CORS_ORIGINS="https://your-frontend-domain.com,https://www.your-frontend-domain.com"
```

## Allow All Origins (Development Only)

⚠️ **WARNING**: Only use this in development, never in production!

To allow all origins during development, uncomment this line in `config.py`:

```python
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Uncomment to allow all origins in development
    ALL_CORS_ORIGINS = ['*']
```

## Testing CORS

You can test CORS configuration using curl:

```bash
# Test preflight request
curl -X OPTIONS http://localhost:5000/api/health \
  -H "Origin: http://localhost:3001" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Test actual request
curl http://localhost:5000/api/health \
  -H "Origin: http://localhost:3001" \
  -v
```

Look for these headers in the response:
- `Access-Control-Allow-Origin: http://localhost:3001`
- `Access-Control-Allow-Credentials: true`