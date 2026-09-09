from sqlalchemy import create_engine, text
from src.config import settings

engine = create_engine(settings.database_url)


def check_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("connection ok")
    except Exception as e:
        print(f"connection failed: {e}")


if __name__ == "__main__":
    check_connection()