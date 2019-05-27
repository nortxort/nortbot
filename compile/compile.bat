@echo off
TITLE NortBot Compiler
python -V > NUL 2> NUL
if errorlevel 1 echo PYTHON NOT IN PATH! && PAUSE && EXIT
python -m pip install -U pyinstaller --user
python -m pip install -r %~dp0..\requirements.txt --user
cd %~dp0
pyinstaller -F --clean "..\nortbot.py"
ECHO Copying cacert.pem
COPY ..\cacert.pem .\dist\cacert.pem
COPY ..\config.ini .\dist\config.ini
ECHO Done! Files are located in %~dp0dist
PAUSE
EXIT
