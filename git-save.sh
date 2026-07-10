#!/bin/bash

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "Please provide commit message"
    exit 1
fi

echo "Checking status..."
git status

echo "Adding changes..."
git add .

echo "Committing..."
git commit -m "$MESSAGE"

echo "Pushing..."
git push origin $(git branch --show-current)

echo "Done!"
