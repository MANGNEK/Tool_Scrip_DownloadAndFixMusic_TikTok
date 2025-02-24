@echo off
echo Watting Install Lid For COde>>>>>
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Done !!!!!
pause
