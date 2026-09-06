#!/bin/bash

echo "=== OpenRoot Ecosystem Push Script ==="
echo ""

# Push all repositories
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "Pushing $dir..."
        cd "$dir"
        git push origin main
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed $dir"
        else
            echo "❌ Failed to push $dir"
        fi
        cd ..
        echo ""
    fi
done

echo "=== All repositories processed ==="
