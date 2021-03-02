# Metin2-Bot


Two bots were implemented:
- Bravery Cape Bot

   - Prototype for interacting with the game UI
   - Sends key strokes and mouse presses to the game to automatically farm monsters for experience
   - Mostly an intermediate step for the Metin Farm Bot (see below)
   
- Metin (Snowman) Farm Bot

   - Takes sreenshots of the game client and pre-processes them using HSV filters
   - Detects snowmen using a Haar feature-based Cascade Classifiers
   - Multi-threaded bot implementation as state machine to farm snowmen automatically
   - Remote monitoring through Telegram Bot implementation

   ![Demo GIF](https://github.com/philipp-kurz/Metin2-Bot/blob/main/demo/demo.gif "Demo GIF")
   
How to install and run:
   1)
