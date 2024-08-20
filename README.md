# 🎩cardgeneratorbot🃏

Welcome to Card Magic Bot! This Telegram bot is designed to help magicians and card enthusiasts master card stacks and perform incredible card magic tricks. Whether you're working on memorizing a card stack or preparing for your next magic performance, Card Magic Bot is here to assist!

## 🚀 Features

- 🎴 **Generate a Card** - Generates a random card from a deck, perfect for practicing or performing.
- ✨ **Selected Card** - Only works after a card has been selected by a participant. When used, it reveals the selected card. If no card has been selected, the bot will send humorous or unexpected "cards" instead!
- 🧠 **Memorize Stacks** - Helps you memorize famous card stacks (Mnemonica, Memorandum, DaOrtiz, Redford, Aronson) by sending a card and, after a 5-second pause, revealing its position in the stack.

## 🔗 Access the Bot

You can find and start using the Card Magic Bot on Telegram by clicking [here](https://t.me/randomcardgenerator_bot).

## 🌟 Usage

### 🎮 Commands

- **/start** - Start interacting with the bot, set up the default settings.
- **/stack** - Change the current card stack. You can switch between the following stacks: Mnemonica, Memorandum, DaOrtiz, Redford, Aronson.

#### 🧠 Memorize Stacks

These commands help you memorize famous card stacks by sending a card and, after 5 seconds, revealing its position in the stack:

- **/mnemonica** - Practice the Mnemonica stack.
- **/memorandum** - Practice the Memorandum stack.
- **/daortiz** - Practice the DaOrtiz stack.
- **/redford** - Practice the Redford stack.
- **/aronson** - Practice the Aronson stack.

#### 📸 View Complete Stacks

These commands send you a photo of the complete stack:

- **/mnemonica_stack** - View the Mnemonica stack.
- **/memorandum_stack** - View the Memorandum stack.
- **/daortiz_stack** - View the DaOrtiz stack.
- **/redford_stack** - View the Redford stack.
- **/aronson_stack** - View the Aronson stack.

#### 🎩 Expert Mode

- **/expert** - Turn hints off for expert-level practice.
- **/hints** - Turn hints on for guided practice.

### ⏰ Daily Card Selection

Every day at 2 AM, the bot will automatically select a random card to be the first selection of the day. 
When you use the **GENERATE CARD** button, the selected card will be revealed as the second card.

#### 🔄 Trick Repetition

You can press the **GENERATE CARD** and **SELECTED CARD** buttons up to 4 times each. 
After that, pressing **SELECTED CARD** will send a face-down card with a **TURN THE CARD** button.

Pressing **TURN THE CARD** will reveal the selected card. 
The next selection for repeating the trick will be the following card in the stack you’ve chosen (Mnemonica by default).

If HINTS are on, the bot will send you the new selection as the second card when pressing **GENERATE CARD**, 
otherwise, you’ll have to rely on your knowledge of the mnemonic stack.

## 🛠️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/mattallio/cardgeneratorbot.git
   cd quotebot
   ```
2. **Create a Telegram Bot**
   - Talk to [BotFather](https://telegram.me/BotFather) on Telegram.
   - Use the **/newbot** command to create your bot and get the API token.
3. **Configure Environment Variables**
   - Create a `.env` file in the root directory with the following content: `API_KEY=your-telegram-api-key`
5. **Run the bot**
   - Run the bot using docker:
     ```bash
     docker compose up --build
     ```
   - Use the **/start** command to begin interacting with the bot.

## 📝 License

This project is licensed under the [MIT LICENSE](LICENSE).

