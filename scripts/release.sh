#!/bin/bash
set -e

if [ -z "$GITHUB_TOKEN" ] || [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo "Missing required environment variables"
    exit 1
fi

# Setup Node and install semantic-release
echo "Setting up semantic-release..."
npm install -g semantic-release @semantic-release/git @semantic-release/changelog

# Run semantic-release
echo "Running semantic-release..."
semantic-release

# Build and publish to PyPI
echo "Building Python package..."
python -m build

echo "Publishing to PyPI..."
twine upload dist/*
