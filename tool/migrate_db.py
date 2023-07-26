from sqlalchemy import create_engine, select
from app.db import BaseModel
import os


def migrate(url_from, url_to):
    engine_from = create_engine(url_from)
    engine_to = create_engine(url_to)

    with engine_from.connect() as conn_lite:
        with engine_to.connect() as conn_cloud:
            for table in BaseModel.metadata.sorted_tables:
                data = [dict(row) for row in conn_lite.execute(select(table.c))]
                conn_cloud.execute(table.insert().values(data))


if __name__ == "__main__":
    url_from = os.getenv("URL_FROM")
    url_to = os.getenv("URL_TO")
    migrate(url_from, url_to)
