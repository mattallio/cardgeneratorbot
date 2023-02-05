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

#checks if it's time to run any scheduled activity
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

#adds the user in the database and initializes its properties
def addUser(message):
    if str(message.chat.id) not in db:
        db[str(message.chat.id)] = {}
        db[str(message.chat.id)]['front'] = 0
        db[str(message.chat.id)]['back'] = 0
        db[str(message.chat.id)]['reveal'] = False
        db[str(message.chat.id)]['stack'] = "mnemonica"
        db[str(message.chat.id)]['selection'] = 1

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
    selection = random.randint(1,52)
    for user in db:
        db[user]['front'] = 0
        db[user]['back'] = 0
        db[user]['reveal'] = False
        db[user]['selection'] = selection
    print("Selection changed!!!")

def updateSelection(message):
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    if db[str(message.chat.id)]['stack'] == "mnemonica":
        stack = card2numbers.Mnemonica
    elif db[str(message.chat.id)]['stack'] == "memorandum":
        stack = card2numbers.Memorandum
    elif db[str(message.chat.id)]['stack'] == "daortiz":
        stack = card2numbers.Daortiz
    elif db[str(message.chat.id)]['stack'] == "redford":
        stack = card2numbers.Redford
    elif db[str(message.chat.id)]['stack'] == "Aroson":
        stack = card2numbers.Aronson
    number = int(stack[db[str(message.chat.id)]['selection']-1]) + 1
    count = 1
    for el in stack:
        if el == number:
            break
        else:
            count += 1
    db[str(message.chat.id)]['selection'] = count

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
    addUser(message)
    db[str(message.chat.id)]['front'] = 0
    db[str(message.chat.id)]['back'] = 0
    markup = ReplyKeyboardMarkup(row_width=2)
    generate = KeyboardButton("Generate Card")
    selected = KeyboardButton("Selected Card")
    markup.add(generate, selected)
    bot.send_message(message.chat.id, "Ok, here we go", reply_markup=markup)

#sets the preferred stack for the selection
@bot.message_handler(commands=["stack"])
def selectStack(message):
    addUser(message)
    markup = InlineKeyboardMarkup()
    mnemonica = InlineKeyboardButton("Mnemonica", callback_data="mnemonica")
    memorandum = InlineKeyboardButton("Memorandum", callback_data="memorandum")
    daortiz = InlineKeyboardButton("Daortiz", callback_data="daortiz")
    redford = InlineKeyboardButton("Redford", callback_data="redford")
    aronson = InlineKeyboardButton("Aroson", callback_data="aronson")
    markup.add(mnemonica, memorandum, daortiz, redford, aronson)
    bot.send_message(message.chat.id, "Select your preferred stack:", reply_markup=markup)

#sends the selected stack list
@bot.message_handler(commands=["memorandum_stack"])
def sendMemorandum(message):
    addUser(message)
    photo = open(r"Utilities/memorandum.png","rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

@bot.message_handler(commands=["mnemonica_stack"])
def sendMnemonica(message):
    addUser(message)
    photo = open(r"Utilities/mnemonica.png","rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

@bot.message_handler(commands=["daortiz_stack"])
def sendDaortiz(message):
    addUser(message)
    photo = open(r"Utilities/daortiz.png","rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

@bot.message_handler(commands=["redford_stack"])
def sendRedford(message):
    addUser(message)
    photo = open(r"Utilities/redford.png","rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

@bot.message_handler(commands=["aronson_stack"])
def sendAronson(message):
    addUser(message)
    photo = open(r"Utilities/aronson.png","rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

#commands to memorize the selected stack
@bot.message_handler(commands=["mnemonica"])
def trainMnemonica(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Mnemonica
    trainStack(message, stack)

@bot.message_handler(commands=["memorandum"])
def trainMemorandum(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Memorandum
    trainStack(message, stack)

@bot.message_handler(commands=["daortiz"])
def trainDaortiz(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Daortiz
    trainStack(message, stack)

@bot.message_handler(commands=["redford"])
def trainRedford(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Redford
    trainStack(message, stack)

@bot.message_handler(commands=["aronson"])
def trainAronson(message):
    addUser(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = card2numbers.Aronson
    trainStack(message, stack)

#command to disable the hints 
@bot.message_handler(commands=["expert"])
def expert(message):
    markup = InlineKeyboardMarkup()
    sure = InlineKeyboardButton("I am sure", callback_data="sure")
    cancel = InlineKeyboardButton("Cancel", callback_data="cancel")
    markup.add(sure, cancel)
    bot.send_message(message.chat.id, 'By clicking "I am sure" you will no longer get the hint of what the next card will be, are you sure you have memorized your selected stack? (you can always enable the hints by using the command /hints)', reply_markup=markup)

#command to enable hints
@bot.message_handler(commands=["hints"])
def activateHints(message):
    del db[str(message.chat.id)]['expert']
    bot.send_message(message.chat.id, "You've turned hints back on!")

#the bot sends a random card or tells the performer the card of the day
@bot.message_handler(func=lambda m:"GENERATE CARD" in m.text.upper())
def randomCard(message):
    addUser(message)
    if db[str(message.chat.id)]['front'] != 1 or ('expert' in db[str(message.chat.id)] and db[str(message.chat.id)]['expert'] == 1):
        db[str(message.chat.id)]['front'] += 1
        card = random.randint(1,53)
        photo = open(fr"Cards/{card}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
    else:
        db[str(message.chat.id)]['front'] += 1
        photo = open(fr"Cards/{db[str(message.chat.id)]['selection']}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
        if 'expert' in db[str(message.chat.id)] and db[str(message.chat.id)]['expert'] == 0:
            db[str(message.chat.id)]['expert'] = 1

#button to reveal the selected card
@bot.message_handler(func=lambda m:"SELECTED CARD" in m.text.upper())
def selectedCard(message):
    addUser(message)
    if db[str(message.chat.id)]['front'] < 4 or db[str(message.chat.id)]['back']<3:
        randomFunny(message)
        db[str(message.chat.id)]['back'] += 1
    else:
        back = random.randint(1, countFolder("Backs")-1)
        photo = open(fr"Backs/{back}.jpg", "rb")
        markup = InlineKeyboardMarkup()
        markup.row_width = 8
        markup.add(InlineKeyboardButton("TURN THE CARD", callback_data="reveal"))
        bot.send_photo(message.chat.id, photo, reply_markup=markup)
        photo.close()
        while db[str(message.chat.id)]['reveal'] == False:
            time.sleep(1)
        photo = open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
        db[str(message.chat.id)]['reveal'] = False       
        updateSelection(message)
        start(message)
    
#reveals the card when the button is pressed
@bot.callback_query_handler(func=lambda call: "reveal" == call.data)
def revealSelection(message):
    db[str(message.from_user.id)]['reveal'] = True

#sets the stack preference of the user
@bot.callback_query_handler(func=lambda call: "mnemonica" == call.data)
def setMnemonica(message):
    db[str(message.from_user.id)]['stack'] = "mnemonica"
    bot.send_message(message.from_user.id, "Setup completed!")

@bot.callback_query_handler(func=lambda call: "memorandum" == call.data)
def setMemorandum(message):
    db[str(message.from_user.id)]['stack'] = "memorandum"
    bot.send_message(message.from_user.id, "Setup completed!")

@bot.callback_query_handler(func=lambda call: "daortiz" == call.data)
def setDaortiz(message):
    db[str(message.from_user.id)]['stack'] = "daortiz"
    bot.send_message(message.from_user.id, "Setup completed!")

@bot.callback_query_handler(func=lambda call: "redford" == call.data)
def setRedford(message):
    db[str(message.from_user.id)]['stack'] = "redford"
    bot.send_message(message.from_user.id, "Setup completed!")

@bot.callback_query_handler(func=lambda call: "aronson" == call.data)
def setAronson(message):
    db[str(message.from_user.id)]['stack'] = "aronson"
    bot.send_message(message.from_user.id, "Setup completed!")

#saves the user changes
@bot.callback_query_handler(func=lambda call: "sure" == call.data)
def disableHints(message):
    db[str(message.from_user.id)]['expert'] = 1
    bot.send_message(message.from_user.id, "Changes have been saved!")

@bot.callback_query_handler(func=lambda call: "cancel" == call.data)
def cancel(message):
    bot.send_message(message.from_user.id, "Operation cancelled")

#main
if __name__ == "__main__":
    schedule.every().day.at(TIME).do(selectionOfDay)
    Thread(target=schedule_checker).start() 
    keep_alive()
    bot.polling()