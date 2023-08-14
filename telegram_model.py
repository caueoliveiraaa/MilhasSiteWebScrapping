import telebot


TOKEN = ''
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['help', 'start'])
def hello_friend(message):
    print(message)
    bot.reply_to(message, 'Hello friend')


def send_message_to_group(group_id, message):
    bot.send_message(group_id, message)



if __name__ == '__main__':
    print('bot initiated succesfully.')
    send_message_to_group(group_id='', message='testing bot')
    bot.infinity_polling()
