import telebot
import random
import os
import schedule
import time
import pandas as pd
from replit import db
from threading import Thread
from keep_alive import keep_alive
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

API_KEY = os.environ['API_KEY']

bot = telebot.TeleBot(API_KEY)

#initialization settings
TIME = "02:00"
selection = 22

#checks if it's time to run any scheduled activity
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

#adds the user in the database and initializes its properties
def addUser(message):
    global db
    if str(message.chat.id) not in db:
        db[str(message.chat.id)] = {}
        db[str(message.chat.id)]['first'] = 0
        db[str(message.chat.id)]['reveal'] = False

#counts the elements in a folder
def countFolder(commandFolder):
   dir_path = fr'{commandFolder}'
   count = 0
   # Iterate directory
   for path in os.listdir(dir_path):
      # check if current path is a file
      if os.path.isfile(os.path.join(dir_path, path)):
         count += 1
   #print('File count:', count)
   return count

#randomly picks a selection for the day
def selectionOfDay():
    global selection, db
    for user in db:
        db[user]['first'] = 0
        db[user]['reveal'] = False
    selection = random.randint(1,52)

#helps in memorizing the preferred stack
def trainStack(message, stack):
    card = random.randint(1,52)
    photo = open(fr"Cards/{card}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()
    number = int(stack[card-1])
    if number != 0:
        time.sleep(5)
    bot.send_message(message.chat.id, number)

#sends a funny card
def randomFunny(message):
    randomCard = random.randint(1, countFolder("Funny"))
    photo = open(fr"Funny/{randomCard}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

#the bot welcomes the user
@bot.message_handler(commands=["start"])
def start(message):
    global db
    addUser(message)
    db[str(message.chat.id)]['first'] = 0
    markup = ReplyKeyboardMarkup(row_width=2)
    button1 = KeyboardButton("Generate Card")
    markup.add(button1)
    bot.send_message(message.chat.id, "Ok, here we go", reply_markup=markup)

#manda la lista dello stack memorandum
@bot.message_handler(commands=["memorandum_stack"])
def sendMemorandum(message):
    addUser(message)
    stack = open("memorandum.png","rb")
    bot.send_photo(message.chat.id, stack)
    stack.close()
    addUser(message)

#command to memorize the selected stack
@bot.message_handler(commands=["mnemonica"])
def trainMnemonica(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Mnemonica
    trainStack(message, stack)

#command to memorize the selected stack
@bot.message_handler(commands=["memorandum"])
def trainMemorandum(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Memorandum
    trainStack(message, stack)

#command to memorize the selected stack
@bot.message_handler(commands=["daortiz"])
def trainDaortiz(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Daortiz
    trainStack(message, stack)

#command to memorize the selected stack
@bot.message_handler(commands=["redford"])
def trainRedford(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Redford
    trainStack(message, stack)

#command to memorize the selected stack
@bot.message_handler(commands=["aronson"])
def trainAronson(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Aronson
    trainStack(message, stack)

#the bot sends a random card or tells the performer the card of the day
@bot.message_handler(func=lambda m:"GENERATE CARD" in m.text.upper())
def randomCard(message):
    addUser(message)
    global db, selection
    if db[str(message.chat.id)]['first'] != 1:
        db[str(message.chat.id)]['first'] += 1
        card = random.randint(1,53)
        photo = open(fr"Cards/{card}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
    else:
        db[str(message.chat.id)]['first'] += 1
        photo = open(fr"Cards/{selection}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
    
#revelation mode: on
@bot.message_handler(func=lambda m:"MM" in m.text.upper())
def activateSelectedCard(message):
    addUser(message)
    global db
    markup = ReplyKeyboardMarkup(row_width=2)
    button1 = KeyboardButton("Selected Card")
    markup.add(button1) 
    bot.send_message(message.chat.id, ".", reply_markup=markup)
    db[str(message.chat.id)]['first'] += 1
    for _ in range(1,10):
        randomCard(message)

#button to reveal the selected card
@bot.message_handler(func=lambda m:"SELECTED CARD" in m.text.upper())
def selectedCard(message):
    addUser(message)
    global selection
    back = random.randint(1, countFolder("Backs")-1)
    photo = open(fr"Backs/{back}.jpg", "rb")
    markup = InlineKeyboardMarkup()
    markup.row_width = 8
    markup.add(InlineKeyboardButton("TURN THE CARD", callback_data="reveal"))
    bot.send_photo(message.chat.id, photo, reply_markup=markup)
    photo.close()
    while db[str(message.chat.id)]['reveal'] == False:
        time.sleep(1)
    photo = open(rf"Cards/{selection}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()
    if db[str(message.chat.id)]['reveal'] == True:
        db[str(message.chat.id)]['reveal'] = False       
        selection = 1
        start(message)
    else:
        activateSelectedCard(message)
    
#reveals the card when the button is pressed
@bot.callback_query_handler(func=lambda call: "reveal" == call.data)
def revealSelection(message):
    db[str(message.from_user.id)]['reveal'] = True

if __name__ == "__main__":
    schedule.every().day.at(TIME).do(selectionOfDay)
    Thread(target=schedule_checker).start() 
    keep_alive()
    bot.polling()