from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random

# Flaskアプリケーションのセットアップ
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション用の秘密鍵を設定

# Flask-Loginのセットアップ
login_manager = LoginManager()
login_manager.init_app(app)

# ユーザーデータ（ここでは簡単に辞書で管理）
users = {"teacher": {"password": "password123"}}  # ユーザー名: teacher, パスワード: password123

# ユーザー管理クラス
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# ログイン時に呼ばれるコールバック関数
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# 文章生成関数
def generate_academic_report(attitude, strong_subject, effort, assignment):
    attitude_variations = [
        f"授業態度は{attitude}。",
        f"授業に対して{attitude}姿勢を示す。",
        f"学習に対する意欲は高く、{attitude}。",
    ]

    subject_variations = [
        f"得意科目は{strong_subject}で、高い理解力を持つ。",
        f"{strong_subject}に強みを持ち、論理的思考を発揮する。",
    ]

    effort_variations = [
        f"{effort}工夫をしている。",
        f"{effort}ことを意識して学習に取り組む。",
    ]

    assignment_variations = [
        f"課題は{assignment}。",
        f"{assignment}点が評価される。",
    ]

    # ランダムに表現を選択
    report = (
        random.choice(attitude_variations) +
        random.choice(subject_variations) +
        random.choice(effort_variations) +
        random.choice(assignment_variations)
    )

    return report

# ホームページ
@app.route('/')
def index():
    return render_template('login.html')  # ログインページへリダイレクト

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        user = User(username)
        login_user(user)
        return redirect(url_for('generate_form'))
    return 'Invalid username or password'

# ログイン後、フォームを表示
@app.route('/generate_form')
@login_required
def generate_form():
    return render_template('generate_form.html')

# レポート生成
@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    attitude = request.form['attitude']
    strong_subject = request.form['strong_subject']
    effort = request.form['effort']
    assignment = request.form['assignment']

    if not all([attitude, strong_subject, effort, assignment]):
        return "All fields are required!"

    report = generate_academic_report(attitude, strong_subject, effort, assignment)
    return render_template('result.html', report=report)

# ログアウト処理
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render が提供する PORT を取得（デフォルト5000）
    app.run(host='0.0.0.0', port=port)  # 0.0.0.0 でリッスン
