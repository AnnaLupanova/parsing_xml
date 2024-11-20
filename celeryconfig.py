from celery.schedules import crontab

beat_schedule = {
    'fetch-sales-data-every-day': {
        'task': 'tasks.fetch_and_process_sales_data',
        'schedule': crontab(minute=0, hour=0), 
        'args': ('http://example.com/sales_data.xml',),
    },
}