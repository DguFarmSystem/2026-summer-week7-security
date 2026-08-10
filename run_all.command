#!/bin/bash
cd "$(dirname "$0")"

echo "3개 챌린지에 필요한 라이브러리를 설치합니다..."
python3 -m pip install -q -r 01_sql_injection/requirements.txt
python3 -m pip install -q -r 02_idor/requirements.txt
python3 -m pip install -q -r 03_rsa_break/requirements.txt

echo ""
echo "서버 3개를 동시에 켭니다. 각자 자동으로 브라우저 탭이 열립니다."
echo "  SQL Injection : http://127.0.0.1:5001"
echo "  IDOR          : http://127.0.0.1:5002"
echo "  RSA 깨기       : http://127.0.0.1:5003"
echo ""
echo "종료하려면 이 창에서 Ctrl+C, 또는 그냥 창을 닫으세요."

# 한 스크립트에서 여러 서버를 켤 때는 Flask 자동 재시작(reloader)을 꺼서
# 서버 하나당 프로세스가 딱 하나만 뜨게 만든다 (그래야 종료할 때 PID로 확실히 잡힘).
export NO_RELOADER=1

PIDS=()

cleanup() {
    echo ""
    echo "서버를 종료합니다..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null
    done
    exit 0
}
trap cleanup EXIT INT TERM HUP

(cd 01_sql_injection && exec python3 app.py) &
PIDS+=($!)
(cd 02_idor && exec python3 app.py) &
PIDS+=($!)
(cd 03_rsa_break && exec python3 app.py) &
PIDS+=($!)

wait
