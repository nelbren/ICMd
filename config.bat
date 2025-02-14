@ECHO OFF

REM config.bat v1.1 @ 2025-02-14 - nelbren@nelbren.com
CHCP 65001 > NUL

<NUL set /p ="config.yml........"
IF EXIST "config.yml" (
    call :color 2
    ECHO ✓
    call :color
) ELSE (
    call :color 6
    ECHO ☐
    call :color
    ECHO.
    call :color 70
    <NUL set /p ="copy config.yml.example config.yml"
    call :color
    ECHO.
    copy config.yml.example config.yml
    ECHO.

    <NUL set /p ="config.yml........"
    IF EXIST "config.yml" (
        call :color 2
        ECHO ✓
        call :color
    ) ELSE (
        call :color 4
        ECHO ×
        call :color
        ECHO.
        call :color 6
        ECHO Please manually copy config! ^( copy config.yml.example config.yml ^)
        call :color
        EXIT /B 5
    )
)

<NUL set /p ="INSTRUCTURE_URL..."
type config.yml | findstr replace-with-your-INFRASTRUCTURE-URL_and_rename_this_file 1>/nul 2>/nul
IF %ERRORLEVEL% == 0 (
    call :color 4
    ECHO ×
    call :color
    ECHO.
    ECHO Change INSTRUCTURE_URL in config.yml!
    EXIT /B 6
) ELSE (
    call :color 2
    ECHO ✓
    call :color
)

<NUL set /p ="API_KEY..........."
type config.yml | findstr replace-with-your-KEY_API_and_rename_this_file 1>/nul 2>/nul
IF %ERRORLEVEL% == 0 (
    call :color 4
    ECHO ×
    call :color
    ECHO.
    call :color 6
    ECHO Change APY_KEY in config.yml!
    call :color
    EXIT /B 7
) ELSE (
    call :color 2
    ECHO ✓
    call :color
)

<NUL set /p ="COURSE_ID........."
type config.yml | findstr replace-with-your-COURSE_ID_and_rename_this_file 1>/nul 2>/nul
IF %ERRORLEVEL% == 0 (
    call :color 4
    ECHO ×
    call :color
    ECHO.
    call :color 6
    ECHO Change COURSE_ID in config.yml!
    call :color
    EXIT /B 7
) ELSE (
    call :color 2
    ECHO ✓
    call :color
)

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