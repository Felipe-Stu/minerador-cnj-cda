@echo off
setlocal

REM O Electron inicia o servidor Flask (main.py) e o encerra ao fechar a janela.
REM %~dp0 é a pasta deste arquivo, então o projeto funciona em qualquer local.
cd /d "%~dp0electron"
call npm start

endlocal
