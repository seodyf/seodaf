from pyrogram import Client
from time import sleep

api_id = 123456 #айди
api_hash = " " #хэш
chat_id = ['@бот1', '@бот2'] # и тд.
message_text = "/next"
sticker_file_id = "#айди стикера"

app = Client("my_bot", api_id, api_hash)
app.start()

def send_message():
for x in chat_id:
app.send_message(x, message_text)
sleep(2)
app.send_message(x, message_text)

while True:
send_message()
sleep(10)

idle()