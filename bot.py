from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import pymysql
import os
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")

def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT")),
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sana DATETIME,
        turi VARCHAR(20),
        nomi VARCHAR(255),
        summa BIGINT
    )
    """)

    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Kirim-Chiqim bot tayyor.\n\nMisollar:\n gaz 120300\n savdo 1500000\n\nBuyruqlar:\n/balans\n/hisobot"
    )

async def balans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(SUM(summa),0) FROM transactions WHERE turi='kirim'")
    kirim = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(summa),0) FROM transactions WHERE turi='chiqim'")
    chiqim = cur.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"💰 Kirim: {kirim:,}\n💸 Chiqim: {chiqim:,}\n📊 Balans: {kirim-chiqim:,}"
    )

async def hisobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT nomi,turi,summa
        FROM transactions
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Ma'lumot yo'q.")
        return

    text = "📋 Oxirgi yozuvlar:\n\n"

    for nomi, turi, summa in rows:
        text += f"{turi.upper()} | {nomi} | {summa:,}\n"

    await update.message.reply_text(text)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    parts = msg.split()

    if len(parts) < 2:
        return

    nomi = " ".join(parts[:-1])

    try:
        summa = int(parts[-1].replace(".", "").replace(",", ""))
    except:
        return

    kirim_sozlar = [
        "savdo",
        "tushum",
        "kirim",
        "mijoz",
        "klient"
    ]

    turi = "chiqim"

    for k in kirim_sozlar:
        if k in nomi.lower():
            turi = "kirim"

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO transactions
        (sana,turi,nomi,summa)
        VALUES (%s,%s,%s,%s)
        """,
        (datetime.now(), turi, nomi, summa)
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Saqlandi\n\nTuri: {turi}\nNomi: {nomi}\nSumma: {summa:,}"
    )

init_db()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balans", balans))
app.add_handler(CommandHandler("hisobot", hisobot))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
