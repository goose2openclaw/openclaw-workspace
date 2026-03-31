#!/bin/bash
# Failover Script - Auto-restart on failure
MAX_RETRIES=3
RETRY_DELAY=10

cd /root/.openclaw/workspace/GO2SE_PLATFORM

for i in $(seq 1 $MAX_RETRIES); do
    echo "[Failover Attempt $i/$MAX_RETRIES]"
    
    # Kill existing
    pkill -f uvicorn || true
    sleep 2
    
    # Restart
    ./scripts/start_server.sh
    
    # Wait and check
    sleep 5
    if curl -sf http://localhost:8000/api/stats >/dev/null 2>&1; then
        echo "✅ Service restored"
        exit 0
    fi
    
    if [ $i -lt $MAX_RETRIES ]; then
        echo "❌ Attempt failed, retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    fi
done

echo "🚨 All failover attempts failed!"
exit 1
