from dotenv import load_dotenv
import os
from typing import Final

load_dotenv()
TOKEN: Final = os.getenv("BOT_TOKEN")

print(TOKEN)  # بس علشان نتأكد إنه اتجاب صح
