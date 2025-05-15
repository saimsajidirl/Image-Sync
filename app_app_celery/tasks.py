from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import redis
from PIL import Image
import logging
import threading
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
app = Celery('tasks', broker='redis://localhost:6379/0')

current_task_lock = threading.Lock()
current_tasks = {}

def hash_image(image_path):

    hash_md5 = hashlib.md5()
    filename = os.path.basename(image_path)
    hash_md5.update(filename.encode('utf-8'))

    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.task(bind=True)
def resize_image(self, image_path, output_size=(1920, 1080)):
    logger.info(f"Processing image: {image_path}")

    image_hash = hash_image(image_path)
    output_path = f"{image_hash}_resized.jpg"  # Use hash for output filename

    try:
        if redis_client.exists(image_hash):
            logger.info(f"Resized image already exists for: {image_path}")
            return redis_client.get(image_hash)

        img = Image.open(image_path)
        img = img.resize(output_size)
        img.save(output_path)

        redis_client.set(image_hash, output_path)
        logger.info(f"Image saved to: {output_path}")

        return output_path

    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        self.retry(exc=e)

def add_resize_task(image_path):
    global current_tasks
    image_hash = hash_image(image_path)

    with current_task_lock:
        if redis_client.exists(image_hash):
            existing_image_path = redis_client.get(image_hash)
            logger.info(f"Image already exists: {existing_image_path}")
            return existing_image_path

        if image_hash in current_tasks:
            logger.info(f"Task for {os.path.basename(image_path)} is already in progress. Ignoring the new task.")
            return current_tasks[image_hash]

        new_task = resize_image.delay(image_path)
        current_tasks[image_hash] = new_task.id

    return new_task
