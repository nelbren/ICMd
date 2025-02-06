@ECHO OFF
REM run.bat v1.0 @ 2025-02-05 - nelbren@nelbren.com

IF EXIST ".venv\Scripts\activate" (
  .venv\Scripts\activate
  IF EXIST "config.yml" (
    call .venv\Scripts\activate
    flask run -p 8080 --host=0.0.0.0
  ) ELSE (
    ECHO Please make config.yml! ^( config.bat ^)
  )
) ELSE (
  ECHO Please make my virtual environment! ^( install.bat ^)
)
