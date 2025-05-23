@echo on
setlocal enabledelayedexpansion

echo === Starting invert_folder.bat ===

:: === Configuration ===
set PYTH="C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe"
set SHAPE="D:\GitHub\neg2pos\shape_image.py"
set INVERT="D:\GitHub\neg2pos\invert_image.py"
set IVIEW="C:\Program Files\IrfanView\i_view64.exe"

:: === Validate prerequisites ===
if not exist %PYTH% (
    echo [ERROR] Python interpreter not found at:
    echo   %PYTH%
    exit /b 1
)

if not exist %SHAPE% (
    echo [ERROR] shape_image.py not found at:
    echo   %SHAPE%
    exit /b 1
)

if not exist %INVERT% (
    echo [ERROR] invert_image.py not found at:
    echo   %INVERT%
    exit /b 1
)

if not exist %IVIEW% (
    echo [ERROR] IrfanView not found at:
    echo   %IVIEW%
    exit /b 1
)

:: === Validate folder argument ===
if "%~1"=="" (
    echo [ERROR] Please specify a folder path.
    echo Usage: invert_folder.bat "C:\Path\To\Folder"
    exit /b 1
)
set "FOLDER=%~1"

if not exist "%FOLDER%" (
    echo [ERROR] Folder does not exist:
    echo   %FOLDER%
    exit /b 1
)

:: === Begin Processing ===
echo Folder to process: %FOLDER%
echo 

:: Process .jpg files
for %%F in ("%FOLDER%\*.jpg") do call :process "%%F"

:: Process .png files
for %%F in ("%FOLDER%\*.png") do call :process "%%F"

:: Clean up viewer
%IVIEW% /killmesoftly

echo 
echo === Done! ===
pause
exit /b

:process
set "FILE=%~1"
echo -- Checking: %FILE%

echo %~n1 | findstr /i "_inverted" >nul
if errorlevel 1 (
    echo    Processing: %~nx1
    %PYTH% "%SHAPE%" "%FILE%" > %TEMP%\c4c.json
    %PYTH% "%INVERT%" %TEMP%\c4c.json

    set "DIR=%~dp1"
    set "NAME=%~n1"
    set "OUT=!DIR!!NAME!_inverted.png"

    echo    Opening: !OUT!
    start "" %IVIEW% "!OUT!"
    timeout /t 3 /nobreak >nul
) else (
    echo    Skipping: already inverted
)
exit /b
