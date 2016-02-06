# telegram-tellstick
Control TellStick devices via Telegram message app.

## How to use it
The program is started with this command:

python telegramtellstick.py *telegram_bot_token* *telegram_id_user1* *telegram_id_user2*

Example:
```
python telegramtellstick.py 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw 25643003 93927788
```

## Dependencies
[telepot] (https://github.com/nickoala/telepot) is used to interface the Telegram bot API.

[untangle] (https://github.com/stchris/untangle) is used for XML parsing.

[tellcore-py] (https://pypi.python.org/pypi/tellcore-py) is used for tellstick API calls.
