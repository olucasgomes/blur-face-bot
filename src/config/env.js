require('dotenv').config();

class Env {}

Env.TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN

module.exports = Env