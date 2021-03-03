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
   
# How to install:
   1) Download code as a .zip
   2) Extract .zip folder on your disk
   3) Install python (3.9 recommended)
   4) Install python pip; Tutorial on https://www.liquidweb.com/kb/install-pip-windows/
   5) Open CMD in bot root directory as an administrator
   6) Run this command: pip install -r requirements.txt
   
# How to run:
   1) Open metin2 clients and login
   2) Open run.bat (or just setup an link to a run.bat)
   3) values in GUI form are not so important besides screen setting
         - write position of bottom left corner of your screen (ex. 1920x1080 => 0x1080)
         - if you put 0 in PID, bot wont start for this client
   4) press start
   5) to stop the bot press stop or press * on your keyboard (bot window must be active)
