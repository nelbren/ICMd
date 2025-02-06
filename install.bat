@ECHO OFF

REM install.bat v1.7 @ 2024-12-16 - nelbren@nelbren.com

REM https://gabimarti.medium.com/personalizando-el-int%C3%A9rprete-de-comandos-de-windows-parte-iv-8b107aedf8d3
CHCP 65001 > NUL
REM https://batcheero.blogspot.com/2007/06/how-to-enabledelayedexpansion.html
setlocal ENABLEDELAYEDEXPANSION
REM https://stackoverflow.com/questions/21660249/how-do-i-make-one-particular-line-of-a-batch-file-a-different-color-then-the-oth

call :color f
<NUL set /p ="Python Install...."
call :color
python -V 1>/nul 2>/nul
IF %ERRORLEVEL% == 0 (
    call :color 2
    ECHO ✓
    call :color
) ELSE (
    call :color 4
    ECHO ×
    call :color
    ECHO.
    call :color 6
    ECHO Please manually install Python
    call :color
    EXIT /B 1
)

call :color f
<NUL set /p ="Python Venv......."
call :color
IF EXIST ".venv\Scripts\activate" (
    call :color 2
    ECHO ✓
    call :color 
) ELSE (
    call :color 6
    ECHO ☐
    call :color
    ECHO.
    call :color 70
    <NUL set /p ="python -m venv .venv"
    call :color
    ECHO.
    python -m venv .venv
    ECHO.
    
    call :color f
    <NUL set /p ="Python Venv......."
    call :color
    IF EXIST ".venv\Scripts\activate" (
        call :color 2
        ECHO ✓
        call :color 
    ) ELSE (
        call :color 4
        ECHO ×
        call :color
        ECHO.
        call :color 6
        ECHO Please manually make my virtual environment! ^( python -m venv .venv ^)
        call :color
        EXIT /B 2
    )
)

call .venv\Scripts\activate

call :color f
<NUL set /p ="Pip Updated......."
call :color
pip list --outdated 2>/nul | findstr pip 1>/nul
IF %ERRORLEVEL% == 0 (
    call :color 6
    ECHO ☐
    call :color
    ECHO.
    call :color 70
    <NUL set /p ="python -m pip install --upgrade pip"
    ECHO.
    call :color
    .venv\Scripts\python.exe -m pip install --upgrade pip
    IF !ERRORLEVEL! == 0 (
        call :color f
        <NUL set /p ="Pip Updated......."
        call :color
        call :color 2
        ECHO ✓
        call :color
    ) ELSE (
        call :color f
        <NUL set /p ="Pip Updated......."
        call :color
        call :color 4
        ECHO ×
        call :color
        ECHO.
        call :color 6
        ECHO Please manually update pip! ^( .venv\Scripts\python.exe -m pip install --upgrade pip ^)
        call :color
        EXIT /B 3
    )
) ELSE (
    call :color 2
    ECHO ✓
    call :color 
)

call :color f
<NUL set /p ="Python Modules...."
call :color
FOR /f "tokens=*" %%m IN (requirements.txt) DO (
    FOR /f "tokens=1,2,3 delims= " %%a IN ("%%m") do (
        SET modulo=%%a
        SET import=%%c
    )

    call :color f
    <NUL set /p ="!modulo!..."
    call :color
    IF "!import!" == "" (
        python -c "import !modulo!" 2>/nul
    ) ELSE (
        python -c "import !import!" 2>/nul
    )
    IF !ERRORLEVEL! == 0 (
        call :color 2
        <NUL set /p ="✓ "
        call :color
    ) ELSE (
        call :color 6
        ECHO ☐
        call :color
        ECHO.
        call :color 70
        <NUL set /p ="pip install !modulo!"
        call :color
        ECHO.
        .venv\Scripts\pip.exe install !modulo!
        ECHO.

        .venv\Scripts\pip.exe list 2>/nul | findstr !modulo! 1>/nul
        IF !ERRORLEVEL! == 0 (
            call :color f
            <NUL set /p ="!modulo!..."
            call :color
            call :color 2
            <NUL set /p ="✓ "
            call :color
        ) ELSE (
            call :color f
            <NUL set /p ="!modulo!..."
            call :color
            call :color 4
            ECHO ×
            call :color
            ECHO.
            call :color 6
            ECHO Please manually install the modules! ^( .venv\Scripts\pip.exe install -r requirements.txt ^)
            call :color
            EXIT /B 4
        )
    )
)
ECHO.

goto :eof

REM https://stackoverflow.com/questions/2048509/how-to-echo-with-different-colors-in-the-windows-command-line
:: Displays a text without new line at the end (unlike echo)
:echo
@<nul set /p ="%*"
@goto :eof

:: Change color to the first parameter (same codes as for the color command) 
:: And display the other parameters (write $ at the end for new line)
:color
@echo off
IF [%ESC%] == [] for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
SET color=0%1
IF [%color%] == [0] SET color=07
SET fore=%color:~-1%
SET back=%color:~-2,1% 
SET color=%ESC%[
if %fore% LEQ 7 (
  if %fore% == 0 SET color=%ESC%[30
  if %fore% == 1 SET color=%ESC%[34
  if %fore% == 2 SET color=%ESC%[32
  if %fore% == 3 SET color=%ESC%[36
  if %fore% == 4 SET color=%ESC%[31
  if %fore% == 5 SET color=%ESC%[35
  if %fore% == 6 SET color=%ESC%[33
  if %fore% == 7 SET color=%ESC%[37
) ELSE (
  if %fore% == 8 SET color=%ESC%[90
  if %fore% == 9  SET color=%ESC%[94
  if /i %fore% == a SET color=%ESC%[92
  if /i %fore% == b SET color=%ESC%[96
  if /i %fore% == c SET color=%ESC%[91
  if /i %fore% == d SET color=%ESC%[95
  if /i %fore% == e SET color=%ESC%[93
  if /i %fore% == f SET color=%ESC%[97
)
if %back% == 0 (SET color=%color%;40) ELSE (
  if %back% == 1 SET color=%color%;44
  if %back% == 2 SET color=%color%;42
  if %back% == 3 SET color=%color%;46
  if %back% == 4 SET color=%color%;41
  if %back% == 5 SET color=%color%;45
  if %back% == 6 SET color=%color%;43
  if %back% == 7 SET color=%color%;47
  if %back% == 8 SET color=%color%;100
  if %back% == 9  SET color=%color%;104
  if /i %back% == a SET color=%color%;102
  if /i %back% == b SET color=%color%;106
  if /i %back% == c SET color=%color%;101
  if /i %back% == d SET color=%color%;105
  if /i %back% == e SET color=%color%;103
  if /i %back% == f SET color=%color%;107
)
SET color=%color%m
:repeatcolor
if [%2] NEQ [$] SET color=%color%%~2
shift
if [%2] NEQ [] if [%2] NEQ [$] SET color=%color% & goto :repeatcolor
if [%2] EQU [$] (echo %color%) else (<nul set /p ="%color%")
goto :eof