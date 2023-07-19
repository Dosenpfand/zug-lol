from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta

db = SQLAlchemy()
# Needed for mypy
BaseModel: DeclarativeMeta = db.Model
