@echo off
chcp 65001 >nul
title Сборка CRYPT8BIT

echo ========================================
echo Сборка CRYPT8BIT
echo ========================================

:: Чистим временные папки
if exist "build" rmdir /s /q "build"
if exist "build_out" rmdir /s /q "build_out"

echo 1. Сборка основного лаунчера...
pyinstaller --noconfirm --noconsole --onedir --name="CRYPT8BIT" --icon="assets\launcher_icon.ico" --add-data "assets;assets" --add-data "core;core" --add-data "ui;ui" --add-data "tools;tools" --add-data "links.json;." --distpath "build_out" main.py

echo.
echo 2. Сборка конструктора игр...
:: Используем относительный путь к иконке
pyinstaller --clean --noconfirm --noconsole --onedir --name="GameCreator" --icon="assets\game_creator_icon.ico" --distpath "build_out" tools\game_creator.py

echo.
echo 3. Копирование в dist...
if not exist "dist\CRYPT8BIT" mkdir "dist\CRYPT8BIT"
if not exist "dist\CRYPT8BIT\tools" mkdir "dist\CRYPT8BIT\tools"

:: Копируем лаунчер
xcopy "build_out\CRYPT8BIT\CRYPT8BIT.exe" "dist\CRYPT8BIT\" /Y /I
if exist "build_out\CRYPT8BIT\_internal" (
    if exist "dist\CRYPT8BIT\_internal" rmdir /s /q "dist\CRYPT8BIT\_internal"
    xcopy "build_out\CRYPT8BIT\_internal" "dist\CRYPT8BIT\_internal\" /E /Y /I
)

:: Копируем конструктор
xcopy "build_out\GameCreator\GameCreator.exe" "dist\CRYPT8BIT\tools\" /Y /I
if exist "build_out\GameCreator\_internal" (
    if exist "dist\CRYPT8BIT\tools\_internal" rmdir /s /q "dist\CRYPT8BIT\tools\_internal"
    xcopy "build_out\GameCreator\_internal" "dist\CRYPT8BIT\tools\_internal\" /E /Y /I
)

echo.
echo 4. Очистка временных файлов...
rmdir /s /q "build_out"
if exist "build" rmdir /s /q "build"

echo.
echo ========================================
echo Сборка завершена!
echo Проверь: dist\CRYPT8BIT\CRYPT8BIT.exe
echo Конструктор: dist\CRYPT8BIT\tools\GameCreator.exe
echo ========================================
pause