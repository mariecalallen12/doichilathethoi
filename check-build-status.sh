#!/bin/bash
# Script to check build status and restart container if build succeeded

echo "Checking build status..."

if [ -f /tmp/docker-build-final.log ]; then
    echo ""
    echo "Last 20 lines of build log:"
    tail -20 /tmp/docker-build-final.log
    echo ""
    
    if grep -q "Successfully built\|Successfully tagged" /tmp/docker-build-final.log; then
        echo "✅ Build completed successfully!"
        echo ""
        echo "Restarting container..."
        cd /root/forexxx
        docker compose stop client-app
        docker compose rm -f client-app
        docker compose up -d client-app
        sleep 5
        docker ps | grep client-app
        echo ""
        echo "✅ Deployment completed!"
    elif grep -q "ERROR\|error\|failed" /tmp/docker-build-final.log | tail -1; then
        echo "❌ Build failed. Check the log above for details."
    else
        echo "⏳ Build still in progress..."
        echo "Check again in a few minutes with: ./check-build-status.sh"
    fi
else
    echo "Build log not found. Build may not have started."
fi

