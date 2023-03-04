import asyncio
import random
from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Price


def update_oldest_prices(count: int = 10, min_age_days: int = 30) -> List["Price"]:
    return asyncio.run(async_update(count, min_age_days))


async def async_update(count: int = 10, min_age_days: int = 30) -> List["Price"]:
    from app.models import Price  # noqa

    min_age = datetime.utcnow() - timedelta(days=min_age_days)
    prices = []

    for i in range(count):
        wait = random.randint(1, 10)
        await asyncio.sleep(wait)
        price = Price.update_oldest(min_update_time=min_age)
        if not price:
            break
        prices.extend(price)

    return prices