# Deployment Guide

## Docker Deployment

### Build Image

```bash
docker build -t pdf-price-search .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -v $(pwd)/source:/app/source \
  pdf-price-search
```

### Docker Compose

```bash
docker-compose up -d
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn src.presentation.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Uvicorn

```bash
uvicorn src.presentation.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

## Environment Variables

```bash
export PDF_SEARCH_DIR=/path/to/pdfs
export PDF_SEARCH_CACHE_DIR=/path/to/cache
export PDF_SEARCH_LOG_LEVEL=INFO
export PDF_SEARCH_MAX_PDF_SIZE_MB=50
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Health Checks

Monitor the `/api/health` endpoint for application status.

## Scaling

- Use load balancer for horizontal scaling
- Enable distributed caching (Redis)
- Use database for persistent storage

## Security

- Enable HTTPS
- Add authentication middleware
- Implement rate limiting
- Validate file uploads
- Use security headers
