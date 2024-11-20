from celery import Celery
import requests
from utils import parse_and_save_sales_data
from database import AsyncSessionLocal
import os


celery = Celery('sales_analyzer',
                broker=os.getenv('CELERY_BROKER_URL'),
                backend=os.getenv('CELERY_BROKER_URL'))

@celery.task
def fetch_and_process_sales_data(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        db = AsyncSessionLocal()
        try:
            parse_and_save_sales_data(response.text, db)
        finally:
            db.close()
