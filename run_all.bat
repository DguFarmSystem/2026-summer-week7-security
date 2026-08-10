@echo off
cd /d "%~dp0"
echo 3개 챌린지에 필요한 라이브러리를 설치합니다...
python -m pip install -q -r 01_sql_injection\requirements.txt
python -m pip install -q -r 02_idor\requirements.txt
python -m pip install -q -r 03_rsa_break\requirements.txt

echo.
echo 서버 3개를 각각 새 창으로 켭니다. 창마다 브라우저 탭도 자동으로 열립니다.
echo   SQL Injection : http://127.0.0.1:5001
echo   IDOR          : http://127.0.0.1:5002
echo   RSA 깨기       : http://127.0.0.1:5003
echo.
echo 끝내려면 새로 열린 3개 창을 각각 닫으세요.

set NO_RELOADER=1
start "SQL Injection (:5001)" cmd /k "cd /d 01_sql_injection && python app.py"
start "IDOR (:5002)" cmd /k "cd /d 02_idor && python app.py"
start "RSA 깨기 (:5003)" cmd /k "cd /d 03_rsa_break && python app.py"
