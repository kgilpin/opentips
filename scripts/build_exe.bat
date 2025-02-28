@echo off

echo Building OpenTips executable using cx_Freeze CLI...

REM Install cx_Freeze if not already installed
pip install -U cx_Freeze

REM Run cx_Freeze build using CLI options
cxfreeze opentips/cli/main.py ^
  --target-name=opentips ^
  --no-compress

echo Build completed. Check the "dist" directory for the executable.
