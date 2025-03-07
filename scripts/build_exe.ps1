
Write-Host "Building OpenTips executable using cx_Freeze CLI..."

# Install cx_Freeze if not already installed
python -m pip install -U cx_Freeze

# Run cx_Freeze build using CLI options
python -m cx_Freeze opentips/cli/main.py `
  --include-msvcr `
  --target-name=opentips `
  --no-compress

Write-Host "Build completed. Check the 'dist' directory for the executable."
