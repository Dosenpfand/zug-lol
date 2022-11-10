import asyncio
import random
from datetime import datetime, timedelta

from app import crontab
from app.models import Price


@crontab.job(minute="*/5")
def update_oldest_prices(count: int = 10):
    asyncio.run(async_update(count))


async def async_update(count):
    min_age = datetime.utcnow() - timedelta(days=30)
    for i in range(count):
        wait = random.randint(1, 10)
        await asyncio.sleep(wait)
        price = Price.update_oldest(min_update_time=min_age)
        if not price:
            break
        print(price)
