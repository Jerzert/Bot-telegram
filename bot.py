import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["TELEGRAM_TOKEN"]

AYUDA = """
Enviame un mensaje así:
  100 USD a EUR
  50 EUR a CRC
  200 CRC a USD
"""

async def convertir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().upper()
    partes = texto.split()

    if len(partes) != 4 or partes[2] != "A":
        await update.message.reply_text("No entendí. Ejemplo: 100 USD a EUR")
        return

    try:
        monto = float(partes[0])
    except ValueError:
        await update.message.reply_text("El monto debe ser un número.")
        return

    origen = partes[1]
    destino = partes[3]

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": origen, "to": destino}
            )

        await update.message.reply_text(f"Status: {r.status_code}\nRespuesta: {r.text}")

    except Exception as e:
        await update.message.reply_text(f"Excepción: {type(e).__name__}: {str(e)}")

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Soy un bot de conversión de monedas.\n" + AYUDA)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convertir))

app.run_polling()
