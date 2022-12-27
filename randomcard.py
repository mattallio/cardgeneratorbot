import telebot, random, os, time
import pandas as pd
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from keep_alive import keep_alive

API_KEY = os.environ['API_KEY']

bot = telebot.TeleBot(API_KEY)

selection = 0
reveal = False
language = "it"
acaanNum = ""
acaanSelection = 0
acaanSuit = ""
acaanFind = 0
listening = 0
first = 1

#reading of the excel
card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
CodesIt = card2numbers.CodesIt
CodesEn = card2numbers.CodesEn
Memorandum = card2numbers.Memorandum
MemorandumCodes = card2numbers.MEMORANDUM
CardsIdx = card2numbers.Numbers

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

#a random funny card is sent if no card is selected
def randomFunny(message):
    randomCard = random.randint(1, countFolder("Funny"))
    photo = open(fr"Funny/{randomCard}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

#greetings
@bot.message_handler(commands=["start"])
def start(message):
    global first
    first = 1
    markup = ReplyKeyboardMarkup(row_width=2)
    button1 = KeyboardButton("Generate Card")
    markup.add(button1)
    bot.send_message(message.chat.id, "Ok, here we go", reply_markup=markup)

#sends the memorandum stack
@bot.message_handler(commands=["memorandum_stack"])
def sendMemorandum(message):
    stack = open("memorandum.png","rb")
    bot.send_photo(message.chat.id, stack)
    stack.close()

#training of memorandum
@bot.message_handler(commands=["memorandum"])
def trainMemorandum(message):
    card = random.randint(1,52)
    photo = open(fr"Cards/{card}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()
    number = int(Memorandum[card-1])
    if number != 0:
        time.sleep(5)
    bot.send_message(message.chat.id, number)

#randomly generates a card
@bot.message_handler(func=lambda m:"GENERATE CARD" in m.text.upper())
def randomCard(message):
    card = random.randint(1,53)
    photo = open(fr"Cards/{card}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()

#card selected
@bot.message_handler(func=lambda m:"MM" in m.text.upper())
def activateSelectedCard(message):
    markup = ReplyKeyboardMarkup(row_width=2)
    button1 = KeyboardButton("Selected Card")
    markup.add(button1) 
    if first == 1:
        bot.send_message(message.chat.id, ".", reply_markup=markup)
        for _ in range(1,10):
            randomCard(message)
    else:
        bot.send_message(message.chat.id, "Sorry, can't help you :(", reply_markup=markup)

#selected card revelation
@bot.message_handler(func=lambda m:"SELECTED CARD" in m.text.upper())
def selectedCard(message):
    global reveal, selection, first
    selectioncard = open(r"Cards/selection.txt", "r")
    selectionNum = int(selectioncard.read())
    selectioncard.close()
    if selectionNum>0 and selectionNum <= 53:
        back = random.randint(1, countFolder("Backs")-1)
        photo = open(fr"Backs/{back}.jpg", "rb")
        markup = InlineKeyboardMarkup()
        markup.row_width = 8
        markup.add(InlineKeyboardButton("TURN THE CARD", callback_data="reveal"))
        bot.send_photo(message.chat.id, photo, reply_markup=markup)
        photo.close()
        while reveal == False:
            time.sleep(1)
        photo = open(rf"Cards/{selectionNum}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
    else:
        randomFunny(message)
    if reveal == True:
        reveal = False
        selectedcard = open(r"Cards/selection.txt", "w")
        selectedcard.write("0")
        selectedcard.close()
        selection = 0
        start(message)
    else:
        first = 0
        activateSelectedCard(message)
    

#acaan mode on
@bot.message_handler(func=lambda m:"ACAAN" in m.text.upper())
def activateACAAN(message):
    global acaanSelection, acaanSuit, listening, acaanFind
    markup = ReplyKeyboardMarkup(row_width=2)
    button3 = KeyboardButton("♣")
    button4 = KeyboardButton("♦")
    button2 = KeyboardButton("♥")
    button1 = KeyboardButton("♠")
    markup.add(button1, button2, button3, button4)
    bot.send_message(message.chat.id, "So you would like to perform the mythical ACAAN?")
    time.sleep(1)
    bot.send_message(message.chat.id, "So be it. Tell me the suit of selected card",reply_markup=markup)
    while acaanSelection != 1:
        time.sleep(1)
    acaanSelection = 0
    markup = ReplyKeyboardMarkup()
    bot.send_message(message.chat.id, "Let's move on",reply_markup=markup)
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("A", callback_data="1")
    button2 = InlineKeyboardButton("2", callback_data="2")
    button3 = InlineKeyboardButton("3", callback_data="3")
    button4 = InlineKeyboardButton("4", callback_data="4")
    button5 = InlineKeyboardButton("5", callback_data="5")
    button6 = InlineKeyboardButton("6", callback_data="6")
    button7 = InlineKeyboardButton("7", callback_data="7")
    button8 = InlineKeyboardButton("8", callback_data="8")
    button9 = InlineKeyboardButton("9", callback_data="9")
    button10 = InlineKeyboardButton("10", callback_data="10")
    button11 = InlineKeyboardButton("J", callback_data="11")
    button12 = InlineKeyboardButton("Q", callback_data="12")
    button13 = InlineKeyboardButton("K", callback_data="13")
    markup.add(button1,button2,button3,button4,button5,button6,button7,button8,button9,button10,button11,button12,button13)
    bot.send_message(message.chat.id, "Now tell me the value of the selected card",reply_markup=markup)
    while acaanSelection != 1:
        time.sleep(1)
    acaanSelection = 0
    position=0
    selectionPos=0
    card = acaanSuit + acaanNum
    for code in MemorandumCodes:
        if code == card:
            selectionPos = position + 1
        position +=1
    markup = ReplyKeyboardMarkup()
    bot.send_message(message.chat.id, "Now, tell me at which number you want your card to appear",reply_markup=markup)
    listening = 1
    while acaanSelection != 1:
        time.sleep(1)
    acaanSelection = 0
    listening = 0
    if acaanFind == selectionPos:
        bottomCard = 52
    elif acaanFind > selectionPos:
        bottomCard = 51 - (acaanFind-selectionPos)
    else:
        bottomCard = selectionPos-acaanFind-1
    count=0
    for code in MemorandumCodes:
        if count == bottomCard:
            bottomCard = code
        count+=1
    count = 1
    for code in CodesIt:
        if code == bottomCard:
            photo = open(fr"Cards/{count}.jpg", "rb")
            bot.send_photo(message.chat.id, photo)
            photo.close()
        count += 1
    time.sleep(0.5)
    for i in range(1,4):
        randomCard(message)
        time.sleep(0.5)
    for i in range(1,10):
        randomFunny(message)
        time.sleep(0.5)
    start(message)

#checks if a message selects a card
def checkSelection(message):
    global language
    for code in CodesIt:
        if len(message.text) == 2 and message.text.upper() in code:
            language = "it"
            return True
    for code in CodesEn:
        language = "en"
        if len(message.text) == 2 and message.text.upper() in code:
            return True
    return False

#selected card saved in a text file
@bot.message_handler(func=checkSelection)
def saveSelection(message):
    global selection, language, first
    cardNum = 1
    if language == "it":
        for code in CodesIt:
            if message.text.upper() in code:
                break
            else:
                cardNum += 1
    elif language == "en":
        for code in CodesEn:
            if message.text.upper() in code:
                break
            else:
                cardNum += 1
    selection = cardNum
    selectionFile = open(r"Cards/selection.txt", "w")
    selectionFile.write(str(selection))
    selectionFile.close()
    #15 random cards sent to cover the messages
    for _ in range(1,15):
        randCard = random.randint(1,countFolder("Funny"))
        photo = open(rf"Funny/{randCard}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
    first = 0
    activateSelectedCard(message)

@bot.message_handler(func=lambda m:"♣" == m.text.upper())
def clubs(message):
    global acaanSelection, acaanSuit
    acaanSelection = 1
    acaanSuit = "F"

@bot.message_handler(func=lambda m:"♦" == m.text.upper())
def activateACAAN(message):
    global acaanSelection, acaanSuit
    acaanSelection = 1
    acaanSuit = "Q"

@bot.message_handler(func=lambda m:"♥" == m.text.upper())
def activateACAAN(message):
    global acaanSelection, acaanSuit
    acaanSelection = 1
    acaanSuit = "C"

@bot.message_handler(func=lambda m:"♠" == m.text.upper())
def activateACAAN(message):
    global acaanSelection, acaanSuit
    acaanSelection = 1
    acaanSuit = "P"

@bot.message_handler(func=lambda m:"1" == m.text.upper())
def select1(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 1
@bot.message_handler(func=lambda m:"2" == m.text.upper())
def select2(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 2
@bot.message_handler(func=lambda m:"3" == m.text.upper())
def select3(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 3
@bot.message_handler(func=lambda m:"4" == m.text.upper())
def select4(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 4
@bot.message_handler(func=lambda m:"5" == m.text.upper())
def select5(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 5
@bot.message_handler(func=lambda m:"6" == m.text.upper())
def select6(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 6
@bot.message_handler(func=lambda m:"7" == m.text.upper())
def select7(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 7
@bot.message_handler(func=lambda m:"8" == m.text.upper())
def select8(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 8
@bot.message_handler(func=lambda m:"9" == m.text.upper())
def select9(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 9
@bot.message_handler(func=lambda m:"10" == m.text.upper())
def select10(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 10
@bot.message_handler(func=lambda m:"11" == m.text.upper())
def select11(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 11
@bot.message_handler(func=lambda m:"12" == m.text.upper())
def select12(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 12
@bot.message_handler(func=lambda m:"13" == m.text.upper())
def select13(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 13
@bot.message_handler(func=lambda m:"14" == m.text.upper())
def select14(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 14
@bot.message_handler(func=lambda m:"15" == m.text.upper())
def select15(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 15
@bot.message_handler(func=lambda m:"16" == m.text.upper())
def select16(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 16
@bot.message_handler(func=lambda m:"17" == m.text.upper())
def select17(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 17
@bot.message_handler(func=lambda m:"18" == m.text.upper())
def select18(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 18
@bot.message_handler(func=lambda m:"19" == m.text.upper())
def select19(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 19
@bot.message_handler(func=lambda m:"20" == m.text.upper())
def select20(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 20
@bot.message_handler(func=lambda m:"21" == m.text.upper())
def select21(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 21
@bot.message_handler(func=lambda m:"22" == m.text.upper())
def select22(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 22
@bot.message_handler(func=lambda m:"23" == m.text.upper())
def select23(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 23
@bot.message_handler(func=lambda m:"24" == m.text.upper())
def select24(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 24
@bot.message_handler(func=lambda m:"25" == m.text.upper())
def select25(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 25
@bot.message_handler(func=lambda m:"26" == m.text.upper())
def select26(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 26
@bot.message_handler(func=lambda m:"27" == m.text.upper())
def select27(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 27
@bot.message_handler(func=lambda m:"28" == m.text.upper())
def select28(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 28
@bot.message_handler(func=lambda m:"29" == m.text.upper())
def select29(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 29
@bot.message_handler(func=lambda m:"30" == m.text.upper())
def select30(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 30
@bot.message_handler(func=lambda m:"31" == m.text.upper())
def select31(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 31
@bot.message_handler(func=lambda m:"32" == m.text.upper())
def select32(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 32
@bot.message_handler(func=lambda m:"33" == m.text.upper())
def select33(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 33
@bot.message_handler(func=lambda m:"34" == m.text.upper())
def select34(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 34
@bot.message_handler(func=lambda m:"35" == m.text.upper())
def select35(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 35
@bot.message_handler(func=lambda m:"36" == m.text.upper())
def select36(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 36
@bot.message_handler(func=lambda m:"37" == m.text.upper())
def select37(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 37
@bot.message_handler(func=lambda m:"38" == m.text.upper())
def select38(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 38
@bot.message_handler(func=lambda m:"39" == m.text.upper())
def select39(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 39
@bot.message_handler(func=lambda m:"40" == m.text.upper())
def select40(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 40
@bot.message_handler(func=lambda m:"41" == m.text.upper())
def select41(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 41
@bot.message_handler(func=lambda m:"42" == m.text.upper())
def select42(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 42
@bot.message_handler(func=lambda m:"43" == m.text.upper())
def select43(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 43
@bot.message_handler(func=lambda m:"44" == m.text.upper())
def select44(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 44
@bot.message_handler(func=lambda m:"45" == m.text.upper())
def select45(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 45
@bot.message_handler(func=lambda m:"46" == m.text.upper())
def select46(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 46
@bot.message_handler(func=lambda m:"47" == m.text.upper())
def select47(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 47
@bot.message_handler(func=lambda m:"48" == m.text.upper())
def select48(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 48
@bot.message_handler(func=lambda m:"49" == m.text.upper())
def select49(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 49
@bot.message_handler(func=lambda m:"50" == m.text.upper())
def select50(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 50
@bot.message_handler(func=lambda m:"51" == m.text.upper())
def select51(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 51
@bot.message_handler(func=lambda m:"52" == m.text.upper())
def select52(message):
    global acaanSelection, acaanFind, listening
    if listening == 1:
        acaanSelection = 1
        acaanFind = 52

@bot.callback_query_handler(func=lambda call:"1" == call.data)
def card1(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="A"
@bot.callback_query_handler(func=lambda call:"2" == call.data)
def card2(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="2"
@bot.callback_query_handler(func=lambda call:"3" == call.data)
def card3(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="3"
@bot.callback_query_handler(func=lambda call:"4" == call.data)
def card4(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="4"
@bot.callback_query_handler(func=lambda call:"5" == call.data)
def card5(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="5"
@bot.callback_query_handler(func=lambda call:"6" == call.data)
def card6(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="6"
@bot.callback_query_handler(func=lambda call:"7" == call.data)
def card7(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="7"
@bot.callback_query_handler(func=lambda call:"8" == call.data)
def card8(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="8"
@bot.callback_query_handler(func=lambda call:"9" == call.data)
def card9(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="9"
@bot.callback_query_handler(func=lambda call:"10" == call.data)
def card10(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="O"
@bot.callback_query_handler(func=lambda call:"11" == call.data)
def card11(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="J"
@bot.callback_query_handler(func=lambda call:"12" == call.data)
def card12(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="Q"
@bot.callback_query_handler(func=lambda call:"13" == call.data)
def card13(message):
   global acaanSelection, acaanNum
   acaanSelection=1
   acaanNum="K"

#turn the card
@bot.callback_query_handler(func=lambda call: "reveal" == call.data)
def revealSelection(message):
    global reveal
    reveal = True

keep_alive()
bot.polling()