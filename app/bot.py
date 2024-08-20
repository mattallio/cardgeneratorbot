"""
Bot module
handles the bot initialization and commands
"""

import random
import time
from os import getenv, listdir
from os import path as ospath

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

STACKS = ["mnemonica", "memorandum", "daortiz", "redford", "aronson"]


def add_user(message):
    """
    add the user in the database and initializes its properties
    """

    if str(message.chat.id) not in db:
        db[str(message.chat.id)] = {}
        db[str(message.chat.id)]["front"] = 0
        db[str(message.chat.id)]["back"] = 0
        db[str(message.chat.id)]["reveal"] = False
        db[str(message.chat.id)]["stack"] = "mnemonica"
        db[str(message.chat.id)]["selection"] = 1


def count_folder(command_folder):
    """
    count the elements in a directory
    """

    dir_path = rf"{command_folder}"
    count = 0
    # Iterate directory
    for path in listdir(dir_path):
        # check if current path is a file
        if ospath.isfile(ospath.join(dir_path, path)):
            count += 1
    # print('File count:', count)
    return count


# finds the card in the photo and returnes its coordinates
def find_card(photo):
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
def apply_selection(card_coords: tuple, message):
    base = Image.open(r"Utilities/base.jpg")
    # base = base.rotate(270, expand=True)

    selection = Image.open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg")
    factor = 0.45
    selection = selection.resize(
        (round(selection.size[0] * factor), round(selection.size[1] * factor))
    )

    base.paste(selection, card_coords)
    try:
        base.save(r"Utilities/final.jpg")
        return 0
    except:
        return 1


def selection_of_day():
    """
    randomly pick the first selection of the day
    """

    selection = random.randint(1, 52)
    for user in db:
        db[user]["front"] = 0
        db[user]["back"] = 0
        db[user]["reveal"] = False
        db[user]["selection"] = selection
    print("Selection changed!!!")


def update_selection(message):
    """
    choose the following card in the stack as the selection
    """

    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")

    stack = None

    match db[str(message.chat.id)]["stack"]:
        case "mnemonica":
            stack = card2numbers.Mnemonica
        case "memorandum":
            stack = card2numbers.Memorandum
        case "daortiz":
            stack = card2numbers.Daortiz
        case "redford":
            stack = card2numbers.Redford
        case "aronson":
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
        count += 1
    if count > 52:
        count = 1
    db[str(message.chat.id)]["selection"] = count


def train_stack(message, stack):
    """
    send a random card
    after 5 seconds send its position in the selected stack
    """

    card = random.randint(1, 52)
    with open(rf"Cards/{card}.jpg", "rb") as f:
        photo = f.read()
        bot.send_photo(message.chat.id, photo)

    number = int(stack[card - 1])
    if number != 0:
        time.sleep(5)
    bot.send_message(message.chat.id, str(number))


def random_funny(message):
    """
    send a funny card
    """

    card = random.randint(1, count_folder("Funny"))
    with open(rf"Funny/{card}.jpg", "rb") as f:
        photo = f.read()
        bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=["start"])
def start(message):
    """
    initialize the user's info
    create the buttons
    """

    add_user(message)
    db[str(message.chat.id)]["front"] = 0
    db[str(message.chat.id)]["back"] = 0
    markup = ReplyKeyboardMarkup(row_width=2)
    generate = KeyboardButton("Generate Card")
    selected = KeyboardButton("Selected Card")
    markup.add(generate, selected)
    bot.send_message(message.chat.id, "Ok, here we go", reply_markup=markup)


@bot.message_handler(commands=["stack"])
def select_stack(message):
    """
    let the user choose their preferred stack
    """

    add_user(message)
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
def get_photo(message):
    downloaded_file = bot.download_file(
        bot.get_file(message.photo[-1].file_id).file_path
    )
    with open(r"Utilities/base.jpg", "wb") as new_file:
        new_file.write(downloaded_file)

    card = find_card(r"Utilities/base.jpg")
    if card is not None:
        modify = apply_selection(
            (card[0] + card[2] - 200, card[1] + card[3] - 300), message
        )
        if modify == 0:
            with open(r"Utilities/final.jpg", "rb") as f:
                photo = f.read()
                bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id, "Was this your card?")
            update_selection(message)
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


@bot.message_handler(commands=[f"{stack}_stack" for stack in STACKS])
def send_stack(message):
    """
    send the picture of the selected stack
    """

    add_user(message)

    stack = str(message.text).split("_", maxsplit=1)[0][1:]

    with open(rf"Utilities/{stack}.png", "rb") as f:
        photo = f.read()
        bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=STACKS)
def train(message):
    """
    train the user on the selected stack
    """

    add_user(message)
    card2numbers = pd.read_excel(r"Cards/0-card-to-number.xlsx")

    stack = None

    match message.text:
        case "/mnemonica":
            stack = card2numbers.Mnemonica
        case "/memorandum":
            stack = card2numbers.Memorandum
        case "/daortiz":
            stack = card2numbers.Daortiz
        case "/redford":
            stack = card2numbers.Redford
        case "/aronson":
            stack = card2numbers.Aronson

    if stack is not None:
        train_stack(message, stack)


@bot.message_handler(commands=["expert"])
def expert(message):
    """
    set the user as expert
    they won't receive hints anymore
    """

    markup = InlineKeyboardMarkup()
    sure = InlineKeyboardButton("I am sure", callback_data="sure")
    cancel = InlineKeyboardButton("Cancel", callback_data="cancel")
    markup.add(sure, cancel)
    bot.send_message(
        message.chat.id,
        'By clicking "I am sure" you will no longer get the hint of what the next card will be, are you sure you have memorized your selected stack? (you can always enable the hints by using the command /hints)',
        reply_markup=markup,
    )


@bot.message_handler(commands=["hints"])
def activate_hints(message):
    """
    save the user as not expert
    """

    del db[str(message.chat.id)]["expert"]
    bot.send_message(message.chat.id, "You've turned hints back on!")


@bot.callback_query_handler(func=lambda call: "sure" == call.data)
def disable_hints(message):
    """
    save the user as expert
    """

    db[str(message.from_user.id)]["expert"] = 1
    bot.send_message(message.from_user.id, "Changes have been saved!")


@bot.message_handler(func=lambda m: "GENERATE CARD" in m.text.upper())
def random_card(message):
    """
    send a random card
    if hints are active or first selection of the day send the seleciton
    """

    add_user(message)
    if db[str(message.chat.id)]["front"] != 1 or (
        "expert" in db[str(message.chat.id)] and db[str(message.chat.id)]["expert"] == 1
    ):
        db[str(message.chat.id)]["front"] += 1
        card = random.randint(1, 53)
        with open(rf"Cards/{card}.jpg", "rb") as f:
            photo = f.read()
            bot.send_photo(message.chat.id, photo)
    else:
        db[str(message.chat.id)]["front"] += 1
        with open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg", "rb") as f:
            photo = f.read()
            bot.send_photo(message.chat.id, photo)
        if (
            "expert" in db[str(message.chat.id)]
            and db[str(message.chat.id)]["expert"] == 0
        ):
            db[str(message.chat.id)]["expert"] = 1


@bot.message_handler(func=lambda m: "SELECTED CARD" in m.text.upper())
def selected_card(message):
    """
    send a funny card or the selected card
    """

    add_user(message)
    if db[str(message.chat.id)]["front"] < 4 or db[str(message.chat.id)]["back"] < 3:
        random_funny(message)
        db[str(message.chat.id)]["back"] += 1
    else:
        back = random.randint(1, count_folder("Backs") - 1)

        with open(rf"Backs/{back}.jpg", "rb") as f:
            photo = f.read()
            markup = ReplyKeyboardMarkup()
            markup.add(KeyboardButton("Turn the Card"))
            bot.send_message(message.chat.id, "Could it be?", reply_markup=markup)
            bot.send_photo(message.chat.id, photo)

        while db[str(message.chat.id)]["reveal"] is False:
            time.sleep(1)

        with open(rf"Cards/{db[str(message.chat.id)]['selection']}.jpg", "rb") as f:
            photo = f.read()
            bot.send_photo(message.chat.id, photo)
        db[str(message.chat.id)]["reveal"] = False
        update_selection(message)
        start(message)


@bot.message_handler(func=lambda m: "TURN THE CARD" in m.text.upper())
def reveal_selection(message):
    """
    make the bot reveal the selected card
    """

    db[str(message.from_user.id)]["reveal"] = True


@bot.callback_query_handler(func=lambda call: call.data in STACKS)
def set_stack(call):
    """
    set the stack as chosen by the user
    """

    stack = call.data
    db[str(call.from_user.id)]["stack"] = stack
    bot.send_message(call.from_user.id, "Setup completed!")


@bot.callback_query_handler(func=lambda call: "cancel" == call.data)
def stop_operation(message):
    """
    cancel the operation
    """

    bot.send_message(message.from_user.id, "Operation cancelled")
