import os
import threading
import webbrowser

from flask import Flask, render_template_string, request

app = Flask(__name__)
PORT = 5003

# ---- 슬라이드 11 "공개키 암호"의 예시(3233 = ? x ?)를 그대로 가져온 문제 ----
# 일부러 아주 작은 소수를 써서, 학생이 직접 소인수분해로 뚫을 수 있게 만들었습니다.
P = 61
Q = 53
N = P * Q  # 3233  (슬라이드 11의 그 숫자입니다)
PHI = (P - 1) * (Q - 1)
E = 17

FLAG = "FARM{RSA_NEEDS_BIG_PRIMES}"

# 공개키(N, E)만으로 평문을 암호화해서 미리 만들어 둡니다.
# 서버는 개인키(D)를 아무 데도 저장/노출하지 않습니다 — 학생이 직접 구해야 합니다.
CIPHERTEXT = [pow(ord(ch), E, N) for ch in FLAG]


PAGE = """
<!doctype html>
<title>RSA 깨기</title>
<!--
  [힌트 1] n = p × q 입니다. n이 이렇게 작으면(3233), p와 q를 직접 찾을 수도 있지 않을까요?
  [힌트 2] 파이썬으로 이렇게 해보세요:
           for p in range(2, 3233):
               if 3233 % p == 0:
                   print(p, 3233 // p)
  [힌트 3] p, q를 구했다면 φ(n) = (p-1) × (q-1) 입니다.
  [힌트 4] e·d ≡ 1 (mod φ(n)) 을 만족하는 d를 찾아야 합니다.
           파이썬 3.8+ 라면 d = pow(e, -1, φ(n)) 한 줄로 구해집니다.
  [힌트 5] 개인키 d를 구했다면, 각 암호문 블록에 pow(c, d, n) 을 하면 원래 글자의 아스키
           코드가 나옵니다. chr()로 바꿔서 이어붙이면 평문이 됩니다.
-->
<h2>RSA 깨기</h2>
<p>아래는 공개키와, 그 공개키로 암호화된 메시지(블록 단위)입니다.<br>
개인키 없이 이 메시지를 읽을 수 있을까요?</p>

<h3>공개키</h3>
<p>n = {{ n }}<br>e = {{ e }}</p>

<h3>암호문 (문자별 블록)</h3>
<p style="word-break:break-all">{{ ciphertext }}</p>

<h3>복호화 시도</h3>
{% if result %}<p><b>{{ result }}</b></p>{% endif %}
<form method="post">
  구한 개인키 d: <input name="d" autocomplete="off"><br>
  <button type="submit">복호화</button>
</form>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            d = int(request.form["d"])
            plain = "".join(chr(pow(c, d, N)) for c in CIPHERTEXT)
        except (ValueError, OverflowError):
            plain = None

        if plain == FLAG:
            result = f"정답입니다! 플래그: {plain}"
        elif plain is not None and plain.isprintable():
            result = f"복호화 결과: {plain}  (플래그와 다릅니다. d를 다시 확인해보세요)"
        else:
            result = "복호화 결과가 이상합니다. d 값을 다시 확인해보세요."

    return render_template_string(
        PAGE, n=N, e=E, ciphertext=CIPHERTEXT, result=result
    )


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    app.run(debug=True, port=PORT)
