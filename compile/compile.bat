@echo off
TITLE NortBot Compiler
python -V > NUL 2> NUL
if errorlevel 1 echo PYTHON NOT IN PATH! && PAUSE && EXIT
cd %~dp0
python -m pip install -U pyinstaller
python -m pip install -r %~dp0..\requirements.txt --user
pyinstaller -F --clean "..\nortbot.py" -p "%~dp0.."
ECHO Copying cacert.pem
COPY ..\cacert.pem .\dist\cacert.pem
ECHO Copying config.ini
COPY ..\config.ini .\dist\config.ini
ECHO Done! Files are located in %~dp0dist
PAUSE
EXIT
