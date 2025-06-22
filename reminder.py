import asyncio
from bot import ApplicationBuilder, send_daily_reminder, TOKEN

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    await send_daily_reminder(app)

if __name__ == "__main__":
    asyncio.run(main())
