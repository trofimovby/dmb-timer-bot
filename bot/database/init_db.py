# init_db.py (в корне dmb-timer-bot)

from bot.database.models import Base
from bot.database.db import engine

Base.metadata.create_all(bind=engine)

import os
print("DATABASE_URL =", os.getenv("DATABASE_URL"))
