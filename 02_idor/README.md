# IDOR (인가 누락) 실습 (약 30분)

슬라이드 31 "인가 누락과 IDOR" 예시(`GET /api/orders/1024` → `GET /api/orders/1025`)를
실제로 동작하는 미니 주문 조회 API로 만든 것입니다. "인증 ≠ 인가"를 직접 겪어봅니다.

## 준비 (2분)

```bash
cd 02_idor
pip install -r requirements.txt
python app.py
```

브라우저에서 http://127.0.0.1:5002 접속.

## 진행 순서

### 1. 정상 흐름 먼저 (3분)
`alice` / `alice1234` 로 로그인 → "내 주문" 목록에서 본인 주문(`#1`)을 클릭해 정상 조회.

### 2. 공격 — 학생 스스로 풀어보기 (5분)
"로그인은 alice로 유지한 채, bob의 주문 내용을 알아내보라"고 과제를 냅니다.
이 챌린지는 SQLi보다 훨씬 빨리 풀립니다. 페이지 소스보기를 하면 힌트가 이미
HTML 주석으로 숨어있습니다.

<details>
<summary>힌트 1</summary>

주문을 클릭하면 이동하는 URL을 잘 보세요. 그 안에 숫자가 하나 보일 겁니다.
</details>

<details>
<summary>힌트 2</summary>

그 숫자를 다른 값으로 바꿔서 직접 주소창에 입력해보세요.
예: `http://127.0.0.1:5002/api/orders/2`
</details>

<details>
<summary>정답</summary>

alice로 로그인한 상태에서 주소창에 `/api/orders/2` 를 입력하면 bob의 주문(주소 포함)이
그대로 보입니다. bob으로 로그인해서 `/api/orders/1` 을 열어도 마찬가지입니다.
</details>

### 3. 왜 뚫리는지 (5분)
`app.py`의 `get_order` 함수를 같이 읽습니다. 로그인 여부(인증)만 확인하고,
`order['user_id']`가 지금 로그인한 사람과 같은지(인가)는 확인하지 않는다는 점을 짚습니다.
슬라이드 31의 "화면에서의 접근만 막는 것이 방어의 전부가 아니다"와 연결합니다.

### 4. 패치 (10분)
`app.py` 상단의 `SECURE_MODE = False` 를 `True` 로 바꾸고 서버를 재시작합니다.

```bash
python app.py
```

같은 방식으로 남의 주문 번호(`/api/orders/2`)에 접근 → 이번엔 `403 Forbidden`이
뜨는 것을 확인합니다. 소유자 검증 코드 한 줄(`if SECURE_MODE and order["user_id"] != session["user_id"]`)이
어떻게 막았는지 짚으며 마무리합니다.

---
실습이 끝나면 `SECURE_MODE`를 다시 `False`로 되돌려 두면 다음 반에서도 그대로 쓸 수 있습니다.
