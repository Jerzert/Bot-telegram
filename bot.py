import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
EXCHANGE_KEY = os.environ.get("EXCHANGE_KEY")

# Monedas soportadas (puedes agregar más)
MONEDAS_ALIAS = {
    "colones": "CRC", "colon": "CRC", "crc": "CRC",
    "dolares": "USD", "dolar": "USD", "usd": "USD",
    "euros": "EUR", "euro": "EUR", "eur": "EUR",
    "quetzales": "GTQ", "gtq": "GTQ",
    "pesos": "MXN", "mxn": "MXN",
    "reales": "BRL", "brl": "BRL",
}

def normalizar_moneda(texto):
    texto = texto.lower().strip()
    return MONEDAS_ALIAS.get(texto, texto.upper())

def convertir(monto, desde, hacia):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_KEY}/pair/{desde}/{hacia}/{monto}"
    r = requests.get(url, timeout=10)
    data = r.json()
    if data.get("result") == "success":
        return data["conversion_result"]
    return None

async def manejar_mensaje(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()

    # Detecta patrones: "100 USD a EUR" o "100 usd en colones"
    patron = r"([\d,.]+)\s+(\w+)\s+(?:a|en|to)\s+(\w+)"
    match = re.search(patron, texto, re.IGNORECASE)

    if not match:
        await update.message.reply_text(
            "Escríbeme así: *100 USD a CRC*\n"
            "o también: *50 euros a dolares*",
            parse_mode="Markdown"
        )
        return

    monto_str = match.group(1).replace(",", "")
    desde = normalizar_moneda(match.group(2))
    hacia = normalizar_moneda(match.group(3))

    try:
        monto = float(monto_str)
    except ValueError:
        await update.message.reply_text("No entendí el monto, intenta de nuevo.")
        return

    resultado = convertir(monto, desde, hacia)

    if resultado is None:
        await update.message.reply_text(f"No pude convertir {desde} → {hacia}. Verifica las monedas.")
        return

    await update.message.reply_text(
        f"💱 *{monto:,.2f} {desde}* = *{resultado:,.2f} {hacia}*",
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    print("Bot corriendo...")
    app.run_polling()