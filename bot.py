from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
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

```
cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nomi VARCHAR(255),
    summa BIGINT
)
""")

conn.commit()
conn.close()
```

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"✅ Kirim-Chiqim bot ishlayapti!\n\n"
"Misol:\n"
"savdo 500000\n"
"gaz 120000\n\n"
"Buyruqlar:\n"
"/balans"
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

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
msg = update.message.text.strip()

parts = msg.split()

if len(parts) < 2:
    return

nomi = " ".join(parts[:-1])

try:
    summa = int(parts[-1].replace(",", ""))
except:
    await update.message.reply_text("❌ Summa noto'g'ri.")
    return

conn = get_db()
cur = conn.cursor()

cur.execute(
    "INSERT INTO transactions (nomi, summa) VALUES (%s, %s)",
    (nomi, summa)
)

conn.commit()
conn.close()

await update.message.reply_text(
    f"✅ Saqlandi\n{nomi} - {summa:,} so'm"
)

init_db()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balans", balans))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("✅ Bot ishga tushdi")

app.run_polling()



