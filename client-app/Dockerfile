## Client App - Vue 3 + Vite (LuxeTrade)
## Multi-stage build: Node (build) -> Nginx (serve static)

FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install dependencies with cache mount for faster builds
RUN npm ci --legacy-peer-deps --prefer-offline --no-audit

# Copy source code
COPY . .

# Build-time environment variables
# Use relative paths for production - nginx reverse proxy will handle routing
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

ARG VITE_WS_URL=/ws
ENV VITE_WS_URL=$VITE_WS_URL

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration and remove default config
COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/conf.d/default.conf

# Add health check endpoint
RUN echo 'location /health { access_log off; return 200 "healthy\n"; add_header Content-Type text/plain; }' > /etc/nginx/conf.d/health.conf

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
