import os
import sqlite3
import threading
import webbrowser

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "class-demo-only"

# ---- 여기 스위치 하나로 취약 모드 / 안전 모드를 전환합니다 ----
SECURE_MODE = False  # False: 문자열을 그대로 이어붙인 위험한 쿼리 / True: 파라미터 바인딩

DB = "demo.db"
PORT = 5001


def init_db():
    conn = sqlite3.connect(DB)
    conn.executescript(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            role TEXT
        );
        """
    )
    conn.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        [
            ("admin", "sup3rSecret!", "관리자"),
            ("alice", "alice1234", "일반 사용자"),
            ("bob", "bobpassword", "일반 사용자"),
        ],
    )
    conn.commit()
    conn.close()


LOGIN_PAGE = """
<!doctype html>
<title>학원 회원 로그인</title>
<!--
  [힌트 1] 이 페이지는 아이디/비밀번호를 그대로 SQL 문장에 끼워넣어 확인합니다.
  [힌트 2] 아이디 칸에 작은따옴표(') 하나만 넣고 로그인해보면 어떻게 될까요?
           (에러가 난다면, 그게 바로 "내 입력이 SQL 문법의 일부가 됐다"는 신호입니다.)
  [힌트 3] SQL에서 -- 뒤는 전부 주석 처리됩니다. 비밀번호 검사 자체를 통째로 지워버릴 수 있다면?
  [힌트 4] admin 계정 비밀번호를 몰라도, 아이디만으로 admin으로 로그인하는 방법이 있습니다.
-->
<h2>로그인</h2>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
<form method="post">
  아이디: <input name="username" autocomplete="off"><br>
  비밀번호: <input name="password" type="password"><br>
  <button type="submit">로그인</button>
</form>
<p style="color:gray">테스트 계정: alice/alice1234, bob/bobpassword (admin 비번은 비밀!)</p>
<p style="color:gray">현재 모드: {{ mode }}</p>
"""

WELCOME_PAGE = """
<!doctype html>
<title>환영합니다</title>
<h2>{{ user['username'] }}님 환영합니다 (권한: {{ user['role'] }})</h2>
<p>이 페이지는 로그인에 성공해야만 보이는 페이지입니다.</p>
<a href="/logout">로그아웃</a>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if SECURE_MODE:
            # 안전한 방식: 쿼리 구조를 먼저 확정하고 값은 나중에 끼워넣는다
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cur.execute(query, (username, password))
        else:
            # 위험한 방식: 입력값을 문자열에 그대로 이어붙인다
            query = (
                f"SELECT * FROM users WHERE username = '{username}' "
                f"AND password = '{password}'"
            )
            print("실행되는 쿼리:", query)  # 터미널에서 실제 쿼리를 눈으로 확인하기 위함
            cur.execute(query)

        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("welcome"))
        error = "로그인 실패"

    mode = "취약 모드 (SECURE_MODE = False)" if not SECURE_MODE else "안전 모드 (SECURE_MODE = True)"
    return render_template_string(LOGIN_PAGE, error=error, mode=mode)


@app.route("/welcome")
def welcome():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return render_template_string(WELCOME_PAGE, user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    # run_all.command 처럼 여러 서버를 한 스크립트에서 켤 때는 NO_RELOADER=1을 심어
    # Werkzeug 자동 재시작(프로세스가 두 개로 늘어나는 것)을 꺼서 PID 하나로 종료하기
    # 쉽게 만든다. 개별 run.command로 켤 때는 그대로 자동 재시작이 켜져 있어서
    # SECURE_MODE를 고치고 저장하면 바로 반영된다.
    use_reloader = os.environ.get("NO_RELOADER") != "1"
    if not use_reloader or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    app.run(debug=True, use_reloader=use_reloader, port=PORT)
