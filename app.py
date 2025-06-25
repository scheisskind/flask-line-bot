from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import csv
import os

app = Flask(__name__)

# 環境変数から取得
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise Exception("LINEのトークンやシークレットが設定されていません。")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# CSV読み込み
garbage_data = []
with open('garbage.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        garbage_data.append({
            'name': row[0],
            'type': row[1],
            'detail': row[2],
            'url': row[3],
            'related': [r for r in row[4:] if r]
        })

def search_garbage(query):
    for item in garbage_data:
        if query in item['name']:
            message = f"{item['name']} は【{item['type']}】です。\n"
            if item['detail']:
                message += f"{item['detail']}\n"
            if item['url']:
                message += f"🔗 詳細: {item['url']}\n"
            if item['related']:
                message += "🔁 関連: " + "・".join(item['related'])
            return message
    return "該当するごみが見つかりませんでした。"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("エラー:", e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()
    reply = search_garbage(user_text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# ✅ Flask起動（Render用）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
