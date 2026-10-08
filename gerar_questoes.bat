@echo off
rem Gera o banco de questoes. No Windows, basta dar dois cliques neste arquivo.
chcp 65001 >nul
cd /d "%~dp0"
set PROMPT=$G
where py >nul 2>nul
if %errorlevel%==0 (
  py scripts\gerar_questoes.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python nao encontrado. Instale em https://www.python.org/downloads/ marcando "Add Python to PATH".
  ) else (
    python scripts\gerar_questoes.py
  )
)
pause
