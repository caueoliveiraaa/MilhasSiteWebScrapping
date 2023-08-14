import telebot
import json


JSON_DATA: dict = {}
with open('bot_info.json', 'r') as json_file:
    JSON_DATA = json.load(json_file)


TOKEN: str = JSON_DATA['token']
bot: telebot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help', 'start'])
def hello_friend(message):
    print(message)
    bot.reply_to(message, 'Hello friend')


def send_message_to_group(group_id, message):
    bot.send_message(group_id, message)


if __name__ == '__main__':
    print('bot initiated succesfully.')
    bot.infinity_polling()