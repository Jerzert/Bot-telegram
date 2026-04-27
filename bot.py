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

Monedas soportadas: USD, EUR, CRC, GBP, JPY, MXN, COP, BRL, entre otras.
"""

async def convertir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().upper()
    partes = texto.split()

    if len(partes) != 4 or partes[2] != "A":
        await update.message.reply_text("No entendí. Ejemplo: 100 USD a EUR\n" + AYUDA)
        return

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://api.frankfurter.app/latest",
                params={"from": origen, "to": destino}
            )
            
        if r.status_code != 200:
            await update.message.reply_text(f"API respondió {r.status_code}: {r.text}")
            return

        data = r.json()

    origen = partes[1]
    destino = partes[3]

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://api.frankfurter.app/latest",
                params={"from": origen, "to": destino}
            )
            data = r.json()

        if "rates" not in data:
            await update.message.reply_text(f"No encontré la moneda {origen} o {destino}. Verificá el código.")
            return

        tasa = data["rates"][destino]
        resultado = monto * tasa
        await update.message.reply_text(
            f"{monto:,.2f} {origen} = {resultado:,.2f} {destino}\n(Tasa: 1 {origen} = {tasa} {destino})"
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Soy un bot de conversión de monedas.\n" + AYUDA)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("start"), inicio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convertir))

app.run_polling()
