from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime as dt
from fuselink import totp
from json import loads, dumps
from sanic.response import json
from sanic import Sanic
from uuid import uuid1
from time import time
import asyncio


app = Sanic("FuseLink")

# 初始化 MongoDB 客户端和数据库
mongo_client = AsyncIOMotorClient("mongodb://localhost:27017/")
admin_log = mongo_client["FuseLink_Cache"][F"admin_log_{str(uuid1())[-12:]}"]
admin_read = mongo_client["FuseLink_Cache"][F"clients_read_{str(uuid1())[-12:]}"]
admin_write = mongo_client["FuseLink_Cache"][F"clients_write_{str(uuid1())[-12:]}"]
admin_device = mongo_client["FuseLink_Cache"][F"clients_device_{str(uuid1())[-12:]}"]


async def ws_connect(request):
    connect_data = {
        "utc": int(time()),
        "network": {
            "send": list(request.socket),
            "recv": list(request.socket)
            # "recv": [request.server_name, request.server_port]
        },
        "code": None
    }
    await admin_log.insert_one(connect_data.copy())
    return connect_data


async def ws_task(ws, connect_data):
    connect_swap = await ws.recv()
    try:
        connect_swap = loads(connect_swap)
        if (type(connect_swap) == dict and "@device" in connect_swap):
            await admin_write.insert_one(connect_swap.copy())
            connect_swap = None
            while not (connect_swap):
                connect_swap = await admin_device.find(dict(), {"_id": 0}).to_list(length=None)
                await asyncio.sleep(0.1)
            await admin_device.delete_many(dict())
        if ("code" in connect_swap):
            await admin_write.insert_one(connect_swap.copy())
            connect_swap = await admin_read.find_one_and_delete(dict(), {"_id": 0})
            print(connect_swap["code"]["status"])
            if(connect_swap["code"]["status"]):
                await ws.send(dumps(connect_swap, indent=4, ensure_ascii=False))
                connect_swap = await admin_read.find_one_and_delete(dict(), {"_id": 0})
            else:
                connect_swap = None
        if (connect_swap):
            await ws.send(dumps(connect_swap, indent=4, ensure_ascii=False))
        connect_swap = None
    except Exception as e:
        connect_data["code"] = {
            "message": connect_swap,
            "error": str(e)
        }
        await ws.send(dumps(connect_data, indent=4, ensure_ascii=False))


@app.websocket("/ws")
async def ws_handler(request, ws):
    """
    WebSocket 连接处理函数
    """
    connect_data = await ws_connect(request)
    # 直接在 handler 中构建并记录连接信息
    try:
        while True:
            await ws_task(ws, connect_data)
    except Exception as e:
        print(F"[{str(dt.now())[:-7]}] WebSocket error: {str(e)}")
    finally:
        print(F"[{str(dt.now())[:-7]}] Connection closed")


@app.get("/code")
async def code(request):
    code_data = {f1k: f1v[0] for f1k, f1v in request.args.items()}
    return json(totp(**code_data))


@app.get("/")
async def index(request):
    return json(None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, auto_reload=True)
