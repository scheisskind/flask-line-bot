from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import csv
import os

app = Flask(__name__)

# セキュリティ情報（環境変数で安全に管理してください）
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "lT+wIbkpj93F0XLr9TCI7NmqGx1C3trylxDvJ5xW5cvQIrHsei7cyKCamVvyvYMWm5aM74bDkdsYubnF0ZKlNKV1Zb9HVNL884vuIGesI5rMzXAzqpY4PcYdDi9VyFj6EEoctGG5zfr0g2b0SOHPDAdB04t89/1O/w1cDnyilFU=")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "e7330e654413863be5c40c0a87d595cf")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# CSV読み込み
garbage_data = []
with open('garbage.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # ヘッダースキップ
    for row in reader:
        garbage_data.append({
            'name': row[0],
            'type': row[1],
            'detail': row[2],
            'url': row[3],
            'related': [r for r in row[4:] if r]
        })

# ごみ名を検索
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

# LINEからのメッセージ受信
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
def handle_text_message(event):
    query = event.message.text.strip()
    reply = search_garbage(query)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# 起動
if __name__ == "__main__":
    app.run(port=5000)
