#!/usr/bin/env bash
set -euo pipefail

CONTAINER_COMMAND="uname -a"
CLEAN_FLAG="--clean"
OS_LIST=("ubuntu:latest" "debian:bookworm-slim" "alpine:latest")

if command -v uv >/dev/null 2>&1; then
  for os in "${OS_LIST[@]}"; do
    printf "\nRunning integration test with OS '%s'...\n" "$os"
    output=$(uv run contest "$os" --command "$CONTAINER_COMMAND" $CLEAN_FLAG)
    if [ -n "$output" ]; then
      printf '\e[36m%s\e[0m\n' "$output"
    else
      printf '\e[31mTest failed for %s: no output received\e[0m\n' "$os" >&2
      exit 1
    fi
  done
  printf '\n\e[32mIntegration tests completed successfully.\e[0m\n'
else
  echo "Error: 'uv' command not found. Please install the package or adjust PATH." >&2
  exit 1
fi
