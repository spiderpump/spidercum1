import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.ext import JobQueue

# Función para obtener las 5 monedas tendencia (API de CoinGecko)
def get_top_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'percent_change_24h',  # Ordenar por cambio en 24h
        'per_page': 5,
        'page': 1
    }
    response = requests.get(url, params=params)
    data = response.json()

    top_coins_message = ""
    for idx, coin in enumerate(data, 1):
        name = coin['name']
        symbol = coin['symbol']
        price = coin['current_price']
        change_24h = coin['price_change_percentage_24h']

        top_coins_message += f"{idx}. {name} ({symbol}): ${price} | Cambio 24h: {change_24h}%\n"

    return top_coins_message

# Función para obtener el precio de Solana
def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data['solana']['usd']

# Función para obtener el precio de Flork
def get_flork_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=flork-cto&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data['flork-cto']['usd']

# Función para enviar mensaje al chat de Telegram
async def send_message(message, chat_id):
    bot = Bot(token="8054720195:AAHtRd-nqS-HXD52y0TntriKNIKVJ5Rv5ho")  # Token del bot
    await bot.send_message(chat_id=chat_id, text=message)

# Comando /start
async def start(update, context):
    chat_id = update.message.chat_id
    print(f"Mensaje recibido de chat ID: {chat_id}")  # Muestra el chat ID en la consola
    await update.message.reply_text(f"¡Hola! Tu chat ID es: {chat_id}\nAhora recibirás actualizaciones del precio de Solana y Flork.")

# Comando /top
async def top(update, context):
    chat_id = update.message.chat_id
    top_coins_message = get_top_coins()  # Obtiene las 5 monedas tendencia
    await send_message(f"Las 5 monedas tendencia:\n{top_coins_message}", chat_id)

# Comando /sol para obtener el precio de Solana
async def sol(update, context):
    chat_id = -1002492728608  # Chat ID proporcionado
    price = get_sol_price()  # Obtiene el precio de Solana
    await send_message(f"El precio actual de Solana es: ${price}", chat_id)  # Enviar mensaje al chat específico

# Comando /flork para obtener el precio de Flork
async def flork(update, context):
    chat_id = -1002492728608  # Chat ID proporcionado
    price = get_flork_price()  # Obtiene el precio de Flork
    await send_message(f"El precio actual de Flork es: ${price}", chat_id)  # Enviar mensaje al chat específico

# Función que se ejecuta cada 20 minutos para enviar el precio de las monedas
async def send_periodic_prices(context: CallbackContext):
    chat_id = -1002492728608  # Chat ID proporcionado
    sol_price = get_sol_price()
    flork_price = get_flork_price()
    message = (f"Actualización de precios:\n"
               f"Solana: ${sol_price}\n"
               f"Flork: ${flork_price}")
    await send_message(message, chat_id)

# Función para iniciar el bot
def main():
    # Crear la aplicación y los manejadores de comandos
    application = Application.builder().token("8054720195:AAHtRd-nqS-HXD52y0TntriKNIKVJ5Rv5ho").build()

    # Añadir los manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sol", sol))
    application.add_handler(CommandHandler("flork", flork))
    application.add_handler(CommandHandler("top", top))  # Agregar comando /top

    # Crear el JobQueue para enviar los precios cada 20 minutos
    job_queue = application.job_queue
    job_queue.run_repeating(send_periodic_prices, interval=1200, first=0)  # 1200 segundos = 20 minutos

    # Iniciar el bot sin usar asyncio.run()
    application.run_polling()

# Si el script se ejecuta directamente, ejecutamos la función main
if __name__ == "__main__":
    main()