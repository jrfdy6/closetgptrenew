#!/bin/bash
# Stress test script for ClosetGPT backend on Railway
# Runs for 5 minutes (adjust as needed)

DOMAIN="https://closetgptrenew-backend-production.up.railway.app"
DURATION=300  # seconds (5 minutes)
INTERVAL=5    # seconds between requests
START=$(date +%s)

echo "🚀 Starting stress test against $DOMAIN for $DURATION seconds..."
echo "Logging results to stress_test.log"
echo "---------------------------------------"
echo "" > stress_test.log

while [ $(( $(date +%s) - START )) -lt $DURATION ]; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Testing endpoints..." | tee -a stress_test.log

    for ENDPOINT in "/health" "/api/outfits/debug-user" "/api/outfits/generate"; do
        echo -n "[$TIMESTAMP] $ENDPOINT -> " | tee -a stress_test.log
        curl -s -o /dev/null -w "%{http_code}\n" "$DOMAIN$ENDPOINT" | tee -a stress_test.log
    done

    sleep $INTERVAL
done

echo "✅ Stress test complete. Review stress_test.log for results."
