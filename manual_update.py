import config
import requests
import json
from datetime import datetime


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_updates():
    url = config.URL + 'getUpdates'
    r = requests.get(url)
    write_json(r.json())
    return r.json()


if __name__ == '__main__':
    r = get_updates()
    if len(r['result']):
        r = r['result'][-1]
        timestamp = int(r['message']['date'])
        print(datetime.fromtimestamp(timestamp))
