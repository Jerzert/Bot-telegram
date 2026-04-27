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
                "

