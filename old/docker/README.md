# Docker Configuration

This directory contains containerization configurations for BK25.

## Files

- `docker-compose.yml` - Multi-container Docker application definition
- `Dockerfile` - Container image build instructions

## Usage

### Development with Docker Compose
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build the image
docker build -t bk25 .

# Run the container
docker run -p 3000:3000 bk25
```

## Configuration

The Docker setup is configured for:
- Node.js 18+ runtime
- Port 3000 exposure
- Development and production environments
- Volume mounting for development
