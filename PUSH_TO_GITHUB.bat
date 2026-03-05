@echo off
REM Net 仔 Podcast System - Push to GitHub Script
REM 推送到 GitHub 私有倉庫

echo ========================================
echo   Net 仔 Podcast System
echo   GitHub Upload Script
echo ========================================
echo.

REM Check if remote is configured
git remote -v | findstr origin >nul
if %errorlevel% neq 0 (
    echo [!] Remote repository not configured yet.
    echo.
    echo Please follow these steps:
    echo.
    echo 1. Create a private repository on GitHub:
    echo    https://github.com/new
    echo    Repository name: netzai-podcast-system
    echo.
    echo 2. Copy your repository URL, then run:
    echo    git remote add origin https://github.com/YOUR_USERNAME/netzai-podcast-system.git
    echo.
    echo Then run this script again.
    echo.
    pause
    exit /b
)

echo [+] Remote repository is configured.
echo.

REM Rename branch to main
echo [*] Renaming branch to 'main'...
git branch -M main

echo [*] Pushing to GitHub...
echo.
echo This may take a few minutes depending on your internet connection.
echo The first push will upload approximately 5-10 MB of code.
echo.

REM Push to GitHub
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! 
    echo ========================================
    echo.
    echo Your code has been pushed to GitHub.
    echo.
    echo Next steps:
    echo 1. Visit your repository on GitHub
    echo 2. Review the files and README
    echo 3. Invite collaborators if needed
    echo 4. Set up CI/CD (optional)
    echo.
    echo Repository URL:
    echo https://github.com/YOUR_USERNAME/netzai-podcast-system
    echo.
) else (
    echo.
    echo ========================================
    echo   PUSH FAILED
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. Authentication failed - Use Personal Access Token instead of password
    echo 2. Repository doesn't exist - Create it on GitHub first
    echo 3. Network error - Check your internet connection
    echo.
    echo For authentication, create a token at:
    echo https://github.com/settings/tokens
    echo.
)

pause
