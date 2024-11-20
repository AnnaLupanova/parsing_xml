import xml.etree.ElementTree as ET
from models import Product, Sale
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from collections import Counter


async def parse_and_save_sales_data(xml_data: str, db: AsyncSession):
    sales = parseXML(xml_data)
    for sale in sales:
        result = await db.execute(select(Sale).filter(Sale.date == sale.date.date()))
        sale_exists = result.scalars().first()
        if sale_exists:
            for item_product in sale.products:
                exists_product = await db.execute(select(Product)
                                                  .filter(Product.sale_id == sale_exists.id)
                                                  .filter(Product.name == item_product.name))
                exists_product = exists_product.scalars().first()
                if exists_product:
                    exists_product.price = item_product.price
                    exists_product.name = item_product.name
                    exists_product.quantity = item_product.quantity
                    exists_product.category = item_product.category
                else:
                    item_product.sale_id = sale_exists.id
                    item_product.sale = sale_exists
                    db.add(item_product)
        else:
            db.add(sale)
    await db.commit()


def parseXML(xml_data):
    tree = ET.fromstring(xml_data)
    root = tree.getroot()
    date = root.attrib["date"]
    products_list = []
    sales_list = []
    for product in root.find('products').findall('product'):
        elem = Product(
            name=product.find('name').text,
            quantity=int(product.find('quantity').text),
            price=float(product.find('price').text),
            category=product.find('category').text
        )
        products_list.append(elem)

    sale = Sale(date=datetime.strptime(date, '%Y-%m-%d'))
    sale.products = products_list
    sales_list.append(sale)
    return sales_list


async def get_sales_data_for_date(db: AsyncSession, target_date: date):
    result = await db.execute(select(Sale).filter(Sale.date == target_date))
    return result.scalars().first()


def get_products_metrics(products):
    total_revenue = 0
    product_sales = []
    category_sales = []
    category_revenue = {}

    for product in products:
        total_revenue += (product.quantity * product.price)
        product_sales.append((product.name, product.quantity))
        category_sales.append((product.category, product.quantity * product.price))

    sales_counter = Counter(dict(product_sales))
    top_3_products = sales_counter.most_common(3)
    for category, revenue in category_sales:
        if category not in category_revenue:
            category_revenue[category] = 0
        category_revenue[category] += revenue

    total_revenue_ = sum(category_revenue.values())

    category_distribution = {category: (revenue / total_revenue_) * 100 for category, revenue in
                             category_revenue.items()}

    return total_revenue, top_3_products, category_distribution
