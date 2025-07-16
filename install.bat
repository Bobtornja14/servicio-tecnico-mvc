@echo off
echo Instalando dependencias...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo ¡Instalación completada!
echo Para iniciar la aplicación, ejecute: run.bat
pause