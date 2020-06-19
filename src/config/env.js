require('dotenv').config();

class Env {}

Env.TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN
Env.PORT = process.env.PORT || 3000
Env.URL = process.env.URL || 'https://blur-face-bot.herokuapp.com'

module.exports = Env