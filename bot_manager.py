from bot import BotVk
from config import token_app, token_group, id_group

bot = BotVk(token_app, token_group, id_group, "BotInostranky")


while True:
    try:
        bot.start()
    except Exception as e:
        print("Something went wrong.....")
        print(e)
