from multiprocessing.pool import ThreadPool
import logging
import os
import sys
import threading

from dotenv import load_dotenv
load_dotenv()

from google.cloud import storage
import google.cloud.exceptions as cloud_exc

DATA_PATH = os.path.abspath("data")
table_path = os.path.join(DATA_PATH, "tables")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def get_bucket(client: storage.Client) -> storage.Bucket:
    bucket_name = os.getenv('GOOGLE_CLOUD_BUCKET_NAME', 'adpipe')
    try:
        bucket = client.get_bucket(bucket_name)
    except cloud_exc.NotFound:
        logging.info(f"Creating Google Cloud bucket '{bucket_name}'")
        client.create_bucket(bucket_name)
        bucket = client.get_bucket(bucket_name)
    return bucket

def upload_file(src: str, bucket: storage.Bucket):
    logstring = f"[{threading.current_thread().name}] {{message}}"
    logging.info(logstring.format(message=f"Uploading {src} to bucket '{bucket.name}'"))
    fn = os.path.basename(src)
    try:
        blob: storage.Blob = bucket.blob(fn)
    except cloud_exc.exceptions.AlreadyExists:
        logging.warning(logstring.format(message=f"Overwriting blob {fn}"))
        blob = bucket.get_blob(fn)
    blob.upload_from_filename(filename=src, num_retries=3, timeout=3600)

def upload_table_to_bucket(table_fn: str, bucket: storage.Bucket):
    fp: str = os.path.join(table_path, table_fn)
    upload_file(fp, bucket)

def infinite_single_value_generator(value):
    while True:
        yield value

if __name__ == '__main__':
    logging.info("Connecting to Google Cloud Storage")
    client = storage.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT_NAME'))
    bucket = get_bucket(client)
    
    table_filenames = ('user_accounts.csv', 'items.csv', 'impressions.csv', 'view_logs.csv')

    with ThreadPool(processes=4) as pool:
        logging.info("Uploading files")
        pool.starmap(upload_table_to_bucket, zip(table_filenames, infinite_single_value_generator(bucket)))
    