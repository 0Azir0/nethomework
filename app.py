from flask import Flask, session, redirect, url_for, request, render_template, jsonify
import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# 登入 - 跳轉 Discord 授權(謝謝GPT)
@app.route("/login")
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify")

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Discord 回傳 
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code in request", 400
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify'
    }
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    res = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)

    if res.status_code != 200:
        return f"Failed to exchange code. Status: {res.status_code}, Error: {res.text}", 400

    r = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    access_token = r.json().get("access_token")

    user_res = requests.get('https://discord.com/api/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })

    user = user_res.json()
    session['user'] = user
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))

#抽卡API在此!
@app.route("/api/draw-card")
def draw_card():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
#小明建模
    cards = [
        {"name": "我老爸得了", "rarity": "MVP", "image": "https://geng.9letu.com/wp-content/uploads/2025/03/1741056319-2025030107.png"},
        {"name": "回答我", "rarity": "!!!", "image": "https://i.ytimg.com/vi/iCzse-Wutmg/maxresdefault.jpg"},
        {"name": "陽光青提", "rarity": "GRAPE", "image": "https://i.ytimg.com/vi/j2lVtOVd9Dw/sddefault.jpg"},
        {"name": "怎麼不找找自己問題", "rarity": "!!!", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4i0SDr4mUsXWG3bPjqn0iHSsiz0pNcstx2w&s"}
    ]
    return random.choice(cards)

if __name__ == "__main__":
    app.run(debug=True)