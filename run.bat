@echo off
REM CRYPT8BIT — запуск
REM Файл: F:\User\project\GitHub\CRYPT8BIT\run.bat

chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   CRYPT8BIT — запуск
echo ============================================
echo.

py -3.12 main.py

echo.
echo ============================================
echo   Процесс завершился. Код выхода: %errorlevel%
echo ============================================
echo.
pause