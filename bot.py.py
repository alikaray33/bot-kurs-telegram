import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Konfigurasi Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Fungsi untuk mengambil kurs (basis USD)
def get_exchange_rates():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        print(f"Error fetching rates: {e}")
        return None

# Fungsi template konversi universal
async def convert_currency(update: Update, context: ContextTypes.DEFAULT_TYPE, base_curr: str):
    if not context.args:
        await update.message.reply_text(
            f"Format salah! Contoh penggunaan:\n`/{base_curr.lower()} 1000`", 
            parse_mode="Markdown"
        )
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text(f"Masukkan angka yang valid ya! Contoh: `/{base_curr.lower()} 1000`", parse_mode="Markdown")
        return

    rates = get_exchange_rates()
    if not rates:
        await update.message.reply_text("Gagal mengambil data kurs terbaru. Coba lagi nanti.")
        return

    try:
        base_rate = 1.0 if base_curr == "USD" else rates.get(base_curr, 0)
        if base_rate == 0:
            await update.message.reply_text("Mata uang tidak ditemukan dalam sistem kurs.")
            return

        # Konversi ke USD dulu sebagai perantara
        amount_in_usd = amount / base_rate

        # Hitung ke semua target
        val_usd = amount_in_usd
        val_idr = amount_in_usd * rates.get("IDR", 0)
        val_thb = amount_in_usd * rates.get("THB", 0)
        val_khr = amount_in_usd * rates.get("KHR", 0) # Riel Kamboja

        # Format pesan balasan
        message = (
            f"💱 **Konversi Mata Uang ({amount:,.2f} {base_curr})**\n\n"
            f"🇺🇸 USD: $ {val_usd:,.2f}\n"
            f"🇮🇩 IDR: Rp {val_idr:,.2f}\n"
            f"🇹🇭 THB: ฿ {val_thb:,.2f}\n"
            f"🇰🇭 KHR: ៛ {val_khr:,.0f}\n\n"
            f"_Rate berdasarkan kurs real-time._"
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        print(f"Calculation error: {e}")
        await update.message.reply_text("Terjadi kesalahan saat menghitung konversi.")

# Handler masing-masing command
async def cmd_thb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await convert_currency(update, context, "THB")

async def cmd_usd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await convert_currency(update, context, "USD")

async def cmd_idr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await convert_currency(update, context, "IDR")

async def cmd_riel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await convert_currency(update, context, "KHR")

if __name__ == '__main__':
    # MASUKKAN BOT TOKEN KAMU DI SINI (Ganti tulisan di dalam tanda petik)
    TOKEN = "8660251711:AAFNy8gmAhAKxL54L63FUAZnzxhWK7y1JDA"
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Daftarkan semua Command Handler
    app.add_handler(CommandHandler("thb", cmd_thb))
    app.add_handler(CommandHandler("usd", cmd_usd))
    app.add_handler(CommandHandler("idr", cmd_idr))
    app.add_handler(CommandHandler("riel", cmd_riel))

    print("Bot 4 Mata Uang sedang berjalan...")
    app.run_polling()