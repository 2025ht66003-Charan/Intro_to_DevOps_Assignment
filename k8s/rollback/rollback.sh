#!/bin/bash
# Universal rollback script for ACEest Fitness & Gym deployments
# Usage: ./rollback.sh <strategy> [namespace] [revision]
#   strategy: rolling | blue-green | canary | all
#   namespace: default aceest-gym
#   revision:  (rolling only) specific revision number, default = previous

set -e

STRATEGY=${1:-rolling}
NAMESPACE=${2:-aceest-gym}
REVISION=${3:-}

echo "=== ACEest Deployment Rollback ==="
echo "Strategy  : $STRATEGY"
echo "Namespace : $NAMESPACE"
echo ""

rollback_rolling() {
    echo "[Rolling Update] Initiating rollback..."
    if [ -n "$REVISION" ]; then
        kubectl rollout undo deployment/aceest-rolling -n "$NAMESPACE" --to-revision="$REVISION"
    else
        kubectl rollout undo deployment/aceest-rolling -n "$NAMESPACE"
    fi
    kubectl rollout status deployment/aceest-rolling -n "$NAMESPACE" --timeout=120s
    echo "[Rolling Update] Rollback complete."
}

rollback_blue_green() {
    echo "[Blue-Green] Switching service selector back to BLUE slot..."
    kubectl patch service aceest-service \
        -n "$NAMESPACE" \
        -p '{"spec":{"selector":{"slot":"blue"}}}'
    CURRENT=$(kubectl get service aceest-service -n "$NAMESPACE" \
        -o jsonpath='{.spec.selector.slot}')
    echo "[Blue-Green] Active slot: $CURRENT"
    echo "[Blue-Green] Rollback complete."
}

rollback_canary() {
    echo "[Canary] Removing canary deployment..."
    kubectl delete deployment aceest-canary -n "$NAMESPACE" --ignore-not-found=true
    echo "[Canary] Canary removed. All traffic routes to stable."
}

case "$STRATEGY" in
    rolling)    rollback_rolling ;;
    blue-green) rollback_blue_green ;;
    canary)     rollback_canary ;;
    all)
        rollback_rolling
        rollback_blue_green
        rollback_canary
        ;;
    *)
        echo "Unknown strategy: $STRATEGY"
        echo "Valid options: rolling | blue-green | canary | all"
        exit 1
        ;;
esac

echo ""
echo "=== Rollback finished successfully ==="
