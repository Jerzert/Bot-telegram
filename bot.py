import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["TELEGRAM_TOKEN"]

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
                "https://api.frankfurter.app/latest",
                params={"from": origen, "to": destino}
            )
        status = r.status_code
        texto_respuesta = r.text
        await update.message.reply_text("Status: " + str(status) + " Respuesta: " + texto_respuesta)

    except Exception as e:
        await update.message.reply_text("Excepcion: " + str(e))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convertir))
app.run_polling(drop_pending_updates=True)