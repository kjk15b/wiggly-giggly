import json
import requests
import datetime
import time

def get_master_record():
    f = open('master_record.json', 'r')
    master_record = json.load(f)
    f.close()
    return master_record

def check_for_expire_time(master_record : dict):
    now = datetime.datetime.now()
    updated_record = {}
    for ioc_id in master_record.keys():
        # FORMAT: "2023-01-20 18:50:31"
        # '%m-%d-%Y'
        first_seen_utc = datetime.datetime.strptime(master_record[ioc_id][0]['first_seen_utc'], '%Y-%m-%d %H:%M:%S')
        if now - first_seen_utc > datetime.timedelta(days=120):
            print('EXPIRED: {}'.format(master_record[ioc_id][0]['ioc_value']))
        else:
            # del doesn't work here since it breaks the keys
            updated_record[ioc_id] = master_record[ioc_id][0]

    return updated_record

def update_master_record(intel : dict):
    master_record = get_master_record()
    for ioc_id in intel.keys():
        if ioc_id not in master_record.keys():
            print('Adding: {} to master record...'.format(intel[ioc_id][0]['ioc_value']))
            master_record[ioc_id] = intel[ioc_id][0]
    master_record = check_for_expire_time(master_record)
    f = open('master_record.json', 'w')
    f.write(json.dumps(master_record, indent=3))
    f.close()

def get_threatfox_feed(endpoint : str):
    url = 'https://threatfox.abuse.ch/export/json/{}'.format(endpoint)
    req = requests.get(url)
    if req.status_code == 200:
        intel = json.loads(req.content)
        update_master_record(intel)



if __name__ == '__main__':
    ONE_DAY = 86400 # seconds in a day
    while True:
        get_threatfox_feed('recent/')
        time.sleep(ONE_DAY)