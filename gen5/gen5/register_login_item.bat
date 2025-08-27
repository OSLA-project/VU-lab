@echo off
setlocal

:: Define variables
set "BAT_FILE=gen5_service.bat"
set "SHORTCUT_NAME=gen5_service.lnk"
set "CURRENT_DIR=%~dp0"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Check if the batch file exists
if not exist "%CURRENT_DIR%%BAT_FILE%" (
    echo Error: %BAT_FILE% does not exist.
    exit /b 1
)

:: Create the shortcut
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%CURRENT_DIR%%SHORTCUT_NAME%" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%CURRENT_DIR%%BAT_FILE%" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%VBS_SCRIPT%"
echo oLink.WindowStyle = 7 >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

:: Move the shortcut to the Startup folder
if not exist "%STARTUP_FOLDER%" (
    mkdir "%STARTUP_FOLDER%"
)

move "%CURRENT_DIR%%SHORTCUT_NAME%" "%STARTUP_FOLDER%"

echo Shortcut for %BAT_FILE% created and moved to startup folder.

:: Display message and wait
echo Registration complete
timeout /t 10

endlocal
exit /b 0
