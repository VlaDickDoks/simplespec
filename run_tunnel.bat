@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Запуск Cloudflare Tunnel ===
echo Через пару секунд появится ссылка вида https://....trycloudflare.com
echo Эту ссылку кидай другу. Окно не закрывай, пока он смотрит.
echo.

"%~dp0req\cloudflared.exe" tunnel --protocol http2 --url http://localhost:1488
pause