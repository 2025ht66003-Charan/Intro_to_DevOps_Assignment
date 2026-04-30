#!/bin/bash
# Blue-Green rollback: instantly revert traffic from green → blue
# Usage: ./rollback.sh [namespace]

NAMESPACE=${1:-aceest-gym}

echo "Rolling back Blue-Green: switching traffic to BLUE slot..."
kubectl patch service aceest-service \
    -n "$NAMESPACE" \
    -p '{"spec":{"selector":{"slot":"blue"}}}'

echo "Verifying service selector..."
kubectl get service aceest-service -n "$NAMESPACE" -o jsonpath='{.spec.selector}'

echo ""
echo "Rollback complete. Traffic now routes to BLUE (stable) deployment."
echo "To clean up the failed green deployment:"
echo "  kubectl delete deployment aceest-green -n $NAMESPACE"
