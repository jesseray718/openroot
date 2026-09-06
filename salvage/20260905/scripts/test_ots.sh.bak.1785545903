#!/bin/bash
set -e
# Test script for hello world function
counter=0
start_time=$(date +%s)
hello_world() {
  # This script prints a greeting message
  ((counter++))
  uptime=$(( $(date +%s) - start_time ))
  echo "hello world $counter, uptime: $uptime seconds"
}

hello_world
