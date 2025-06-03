@echo on
setlocal enabledelayedexpansion

echo === Starting invert_folder.bat ===

:: === Configuration ===
set PYTH="C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe"
set SHAPE="D:\GitHub\neg2pos\shape_image.py"
set INVERT="D:\GitHub\neg2pos\invert_image.py"
set IVIEW="C:\Program Files\IrfanView\i_view64.exe"

TIMEOUT /T 8

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

:: Extract path parts
set "DIR=%~dp1"
set "NAME=%~n1"
set "OUT=!DIR!!NAME!_inverted.png"
set "PROM=!DIR!!NAME!_.png"


:: Skip if already has _inverted in name
echo %~n1 | findstr /i "_inverted" >nul
if not errorlevel 1 (
    echo    Skipping: filename already contains "_inverted"
    exit /b
)

:: Skip if output file already exists
if exist "!OUT!" (
    echo    Skipping: !OUT! already exists
    exit /b
)

start "" %IVIEW% "%FILE%" /one

:: Proceed with processing
echo    Processing: %~nx1
%PYTH% %SHAPE% "%FILE%" > %TEMP%\\c4c.json
type %TEMP%\\c4c.json

start "" %IVIEW% "!PROM!" /one

%PYTH% %INVERT% %TEMP%\\c4c.json

::%IVIEW% /killmesoftly

echo    Opening: !OUT!
start "" %IVIEW% "!OUT!" /one
timeout /t 4 /nobreak >nul
exit /b

