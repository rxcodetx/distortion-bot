import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image, ImageFilter, ImageOps
import io
import random

# Configuración con TU TOKEN (NO lo cambies aquí, lo pondremos en Render)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.getenv('PORT', 8443))

# Logs para detectar errores
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(name)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('🎨 ¡Hola! Envíame una imagen y la distorsionaré. ¡Prueba ya!')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('❓ Solo envíame una foto y verás la magia.')

def apply_random_distortion(img):
    """Aplica efectos aleatorios divertidos"""
    effects = [
        lambda i: i.filter(ImageFilter.GaussianBlur(random.randint(1, 3))),
        lambda i: i.rotate(random.randint(-30, 30), expand=True),
        lambda i: ImageOps.posterize(i, bits=random.randint(2, 4))),
        lambda i: ImageOps.colorize(i.convert('L'), "red", "blue"),
        lambda i: i.resize((i.width // 2, i.height)).resize((i.width, i.height)),
    ]
    # Aplicar 2 efectos aleatorios
    for _ in range(2):
        img = random.choice(effects)(img)
    return img

def handle_image(update: Update, context: CallbackContext):
    try:
        # Descargar imagen
        photo_file = update.message.photo[-1].get_file()
        img_data = io.BytesIO()
        photo_file.download(out=img_data)
        img_data.seek(0)
        
        # Procesar
        with Image.open(img_data) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            distorted_img = apply_random_distortion(img)
            
            # Enviar resultado
            output = io.BytesIO()
            distorted_img.save(output, format='JPEG')
            output.seek(0)
            update.message.reply_photo(photo=output, caption="¡Aquí está tu imagen distorsionada! 😜")
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("🔴 Error: ¿Me enviaste una imagen válida?")

def error(update: Update, context: CallbackContext):
    logger.error(f'Error en la actualización: {context.error}')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Comandos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    
    # Errores
    dp.add_error_handler(error)
    
    # Modo Render (webhook) o local (polling)
    if os.getenv('RENDER'):
        app_name = os.getenv('RENDER_APP_NAME')
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{app_name}.onrender.com/{TOKEN}"
        )
        updater.bot.set_webhook(f"https://{app_name}.onrender.com/{TOKEN}")
    else:
        updater.start_polling()
    
    updater.idle()

if name == 'main':
    main()