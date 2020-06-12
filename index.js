const fs = require('fs')
const path = require('path')
const { spawn } = require('child_process')

const { Telegraf } = require('telegraf')
const axios = require('axios')

const { TELEGRAM_BOT_TOKEN } = require('./src/config/env')

const resolvePath = (file) => path.resolve(__dirname, file)

const bot = new Telegraf(TELEGRAM_BOT_TOKEN)

bot.command(['start', 'about'], (ctx) => {
  return ctx.replyWithMarkdown(`
*BlurFace*
👤 Developer: Lucas Gomes
📕 /help
`)
})

bot.command('help', (ctx) => {
  return ctx.replyWithMarkdown(`
*Help*!
Need help? No problem.

You can send me photos and videos files and I'll fuck them up for you.
`)
})

bot.on('message', async ctx => {
  let file
  let fileType

  if (!!ctx.update.message.photo) {
    const files = ctx.update.message.photo
    file = files.slice(-1)[0]
    fileType = 'jpg'
  } else if (!!ctx.update.message.document) {
    file = ctx.update.message.document
    fileType = file.mime_type.split('/')[1]
  } else if (!!ctx.update.message.video) {
    file = ctx.update.message.video
    fileType = 'mp4'
  }

  if (file) {
    const { file_id: fileId } = file
    
    let url
    try {
      url = await ctx.telegram.getFileLink(fileId)
    } catch (err) {
      console.error('error getting file id from telegram: [%o]', err)
    }
  
    try {
      const response = await axios({ url, responseType: 'stream' })
      const fileName = `${ctx.update.message.from.id}_${new Date().toISOString()}.${fileType}`
      const filePath = resolvePath(`./files/${fileName}`)
      response.data.pipe(fs.createWriteStream(filePath))
        .on('finish', () => {
          console.log({ fileType })
          if (fileType === 'jpg') {
            const pythonProcess = spawn('python3', ["src/blur_image/blur_image.py", "--image", filePath]);
            pythonProcess.stdout.on("data", data =>{
              ctx.replyWithPhoto({ source: resolvePath(`./processed_files/${fileName}`) })
            })
          } else if (fileType === 'mp4') {
            const pythonProcess = spawn('python3', ["src/blur_image/blur_image_video.py", "--image", filePath]);
            pythonProcess.stdout.on("data", data =>{
              ctx.replyWithVideo({ source: resolvePath(`./processed_files/${fileName}`) })
            })
          }
        })
        .on('error', e => console.log('An error has occured'))
    } catch (err) {
      console.error('error getting file from telegram: [%o]', err)
    }

    return ctx.reply('file received succesfully')
  }
});

bot.launch()