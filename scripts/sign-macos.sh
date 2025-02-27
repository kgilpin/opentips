#!/bin/bash
set -e

if [ -z "$BUILD_CERTIFICATE_BASE64" ] || [ -z "$P12_PASSWORD" ] || [ -z "$KEYCHAIN_PASSWORD" ] || [ -z "$SIGNING_IDENTITY" ]; then
    echo "Missing required environment variables"
    exit 1
fi

# Create keychain
security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
security default-keychain -s build.keychain
security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain

# Import certificate
echo "$BUILD_CERTIFICATE_BASE64" | base64 --decode > certificate.p12
security import certificate.p12 -k build.keychain -P "$P12_PASSWORD" -T /usr/bin/codesign
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" build.keychain

# Sign the app
codesign --force -s "$SIGNING_IDENTITY" -v build/exe.*/*

# Cleanup
security delete-keychain build.keychain
rm certificate.p12
