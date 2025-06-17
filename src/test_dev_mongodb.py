
# DEMO_DATA = {
#     "utc": int(time()),
#     "verif": totp(str(uuid1())[-12:]),
#     "verif": {
#         "secret": str(uuid1())[-12:],
#         "code": totp(str(uuid1())[-12:])["res"]["code"],
#         "totp_debug": True
#     },
#     "network": {},
#     "code": {
#         "utc": {},
#         "exe": {},
#         "res": {}
#     }
# }

demo_server_data = {
    "utc": {},
    "verif": {},
    "network": {},
    "code": {
        "utc": {},
        "exe": {},
        "res": {}
    }
}


from pymongo import MongoClient
from time import time, sleep
from uuid import uuid1


mongo = MongoClient('mongodb://localhost:27017/')
client_log = mongo['FuseLink_Cache'][F"clientss_log_{str(uuid1())[-12:]}"]
client_read = mongo['FuseLink_Cache'][F"clients_read_{str(uuid1())[-12:]}"]
client_write = mongo['FuseLink_Cache'][F"clients_write_{str(uuid1())[-12:]}"]
client_device = mongo['FuseLink_Cache'][F"clients_device_{str(uuid1())[-12:]}"]

if False:
    client_write.delete_many(dict())
    client_write.update_one(
        {"@decive": None},
        {"$set": {"@device": None}},
        upsert=True
    )
    sleep(2)
    device = client_device.find(dict(), {"_id": 0})
    for f1 in device:
        print(f1)
else:
    client_write.delete_many(dict())
    client_write.update_one(
        {"code": {"uuid": str(uuid1())[-12:]}},
        {"$set": {"code": {"uuid": str(uuid1())[-12:], "time": time()}}},
        upsert=True
    )
