@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Сразу запускаем скрипт через питон из venv, который лежит в req
"%~dp0req\.venv\Scripts\python.exe" "%~dp0req\simplespec.py"

:: Если сервер упадет с ошибкой, окно не закроется сразу, чтобы ты прочитал текст
if errorlevel 1 pause