@echo off
SET URL=https://raw.githubusercontent.com/benoitbMTL/malware-bazaar/main/malware_downloader.py
SET FILENAME=malware_downloader.py

:: Check if the file exists and delete it
IF EXIST %FILENAME% DEL /F %FILENAME%

:: Download the file
echo Downloading %URL%...
curl -Os %URL%

:: Print "Done!" when the download is complete
echo Done!
