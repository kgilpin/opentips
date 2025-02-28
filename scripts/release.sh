#!/bin/bash
set -e

if [ -z "$GITHUB_TOKEN" ] || [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo "Missing required environment variables"
    exit 1
fi

# Install python-semantic-release if not already installed
echo "Setting up python-semantic-release..."
pip install python-semantic-release

# Run semantic-release version and publish
echo "Running semantic-release..."
python -m semantic_release version
python -m semantic_release publish

# Build and publish to PyPI
echo "Building Python package..."
python -m build

echo "Publishing to PyPI..."
twine upload --verbose dist/*

echo "Release process completed successfully."
    