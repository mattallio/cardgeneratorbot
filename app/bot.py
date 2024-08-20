"""
Bot module
handles the bot initialization and commands
"""

import random
import time
from os import getenv, listdir, path as ospath

import cv2
import imutils
import pandas as pd
import telebot
from PIL import Image
from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

db = {}

API_KEY = getenv("API_KEY")

if API_KEY is None:
    raise RuntimeError("API key not configured")

bot = telebot.TeleBot(API_KEY)


# adds the user in the database and initializes its properties
def addUser(message):
    if str(message.chat.id) not in db:
        db[str(message.chat.id)] = {}
        db[str(message.chat.id)]["front"] = 0
        db[str(message.chat.id)]["back"] = 0
        db[str(message.chat.id)]["reveal"] = False
        db[str(message.chat.id)]["stack"] = "mnemonica"
        db[str(message.chat.id)]["selection"] = 1


# counts the elements in a folder
def countFolder(commandFolder):
    dir_path = rf"{commandFolder}"
    count = 0
    # Iterate directory
    for path in listdir(dir_path):
        # check if current path is a file
        if ospath.isfile(ospath.join(dir_path, path)):
            count += 1
    # print('File count:', count)
    return count


# finds the card in the photo and returnes its coordinates
def findCard(photo):
    image = cv2.imread(photo)
    image = imutils.resize(image, width=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    threshold_min_area = 30000
    number_of_contours = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if area > threshold_min_area:
            cv2.drawContours(image, [c], 0, (36, 255, 12), 3)
            number_of_contours += 1
            x, y, w, h = cv2.boundingRect(c)
            if x == 0 and y == 0:
                continue
            if x == 0:
                x = int(y + h / 2)
            if y == 0:
                y = int(x + w / 2)
            return (x, y, w, h)

    return None


# applies the selection to the photo
def applySelection(cardCoords: tuple, message):
    base = Image.open(r"Utilities/base.jpg")
    # base = base.rotate(270, expand=True)

    selection = Image.open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg")
    factor = 0.45
    selection = selection.resize(
        (round(selection.size[0] * factor), round(selection.size[1] * factor))
    )

    base.paste(selection, cardCoords)
    try:
        base.save(r"Utilities/final.jpg")
        return 0
    except:
        return 1


# randomly picks a selection for the day
def selectionOfDay():
    selection = random.randint(1, 52)
    for user in db:
        db[user]["front"] = 0
        db[user]["back"] = 0
        db[user]["reveal"] = False
        db[user]["selection"] = selection
    print("Selection changed!!!")


def updateSelection(message):
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")
    stack = None
    if db[str(message.chat.id)]["stack"] == "mnemonica":
        stack = card2numbers.Mnemonica
    elif db[str(message.chat.id)]["stack"] == "memorandum":
        stack = card2numbers.Memorandum
    elif db[str(message.chat.id)]["stack"] == "daortiz":
        stack = card2numbers.Daortiz
    elif db[str(message.chat.id)]["stack"] == "redford":
        stack = card2numbers.Redford
    elif db[str(message.chat.id)]["stack"] == "Aroson":
        stack = card2numbers.Aronson

    if stack is None:
        return

    number = int(stack[db[str(message.chat.id)]["selection"] - 1]) + 1
    if number > 52:
        number = 1
    count = 1
    for el in stack:
        if el == number:
            break
        else:
            count += 1
    if count > 52:
        count = 1
    db[str(message.chat.id)]["selection"] = count


# helps in memorizing the preferred stack
def trainStack(message, stack):
    card = random.randint(1, 52)
    photo = open(rf"Cards/{card}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()
    number = int(stack[card - 1])
    if number != 0:
        time.sleep(5)
    bot.send_message(message.chat.id, str(number))


# sends a funny card
def randomFunny(message):
    randomCard = random.randint(1, countFolder("Funny"))
    photo = open(rf"Funny/{randomCard}.jpg", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()


# the bot welcomes the user
@bot.message_handler(commands=["start"])
def start(message):
    addUser(message)
    db[str(message.chat.id)]["front"] = 0
    db[str(message.chat.id)]["back"] = 0
    markup = ReplyKeyboardMarkup(row_width=2)
    generate = KeyboardButton("Generate Card")
    selected = KeyboardButton("Selected Card")
    markup.add(generate, selected)
    bot.send_message(message.chat.id, "Ok, here we go", reply_markup=markup)


# sets the preferred stack for the selection
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
    bot.send_message(
        message.chat.id, "Select your preferred stack:", reply_markup=markup
    )


# modifies the user's photo with the selection card
@bot.message_handler(content_types=["photo"])
def getPhoto(message):
    downloaded_file = bot.download_file(
        bot.get_file(message.photo[-1].file_id).file_path
    )
    with open(r"Utilities/base.jpg", "wb") as new_file:
        new_file.write(downloaded_file)

    card = findCard(r"Utilities/base.jpg")
    if card != None:
        modify = applySelection(
            (card[0] + card[2] - 200, card[1] + card[3] - 300), message
        )
        if modify == 0:
            photo = open(r"Utilities/final.jpg", "rb")
            bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id, "Was this your card?")
            photo.close()
            updateSelection(message)
            start(message)
        else:
            bot.send_message(
                message.chat.id,
                "Sorry I can't see very well, try to send another image",
            )
            start(message)
    else:
        bot.send_message(
            message.chat.id, "Sorry I can't see very well, try to send another image"
        )
        start(message)


# sends the selected stack list
@bot.message_handler(commands=["memorandum_stack"])
def sendMemorandum(message):
    addUser(message)
    photo = open(r"Utilities/memorandum.png", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()


@bot.message_handler(commands=["mnemonica_stack"])
def sendMnemonica(message):
    addUser(message)
    photo = open(r"Utilities/mnemonica.png", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()


@bot.message_handler(commands=["daortiz_stack"])
def sendDaortiz(message):
    addUser(message)
    photo = open(r"Utilities/daortiz.png", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()


@bot.message_handler(commands=["redford_stack"])
def sendRedford(message):
    addUser(message)
    photo = open(r"Utilities/redford.png", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()


@bot.message_handler(commands=["aronson_stack"])
def sendAronson(message):
    addUser(message)
    photo = open(r"Utilities/aronson.png", "rb")
    bot.send_photo(message.chat.id, photo)
    photo.close()


# commands to memorize the selected stack
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


# command to disable the hints
@bot.message_handler(commands=["expert"])
def expert(message):
    markup = InlineKeyboardMarkup()
    sure = InlineKeyboardButton("I am sure", callback_data="sure")
    cancel = InlineKeyboardButton("Cancel", callback_data="cancel")
    markup.add(sure, cancel)
    bot.send_message(
        message.chat.id,
        'By clicking "I am sure" you will no longer get the hint of what the next card will be, are you sure you have memorized your selected stack? (you can always enable the hints by using the command /hints)',
        reply_markup=markup,
    )


# command to enable hints
@bot.message_handler(commands=["hints"])
def activateHints(message):
    del db[str(message.chat.id)]["expert"]
    bot.send_message(message.chat.id, "You've turned hints back on!")


# the bot sends a random card or tells the performer the card of the day
@bot.message_handler(func=lambda m: "GENERATE CARD" in m.text.upper())
def randomCard(message):
    addUser(message)
    if db[str(message.chat.id)]["front"] != 1 or (
        "expert" in db[str(message.chat.id)] and db[str(message.chat.id)]["expert"] == 1
    ):
        db[str(message.chat.id)]["front"] += 1
        card = random.randint(1, 53)
        photo = open(rf"Cards/{card}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
    else:
        db[str(message.chat.id)]["front"] += 1
        photo = open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
        if (
            "expert" in db[str(message.chat.id)]
            and db[str(message.chat.id)]["expert"] == 0
        ):
            db[str(message.chat.id)]["expert"] = 1


# button to reveal the selected card
@bot.message_handler(func=lambda m: "SELECTED CARD" in m.text.upper())
def selectedCard(message):
    addUser(message)
    if db[str(message.chat.id)]["front"] < 4 or db[str(message.chat.id)]["back"] < 3:
        randomFunny(message)
        db[str(message.chat.id)]["back"] += 1
    else:
        back = random.randint(1, countFolder("Backs") - 1)
        photo = open(rf"Backs/{back}.jpg", "rb")
        markup = ReplyKeyboardMarkup()
        markup.add(KeyboardButton("Turn the Card"))
        bot.send_message(message.chat.id, "Could it be?", reply_markup=markup)
        bot.send_photo(message.chat.id, photo)
        photo.close()
        while db[str(message.chat.id)]["reveal"] == False:
            time.sleep(1)
        photo = open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg", "rb")
        bot.send_photo(message.chat.id, photo)
        photo.close()
        db[str(message.chat.id)]["reveal"] = False
        updateSelection(message)
        start(message)


# reveals the card when the button is pressed
@bot.message_handler(func=lambda m: "TURN THE CARD" in m.text.upper())
def revealSelection(message):
    db[str(message.from_user.id)]["reveal"] = True


# sets the stack preference of the user
@bot.callback_query_handler(func=lambda call: "mnemonica" == call.data)
def setMnemonica(message):
    db[str(message.from_user.id)]["stack"] = "mnemonica"
    bot.send_message(message.from_user.id, "Setup completed!")


@bot.callback_query_handler(func=lambda call: "memorandum" == call.data)
def setMemorandum(message):
    db[str(message.from_user.id)]["stack"] = "memorandum"
    bot.send_message(message.from_user.id, "Setup completed!")


@bot.callback_query_handler(func=lambda call: "daortiz" == call.data)
def setDaortiz(message):
    db[str(message.from_user.id)]["stack"] = "daortiz"
    bot.send_message(message.from_user.id, "Setup completed!")


@bot.callback_query_handler(func=lambda call: "redford" == call.data)
def setRedford(message):
    db[str(message.from_user.id)]["stack"] = "redford"
    bot.send_message(message.from_user.id, "Setup completed!")


@bot.callback_query_handler(func=lambda call: "aronson" == call.data)
def setAronson(message):
    db[str(message.from_user.id)]["stack"] = "aronson"
    bot.send_message(message.from_user.id, "Setup completed!")


# saves the user changes
@bot.callback_query_handler(func=lambda call: "sure" == call.data)
def disableHints(message):
    db[str(message.from_user.id)]["expert"] = 1
    bot.send_message(message.from_user.id, "Changes have been saved!")


@bot.callback_query_handler(func=lambda call: "cancel" == call.data)
def cancel(message):
    bot.send_message(message.from_user.id, "Operation cancelled")
