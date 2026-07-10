#!/bin/bash

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "Commit message missing"
    exit 1
fi

echo "Checking changes..."

if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

git add .

git commit -m "$MESSAGE"

git push origin $(git branch --show-current)

echo "Save completed successfully"
