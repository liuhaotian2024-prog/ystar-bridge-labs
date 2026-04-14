#!/usr/bin/env bash
# Exp 3: Adversarial rule bypass dry_run (safety validation test)

set -e

echo "=== Exp 3: Adversarial rule bypass dry_run ==="

# Write malicious rule WITHOUT dry_run_until
cat > /tmp/malicious_rule.yaml <<'EOF'
rules:
  - id: adversarial_block_all
    enabled: true
    trigger:
      tool: "*"
    action: deny
    reason: "malicious bypass attempt"
EOF

echo "Created malicious rule without dry_run_until"

# Run governance_boot.sh with malicious rule — STEP 8.6 should FAIL
echo "Testing governance_boot.sh with malicious rule..."
YSTAR_FORGET_GUARD_RULES=/tmp/malicious_rule.yaml bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh ceo > /tmp/boot_adversarial.log 2>&1 || true

# Check for dry_run_until detection failure
if grep -A 2 "8.6\|dry_run\|FAIL" /tmp/boot_adversarial.log | grep -q "FAIL\|missing dry_run_until\|FAILURES"; then
  echo "PASS: governance_boot detected missing dry_run_until and failed boot"
else
  echo "FAIL: governance_boot did NOT detect malicious rule bypass"
  echo "Boot log:"
  cat /tmp/boot_adversarial.log
  exit 1
fi
