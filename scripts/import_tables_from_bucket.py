from contextlib import contextmanager
import json
import logging
import os
import sys
import threading
import time
import traceback

from dotenv import load_dotenv
load_dotenv()

from googleapiclient.discovery import build

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class LoadingLine(threading.Thread):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.is_done_loading: threading.Event = threading.Event()

    def stop(self):
        self.is_done_loading.set()

    def run(self):
        def tick(tick_state: dict):
            MAX = 5
            MIN = 1
            i = tick_state['i'] + tick_state['delta']
            if i > MAX:
                tick_state['delta'] = -1
                return tick(tick_state)
            elif i < MIN:
                tick_state['delta'] = 1
                return tick(tick_state)
            tick_state['text'] = '.' * i + ' ' * (MAX - i)
            tick_state['i'] = i
            return tick_state
        tick_state = {
            'text': '.  ',
            'i': 1,
            'delta': 1
        }
        while self.is_done_loading.is_set() is False:
            print("Loading: " + tick_state['text'] + "\r", end='')
            tick_state = tick(tick_state)
            time.sleep(1)
        print('Loading: done')


@contextmanager
def loading_line():
    try:
        loading_thread = LoadingLine()
        loading_thread.start()
        yield None
    finally:
        loading_thread.stop()
        loading_thread.join()


def import_csv_data_to_table(table: str) -> dict:
    body = {
        "importContext": {
            "fileType": "CSV",
            "uri": f"gs://{os.getenv('GOOGLE_CLOUD_BUCKET_NAME', 'adpipe')}/{table}.csv",
            "database": 'production',
            "csvImportOptions":
            {
                "table": table,
                "escapeCharacter":  "5C",
                "quoteCharacter": "22",
                "fieldsTerminatedBy": "2C",
                "linesTerminatedBy": "0A"
            }
        }
    }
    service = build('sqladmin', 'v1')
    req = service.instances().import_(
        project=os.getenv('GOOGLE_CLOUD_PROJECT_NAME'),
        instance=os.getenv('GOOGLE_CLOUD_INSTANCE_NAME'),
        body=body
    )
    response = req.execute()
    return response

def monitor_task_until_complete(task: dict):
    service = build('sqladmin', 'v1')
    request = service.operations().get(
        project=os.getenv('GOOGLE_CLOUD_PROJECT_NAME'),
        operation=task['name']
    )
    
    with loading_line():
        while task['status'] in ('PENDING', 'RUNNING'):
            time.sleep(10)
            task = request.execute()

    return task

if __name__ == '__main__':
    for table in ('user_accounts', 'items', 'impressions', 'view_logs'):
        try:
            logging.info(f"Importing data to {table}")
            response: dict = import_csv_data_to_table(table)
            task = monitor_task_until_complete(response)
            if task['status'] == 'DONE':
                logging.info(f"Successfully imported data into table {table}")
            else:
                logging.error(f"Unsuccessful data import to {table}\n{json.dumps(task, indent=4)}")
        except Exception:
            logging.error(f"Error while queueing import operation for table '{table}'\n{traceback.format_exc()}")
