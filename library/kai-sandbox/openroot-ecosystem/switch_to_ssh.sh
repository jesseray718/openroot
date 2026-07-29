#!/bin/bash

echo "=== Switching repositories to SSH ==="
echo ""

# Switch all repositories to SSH
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "Switching $dir to SSH..."
        cd "$dir"
        git remote set-url origin git@github.com:jesseray718/${dir%/}.git
        if [ $? -eq 0 ]; then
            echo "✅ Successfully switched $dir to SSH"
            git remote -v
        else
            echo "❌ Failed to switch $dir"
        fi
        cd ..
        echo ""
    fi
done

echo "=== All repositories processed ==="
