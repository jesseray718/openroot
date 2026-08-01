#!/bin/bash

cd ~/openroot-staging || { echo "Failed to change directory"; exit 1; }

for zipfile in *.zip */*.zip; do
    if [ -f "$zipfile" ]; then
        echo "Unzipping: $zipfile"
        if ! unzip -o "$zipfile"; then
            echo "Error unzipping $zipfile"
        fi
    else
        echo "Skipping $zipfile, not a regular file"
    fi
done
