"""
Main module
starts the bot
"""

import time
from threading import Thread

import schedule
from bot import bot, selectionOfDay

# initialization settings
TIME = "02:00"


# checks if it's time to run any scheduled activity
def schedule_checker():
    """
    check every second if a scheduled function needs to be executed
    """

    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    """
    start the bot
    """

    schedule.every().day.at(TIME).do(selectionOfDay)
    Thread(target=schedule_checker).start()
    bot.infinity_polling()


if __name__ == "__main__":
    main()
