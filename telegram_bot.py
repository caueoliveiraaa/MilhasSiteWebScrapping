from general import GeneralFuncs as func
import telebot
import json


JSON_DATA: dict = {}
with open('bot_info.json', 'r') as json_file:
    JSON_DATA = json.load(json_file)


TOKEN: str = JSON_DATA['token']
bot: telebot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help', 'start'])
def hello_friend(message):
    try:
        print(message)
        bot.reply_to(message, 'Hello friend')
    except:
        func.display_error()


def send_message_to_group(group_id, message):
    try:
        bot.send_message(group_id, message)
    except:
        func.display_error()


if __name__ == '__main__':
    print('bot initiated succesfully.')
    # bot.infinity_polling()    
    send_message_to_group(group_id=JSON_DATA['channelNacional'], message='testando bot')