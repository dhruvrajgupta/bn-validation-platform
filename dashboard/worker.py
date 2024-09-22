from celery import Celery
import time

app = Celery("worker", broker="pyamqp://bnv_rabbitmq")

@app.task
def TaskQueue(message):
    print("TaskQueue {0}".format(message))