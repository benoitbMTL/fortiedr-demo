@echo off
SET URL=https://raw.githubusercontent.com/benoitbMTL/fortiedr-demo/refs/heads/main/fortiedr-mitre.py
SET FILENAME=fortiedr-mitre.py

:: Check if the file exists and delete it
IF EXIST %FILENAME% DEL /F %FILENAME%

:: Download the file
echo Downloading %URL%...
curl -Os %URL%

:: Print "Done!" when the download is complete
echo Done!
