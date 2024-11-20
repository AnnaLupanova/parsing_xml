import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_report(date: str, total_revenue: float, top_products: str, categories: str):
    prompt = f"""
    Проанализируй данные о продажах за {date}:
    1. Общая выручка: {total_revenue}
    2. Топ-3 товара по продажам: {top_products}
    3. Распределение по категориям: {categories}

    Составь краткий аналитический отчет с выводами и рекомендациями.
    """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()
