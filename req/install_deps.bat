@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Проверка Python ===
where python >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в PATH. 
    echo Установи Python с официального сайта и ОБЯЗАТЕЛЬНО поставь галочку "Add python.exe to PATH".
    pause
    exit /b 1
)

echo === Проверка версии Python ===
python --version
if errorlevel 1 (
    echo [ОШИБКА] Команда python есть, но она не работает. Возможно, это заглушка из Microsoft Store.
    echo Отключи псевдонимы выполнения приложений для python.exe в настройках Windows.
    pause
    exit /b 1
)

echo === Создание виртуального окружения .venv ===
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать venv.
        echo Попроси проверить, установлен ли модуль venv (в некоторых сборках Linux/Windows его нет по умолчанию).
        pause
        exit /b 1
    )
) else (
    echo .venv уже существует, пропускаю создание.
)

echo === Активация .venv ===
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать venv.
    pause
    exit /b 1
)

echo === Обновление pip ===
python -m pip install --upgrade pip

echo === Установка зависимостей ===
python -m pip install flask mss pillow

if errorlevel 1 (
    echo [ОШИБКА] Установка зависимостей провалилась.
    echo Возможно, нет доступа к интернету или заблокирован PyPI.
    pause
    exit /b 1
)

echo.
echo === Готово! ===
echo Теперь запускай сервер так:
echo    .venv\Scripts\activate
echo    python simplespec.py
echo Или просто запусти run_server.bat (создам ниже).
pause
