#!/bin/bash
cd "$(dirname "$0")"
echo "필요한 라이브러리를 확인/설치합니다..."
python3 -m pip install -q -r requirements.txt
echo "서버를 시작합니다. 잠시 후 브라우저가 자동으로 열립니다."
echo "(끝내려면 이 창에서 Ctrl+C, 또는 그냥 창을 닫으세요)"
python3 app.py
