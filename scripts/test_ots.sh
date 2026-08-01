#!/bin/bash
set -e
# Test script for hello world function
# Note: This script's energy efficiency is limited by the Landauer limit, which is the minimum energy required to erase one bit of information (approximately 2.9 * 10^-21 J at room temperature)
counter=0
start_time=$(date +%s)
get_system_uptime() {
  # This function returns system uptime in seconds
  uptime=$(cat /proc/uptime | cut -d ' ' -f 1)
  echo "$uptime"
}

hello_world() {
  # This script prints a greeting message
  ((counter++))
  echo "hello world $counter, system uptime: $(get_system_uptime) seconds, script uptime: $(( $(date +%s) - start_time )) seconds"
}

while true
do
  hello_world
  sleep 1
done
