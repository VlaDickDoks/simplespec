@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Обновление simplespec из GitHub ===
echo Репозиторий: https://github.com/VlaDickDoks/simplespec
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Git не найден в PATH.
    echo Установи Git for Windows: https://git-scm.com/download/win
    pause
    exit /b 1
)

if not exist ".git" (
    echo [ИНФО] Локальный .git не найден. Клонирую репозиторий во временную папку...
    if exist "_update_tmp" rmdir /s /q "_update_tmp"
    git clone https://github.com/VlaDickDoks/simplespec.git _update_tmp
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось клонировать репозиторий.
        pause
        exit /b 1
    )
    echo [ИНФО] Копирую файлы (кроме .venv)...
    xcopy /E /I /Y /EXCLUDE:.venv "_update_tmp\*" "."
    rmdir /s /q "_update_tmp"
) else (
    echo [ИНФО] Найден .git, делаю git pull...
    git pull origin main
    if errorlevel 1 (
        echo [ОШИБКА] git pull завершился с ошибкой. Возможно, есть локальные изменения.
        echo Сделай git stash или закоммить изменения, затем повтори.
        pause
        exit /b 1
    )
)

echo.
echo === Готово! ===
echo Если обновились зависимости — запусти req\install_deps.bat.
echo Затем запускай runsimplespec.bat.
pause