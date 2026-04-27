import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.environ["TELEGRAM_TOKEN"]

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Enviame algo como: 100 USD a EUR")

async def convertir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().upper()
    partes = texto.split()

    if len(partes) != 4 or partes[2] != "A":
        await update.message.reply_text("Ejemplo: 100 USD a EUR")
        return

    try:
        monto = float(partes[0])
    except ValueError:
        await update.message.reply_text("El monto debe ser un numero.")
        return

    origen = partes[1]
    destino = partes[3]

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://v6.exchangerate-api.com/v6/" + os.environ["EXCHANGE_API_KEY"] + "/pair/" + origen + "/" + destino + "/" + str(monto),
                follow_redirects=True
            )

        if r.status_code != 200:
            await update.message.reply_text("Moneda no encontrada.")
            return

        data = r.json()
        resultado = data["conversion_result"]
        tasa = data["conversion_rate"]
        await update.message.reply_text(
            str(monto) + " " + origen + " = " + str(round(resultado, 2)) + " " + destino
        )

    except Exception as e:
        await update.message.reply_text("Excepcion: " + str(e))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", inicio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convertir))
app.run_polling(drop_pending_updates=True)
