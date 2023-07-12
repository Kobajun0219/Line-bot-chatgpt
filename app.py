from flask import Flask
from flask import request
import os
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)
from dotenv import load_dotenv

import openai

# generate instance
app = Flask(__name__)

#key
# .envファイルの内容を読み込見込む
load_dotenv()
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# API_KEY
openai.api_key = OPENAI_API_KEY
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# get environmental value from heroku
# ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
# CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

# endpoint
@app.route("/")
def test():
    return "<h1>It Works!</h1>"

# endpoint from linebot
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
		signature = request.headers['X-Line-Signature']

		# get request body as text
		body = request.get_data(as_text=True)
		app.logger.info("Request body: " + body)

		# handle webhook body
		try:
			handler.handle(body, signature)
		except InvalidSignatureError:
			print("Invalid signature. Please check your channel access token/channel secret.")
			abort(400)
		return 'OK'

# handle message from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  response_text = generate_response(event.message.text)
  line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(text=response_text))


# OpenAIのAPIを使ってChat GPTに入力を渡し、応答を取得する
def generate_response(input_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user","content": input_text}]
    )
    answer = response['choices'][0]['message']['content']
    return answer

# message_text = "お金とは"
# response_text = generate_response(message_text)
# print(message_text)
# print(response_text)

# if __name__ == "__main__":
# 	app.run()

# 修正後
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
