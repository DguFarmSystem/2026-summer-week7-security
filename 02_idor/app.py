import os
import sqlite3
import threading
import webbrowser

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "class-demo-only"

# ---- 여기 스위치 하나로 취약 모드 / 안전 모드를 전환합니다 ----
SECURE_MODE = False  # False: 소유자 확인 없이 아무 주문이나 조회 가능 / True: 소유자 검증

DB = "idor_demo.db"
PORT = 5002


def init_db():
    conn = sqlite3.connect(DB)
    conn.executescript(
        """
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS orders;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            item TEXT,
            address TEXT
        );
        """
    )
    conn.executemany(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        [("alice", "alice1234"), ("bob", "bobpassword")],
    )
    conn.executemany(
        "INSERT INTO orders (user_id, item, address) VALUES (?, ?, ?)",
        [
            (1, "노트북", "서울시 알파아파트 101동 202호 (alice 개인정보)"),
            (2, "키보드", "부산시 베타빌라 5층 (bob 개인정보)"),
        ],
    )
    conn.commit()
    conn.close()


LOGIN_PAGE = """
<!doctype html>
<title>학원 주문 시스템 로그인</title>
<!--
  [힌트 0] 로그인은 정상적으로 하시면 됩니다. 진짜 챌린지는 로그인 다음,
           "내 주문" 페이지에 있습니다. 로그인 후 페이지 소스보기를 해보세요.
-->
<h2>로그인</h2>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
<form method="post">
  아이디: <input name="username" autocomplete="off"><br>
  비밀번호: <input name="password" type="password"><br>
  <button type="submit">로그인</button>
</form>
<p style="color:gray">테스트 계정: alice/alice1234, bob/bobpassword</p>
<p style="color:gray">현재 모드: {{ mode }}</p>
"""

MYPAGE = """
<!doctype html>
<title>내 주문</title>
<!--
  [힌트 1] 주문을 클릭하면 어떤 URL로 이동하나요? 그 안에 있는 숫자는 뭘까요?
  [힌트 2] 그 숫자를 로그인한 사람과 상관없이 아무 값으로나 바꿔서 접속해보세요.
  [힌트 3] 지금 로그인한 사람 것이 아닌 주문도 열리나요? 서버는 "누구 것인지"를 확인할까요?
-->
<h2>{{ username }}님의 주문 목록</h2>
<ul>
{% for o in orders %}
  <li><a href="/api/orders/{{ o['id'] }}" target="_blank">주문 #{{ o['id'] }} - {{ o['item'] }}</a></li>
{% endfor %}
</ul>
<p>다른 주문 번호로도 접속할 수 있는지 한 번 시도해보세요.</p>
<a href="/logout">로그아웃</a>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (request.form["username"], request.form["password"]),
        ).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("mypage"))
        error = "로그인 실패"

    mode = "취약 모드 (소유자 검증 없음)" if not SECURE_MODE else "안전 모드 (소유자 검증 있음)"
    return render_template_string(LOGIN_PAGE, error=error, mode=mode)


@app.route("/mypage")
def mypage():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template_string(MYPAGE, username=session["username"], orders=orders)


@app.route("/api/orders/<int:order_id>")
def get_order(order_id):
    # 인증(Authentication): 로그인은 했는가?
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    order = conn.execute(
        "SELECT * FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    conn.close()

    if order is None:
        abort(404)

    # 인가(Authorization): 이 주문이 로그인한 사용자의 것인가?
    if SECURE_MODE and order["user_id"] != session["user_id"]:
        abort(403)

    return jsonify(
        {
            "order_id": order["id"],
            "item": order["item"],
            "address": order["address"],
            "owner_user_id": order["user_id"],
        }
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    app.run(debug=True, port=PORT)
