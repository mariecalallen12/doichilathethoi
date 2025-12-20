# Multi-stage build for Java Spring Boot multi-module Maven project
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

# Copy all source code (multi-module project needs all modules)
COPY . .

# Download dependencies and build all modules
RUN mvn clean package -DskipTests -B

# Create a directory and copy all executable JARs
RUN mkdir -p /jars && \
    find . -type f -name "*-app-*.jar" ! -name "*-sources.jar" ! -name "*-javadoc.jar" -exec cp {} /jars/ \;

# Runtime stage
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy the api-app JAR as the main application
# If it doesn't exist, copy the first JAR found
COPY --from=builder /jars/*-app-*.jar ./

# Create startup script to run the correct JAR
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'JAR_FILE=$(ls /app/*.jar | head -1)' >> /app/start.sh && \
    echo 'exec java -jar -Dserver.port=${SERVER_PORT:-3001} "$JAR_FILE"' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Run the application
CMD ["/app/start.sh"]
