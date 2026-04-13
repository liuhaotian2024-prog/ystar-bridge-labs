#!/bin/bash
# Shell script syntax validator
# Run this before committing shell scripts

EXIT_CODE=0

echo "Validating shell scripts..."

for script in scripts/*.sh; do
  if [ -f "$script" ]; then
    if ! bash -n "$script" 2>&1; then
      echo "✗ SYNTAX ERROR: $script"
      EXIT_CODE=1
    else
      echo "✓ $script"
    fi
  fi
done

if [ $EXIT_CODE -eq 0 ]; then
  echo "All shell scripts valid ✓"
else
  echo "Shell script validation FAILED ✗"
fi

exit $EXIT_CODE
