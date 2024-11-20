from fastapi import FastAPI, Depends, HTTPException, status
import utils
from database import engine, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from models import *
from service import generate_report
from tasks import fetch_and_process_sales_data


app = FastAPI()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.on_event('startup')
async def startup():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)


@app.get("/generate_report/")
async def generate_report(target_date: date, db: AsyncSession = Depends(get_db)):
    sale = await utils.get_sales_data_for_date(db, target_date)
    if not sale:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sales data found for the given date")
    products = sale.products
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products data found for the given date")

    total_revenue, top_products, category_distribution = utils.get_products_metrics(products)
    report = generate_report(str(target_date), total_revenue, top_products, category_distribution)
    return {"report": report}


@app.get("/process_sales/")
async def process_sales(url: str):
    fetch_and_process_sales_data.apply_async(args=[url])
    return {"message": "Sales data processing started"}