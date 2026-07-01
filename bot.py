from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openpyxl import Workbook
import pymysql
import os

TOKEN = os.getenv("BOT_TOKEN")

def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", "3306"))
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nomi VARCHAR(255),
        summa BIGINT
    )
    """)

    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Kirim-Chiqim bot ishlayapti!\n\n"
        "Misollar:\n"
        "savdo 500000\n"
        "gaz 120000\n\n"
        "Buyruqlar:\n"
        "/balans\n"
        "/excel"
    )

async def balans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(SUM(summa),0) FROM transactions")
    jami = cur.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"💰 Jami summa: {jami:,} so'm"
    )

async def excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT nomi, summa FROM transactions")
    rows = cur.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Kirim-Chiqim"

    ws.append(["Nomi", "Summa"])

    for row in rows:
        ws.append(list(row))

    file_name = "kirim_chiqim.xlsx"
    wb.save(file_name)

    with open(file_name, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename="kirim_chiqim.xlsx"
        )
