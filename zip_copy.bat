@echo off
setlocal

rem Source folder (relative to this .bat file)
set "SRC=%~dp0zip_build\rvt-qgis"

rem Target folders
set "DST1=C:\Users\ncoz\AppData\Roaming\QGIS\QGIS4\profiles\plugin-test\python\plugins\rvt-qgis"
set "DST2=C:\Users\ncoz\AppData\Roaming\QGIS\QGIS3\profiles\plugin-test\python\plugins\rvt-qgis"

rem Check source exists
if not exist "%SRC%\" (
    echo Source folder not found:
    echo %SRC%
    exit /b 1
)

echo Copying to QGIS4 plugin folder...
robocopy "%SRC%" "%DST1%" /MIR /R:1 /W:1 >nul

echo Copying to QGIS3 plugin folder...
robocopy "%SRC%" "%DST2%" /MIR /R:1 /W:1 >nul

rem Robocopy returns codes below 8 for success/acceptable differences
if %ERRORLEVEL% GEQ 8 (
    echo Copy failed.
    exit /b %ERRORLEVEL%
)

echo Done.
exit /b 0