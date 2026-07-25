#!/bin/bash

echo "=== OpenRoot Ecosystem Push Script ==="
echo ""

# Push all repositories with detailed feedback
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "=== Pushing $dir ==="
        cd "$dir"
        
        # Get current branch
        branch=$(git branch --show-current 2>/dev/null || echo "main")
        echo "Branch: $branch"
        
        # Try to push
        if git push origin $branch; then
            echo "✅ Successfully pushed $dir"
        else
            echo "❌ Failed to push $dir"
            echo "Remote URL: $(git remote get-url origin)"
            echo ""
        fi
        
        cd ..
        echo ""
    fi
done

echo "=== All repositories processed ==="
