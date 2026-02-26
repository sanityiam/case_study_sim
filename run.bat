@echo off
setlocal

REM move to the project root
cd /d "%~dp0"

REM Try py launcher first, then python
where py >nul 2>nul
if %errorlevel%==0 (
    echo Using: py
    echo Forwarding args to runners/bootstrap_and_run.py: %*
    py runners\bootstrap_and_run.py %*
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    echo Using: python
    echo Forwarding args to runners/bootstrap_and_run.py: %*
    python runners\bootstrap_and_run.py %*
    goto :end
)

echo Error: Python is not installed or not in PATH.
echo Please install Python 3 and try again.
exit /b 1

:end
if %errorlevel% neq 0 (
    echo.
    echo Script failed with exit code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo.
echo Done.
pause