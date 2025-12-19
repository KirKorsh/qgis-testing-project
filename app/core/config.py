import os
from sqlalchemy import URL
from dotenv import load_dotenv 

load_dotenv()

def get_database_url():

    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "gis_test")
    ).render_as_string(hide_password=False)

DATABASE_URL = get_database_url()