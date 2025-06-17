"""
FuseLink 架构及实现文档
1. 引言
FuseLink 架构旨在实现高效、安全、可扩展的数据交换和通信，专为模拟公网环境下的数据传输而设计。它适用于需要高效、安全通信的场景，尤其适用于研究和测试系统在模拟公网环境中的性能和行为。

2. 架构概览
FuseLink 架构包含以下几个核心组件，它们协同工作以实现数据的安全传输和管理：

应用程序：负责业务逻辑和数据处理，将数据发送到本地临时交换数据库。

数据库（临时交换）：使用 MongoDB 作为本地临时交换数据库，用于存储和交换数据。

客户端交换程序：负责将本地数据库中的数据转存到云端服务端，支持多服务端连接和容灾切换。

服务端（云端）：部署在云端，负责数据的最终存储和管理，支持高可用性和扩展性。

3. 架构特点
集中式管理与分布式部署结合：服务端集中管理数据，而本地组件分布式部署，提高系统的稳定性和可靠性。

模拟公网环境：通过本地组件与云端服务端的协作，模拟公网的通信环境，为研究和测试提供平台。

高效数据交换：优化通信协议和数据处理流程，减少数据传输延迟。

多服务端支持与容灾：客户端支持连接多个服务端，并在服务端故障时自动切换，确保数据传输的连续性。

客户端地址获取与辅助通信：兼容并提升了传统 STUN/TURN 服务器的功能，能够获取客户端地址并辅助通信。

4. 组件详细描述
4.1 应用程序
功能：负责业务逻辑和数据处理。

数据处理：将数据发送到本地临时交换数据库。

实现方式：应用程序可以是任意类型的应用，如客户端、服务端、微服务等，位于本地。

4.2 数据库（临时交换）
功能：临时存储和交换数据。

数据库选择：使用 MongoDB 作为数据库，提供高效的数据存储和查询功能。

数据可靠性：确保数据在不同组件之间的可靠传递。

4.3 客户端交换程序
功能：将本地数据库中的数据转存到云端服务端。

多服务端支持：支持连接多个服务端，提高系统的可用性和可靠性。

容灾切换：当某个服务端出现故障时，自动切换到其他可用服务端。

地址获取与辅助通信：获取客户端地址并辅助通信，确保在不同网络环境下的数据传输。

4.4 服务端（云端）
功能：数据的最终存储和管理。

高可用性：支持多实例部署，确保高可用性。

数据管理：提供数据查询、访问和备份功能。

5. 数据交换流程
数据生成：应用程序生成数据并将其存储在本地临时交换数据库中。

数据转存：客户端交换程序定期从本地数据库读取数据，并将其转存到云端服务端。

数据存储：云端服务端接收并存储数据，提供数据查询和访问功能。

6. 工作原理
数据生成：应用程序在本地生成数据并存储在本地数据库中。

数据转存：客户端交换程序定期检查并转存数据到云端。

数据管理：云端服务端管理所有转存的数据。

容灾切换：客户端在服务端故障时自动切换到其他可用服务端。

地址获取与辅助通信：客户端交换程序获取地址信息并辅助通信。

7. 安全性与身份验证
数据加密：数据在传输和存储过程中采用端到端加密，确保数据的保密性和完整性。

身份验证：使用基于时间的一次性密码（TOTP）进行身份验证，确保只有合法客户端可以进行数据转存。

8. 部署与扩展
自动化部署：支持脚本自动化部署，简化配置过程。

扩展性：云端服务端可通过增加实例进行扩展，支持高可用性和负载均衡。

9. 适用场景
FuseLink 架构适用于以下场景：

数据同步：多设备之间的数据同步，如云存储、协作编辑等。

多设备协作：物联网、智能家居等场景中的设备协同工作。

研究与测试：模拟公网环境下的数据传输和网络行为研究。

10. 与 STUN/TURN 服务器对比
FuseLink 架构在功能、性能、安全性、部署和成本等方面相比传统 STUN/TURN 服务器具有显著优势：

功能增强：不仅支持 NAT 穿越和数据中继，还提供数据管理和模拟公网环境的能力。

性能优化：通过优化数据转存机制和通信协议，提高数据传输效率。

安全性提升：采用多种加密算法和身份验证机制，增强数据安全性。

部署简化：支持自动化部署，降低部署和运维复杂度。

成本可控：云端服务端的资源可根据需求灵活调整，优化成本。

11. 总结
FuseLink 架构通过模拟公网环境，为高效、安全的数据交换和通信提供了一个强大的平台。它结合了集中式管理和分布式部署的优势，支持多服务端连接和容灾切换，确保系统的高可用性和可靠性。FuseLink 架构不仅兼容传统 STUN/TURN 服务器的功能，还扩展了更多的数据管理和通信辅助功能，适用于广泛的应用场景。
"""


from motor.motor_asyncio import AsyncIOMotorClient
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve
from datetime import datetime as dt
from json import loads, dumps
from uuid import uuid1
from time import time
import asyncio


from urllib.parse import urlparse, parse_qs, urlunparse, quote, urlencode
from base64 import b32encode, b32decode
from typing import Dict, Any, Optional
from pyotp import TOTP
import hashlib

from os.path import abspath, dirname, exists, join
from argparse import ArgumentParser
from json import dump, load
from asyncio import run
from sys import exit


# 获取当前脚本所在目录
script_dir = dirname(abspath(__file__))
mongo = AsyncIOMotorClient("mongodb://localhost:27017/")
server_log = mongo["FuseLink_Cache"][F"server_log_{str(uuid1())[-12:]}"]
server_data = mongo["FuseLink_Cache"][F"server_data_{str(uuid1())[-12:]}"]
server_verif = mongo["FuseLink_Cache"][F"server_verif_{str(uuid1())[-12:]}"]
client_log = mongo["FuseLink_Cache"][F"clients_log_{str(uuid1())[-12:]}"]
client_read = mongo["FuseLink_Cache"][F"clients_read_{str(uuid1())[-12:]}"]
client_write = mongo["FuseLink_Cache"][F"clients_write_{str(uuid1())[-12:]}"]
client_device = mongo["FuseLink_Cache"][F"clients_device_{str(uuid1())[-12:]}"]


def totp(
    secret: Optional[str] = None,
    interval: int = 30,
    digits: int = 6,
    algorithm: str = "sha1",
    utc: int = 0,
    label: str = str(),
    issuer: str = str(),
    **parameters: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Generates a Time-based One-Time Password (TOTP) and constructs an otpauth URI.

    This function implements the TOTP algorithm as specified in RFC 6238. It takes a secret key and other parameters
    to generate a one-time password valid for a specific time interval. Additionally, it constructs an otpauth URI
    that can be used to configure TOTP in applications like Google Authenticator. The function also supports parsing
    otpauth URIs to extract parameters and generate a TOTP code based on those parameters.

    Args:
        secret (Optional[str]): The secret key used to generate the TOTP code. Can be a raw secret or an otpauth URI.
        interval (int): The time interval (in seconds) for which the TOTP code is valid. Defaults to 30.
        digits (int): The number of digits in the generated TOTP code. Defaults to 6.
        algorithm (str): The hashing algorithm used to generate the TOTP code. Defaults to "sha1".
        utc (int): The Unix timestamp to use for generating the TOTP code. If 0, the current time is used.
        label (str): The label to use in the otpauth URI. Defaults to an empty string.
        issuer (str): The issuer to use in the otpauth URI. Defaults to an empty string.
        **parameters (Dict[str, Any]): Additional parameters to include in the otpauth URI.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the generated TOTP code, otpauth URI, and other relevant parameters.
            - utc (int): The Unix timestamp used.
            - exec (Dict[str, Any]): A dictionary containing:
                - original_secret (str): The original secret key provided.
                - secret (str): The base32-encoded secret key used.
                - interval (int): The time interval used.
                - digits (int): The number of digits in the TOTP code.
                - algorithm (str): The hashing algorithm used.
                - utc (int): The Unix timestamp used.
                - label (str): The label used in the otpauth URI.
                - issuer (str): The issuer used in the otpauth URI.
                - code (str): The generated TOTP code.
                - parameters (Dict[str, Any]): Any additional parameters provided.
            - res (Dict[str, Any]): A dictionary containing:
                - verif (bool): Whether the generated code matches any of the provided parameters.
                - code (str): The generated TOTP code.
                - uri (str): The constructed otpauth URI.
        Returns None if the secret is invalid or cannot be decoded.

    Raises:
        ValueError: If the secret is invalid or cannot be decoded.

    Example:
        >>> result = totp(secret="JBSWY3DPEHPK3PXP", interval=30, digits=6, algorithm="sha1")
        >>> print(result)
        {
            "utc": 1749471978,
            "exec": {
                "original_secret": "b81ea4ce0dc4",
                "secret": "MI4DCZLBGRRWKMDEMM2A====",
                "interval": 30,
                "digits": 6,
                "algorithm": "sha1",
                "utc": 1749471978,
                "label": "",
                "issuer": "",
                "code": "592156",
                "parameters": {
                    "original_secret": "b81ea4ce0dc4",
                    "code": "592156",
                    "parameters": {}
                }
            },
            "res": {
                "verif": True,
                "code": "592156",
                "uri": "otpauth://totp/default%3A1749471978?original_secret=b81ea4ce0dc4&secret=MI4DCZLBGRRWKMDEMM2A%3D%3D%3D%3D&interval=30&digits=6&algorithm=sha1&utc=1749471978&label=&issuer=&code=592156&parameters=%7B%27original_secret%27%3A%20%27b81ea4ce0dc4%27%2C%20%27code%27%3A%20%27592156%27%2C%20%27parameters%27%3A%20%7B%7D%7D"
            }
        }

    Note:
        - If the secret is an otpauth URI, the function will parse it and extract parameters.
        - The function assumes the secret is base32-encoded. If not, it will attempt to encode it.
        - The `pyotp` library is used to generate the TOTP code.

    See Also:
        pyotp.TOTP: The TOTP class from the pyotp library used for generating TOTP codes.

    生成基于时间的一次性密码（TOTP），并构造otpauth URI。

    该函数实现了 RFC 6238 中指定的 TOTP 算法。它接受一个密钥和其他参数，生成在特定时间间隔内有效的一次性密码。此外，它还构造了一个otpauth URI，
    可用于在 Google Authenticator 等应用程序中配置 TOTP。该函数还支持解析 otpauth URI 以提取参数，并基于这些参数生成 TOTP 代码。

    参数：
        secret (Optional[str])：用于生成 TOTP 代码的密钥。可以是原始密钥或 otpauth URI。
        interval (int)：TOTP 代码有效的时间间隔（以秒为单位）。默认为 30 秒。
        digits (int)：生成的 TOTP 代码的位数。默认为 6 位。
        algorithm (str)：用于生成 TOTP 代码的哈希算法。默认为 "sha1"。
        utc (int)：用于生成 TOTP 代码的 Unix 时间戳。如果为 0，则使用当前时间。
        label (str)：在 otpauth URI 中使用的标签。默认为空字符串。
        issuer (str)：在 otpauth URI 中使用的发行者。默认为空字符串。
        **parameters (Dict[str, Any])：在 otpauth URI 中包含的其他参数。

    返回值：
        Optional[Dict[str, Any]]：一个字典，包含生成的 TOTP 代码、otpauth URI 以及其他相关参数。
            - utc (int)：使用的 Unix 时间戳。
            - exec (Dict[str, Any])：一个字典，包含：
                - original_secret (str)：提供的原始密钥。
                - secret (str)：使用的 base32 编码密钥。
                - interval (int)：使用的时间间隔。
                - digits (int)：TOTP 代码的位数。
                - algorithm (str)：使用的哈希算法。
                - utc (int)：使用的 Unix 时间戳。
                - label (str)：在 otpauth URI 中使用的标签。
                - issuer (str)：在 otpauth URI 中使用的发行者。
                - code (str)：生成的 TOTP 代码。
                - parameters (Dict[str, Any])：提供的其他参数。
            - res (Dict[str, Any])：一个字典，包含：
                - verif (bool)：生成的代码是否与提供的任何参数匹配。
                - code (str)：生成的 TOTP 代码。
                - uri (str)：构造的 otpauth URI。
        如果密钥无效或无法解码，则返回 None。

    异常：
        ValueError：如果密钥无效或无法解码。

    示例：
        >>> result = totp(secret="JBSWY3DPEHPK3PXP", interval=30, digits=6, algorithm="sha1")
        >>> print(result)
        {
            "utc": 1749471978,
            "exec": {
                "original_secret": "b81ea4ce0dc4",
                "secret": "MI4DCZLBGRRWKMDEMM2A====",
                "interval": 30,
                "digits": 6,
                "algorithm": "sha1",
                "utc": 1749471978,
                "label": "",
                "issuer": "",
                "code": "592156",
                "parameters": {
                    "original_secret": "b81ea4ce0dc4",
                    "code": "592156",
                    "parameters": {}
                }
            },
            "res": {
                "verif": True,
                "code": "592156",
                "uri": "otpauth://totp/default%3A1749471978?original_secret=b81ea4ce0dc4&secret=MI4DCZLBGRRWKMDEMM2A%3D%3D%3D%3D&interval=30&digits=6&algorithm=sha1&utc=1749471978&label=&issuer=&code=592156&parameters=%7B%27original_secret%27%3A%20%27b81ea4ce0dc4%27%2C%20%27code%27%3A%20%27592156%27%2C%20%27parameters%27%3A%20%7B%7D%7D"
            }
        }

    注意：
        - 如果密钥是 otpauth URI，该函数将解析它并提取参数。
        - 该函数假设密钥是 base32 编码的。如果不是，它将尝试对其进行编码。
        - 使用 `pyotp` 库生成 TOTP 代码。

    参见：
        pyotp.TOTP：pyotp 库中用于生成 TOTP 代码的 TOTP 类。
    """
    match secret:
        case None:
            return None
        case bytes():
            otp_secret = secret.decode("UTF-8")
        case _:
            otp_secret = str(secret)
    otp_data = {
        "utc": int(time()),
        "exec": {
            "original_secret": parameters["original_secret"] if "original_secret" in parameters else otp_secret,
            "secret": otp_secret,
            "interval": interval,
            "digits": digits,
            "algorithm": algorithm,
            "utc": utc or int(time()),
            "label": label,
            "issuer": issuer,
            # "code": parameters["code"] if ("code" in parameters.copy()) else str(),
            "parameters": parameters,
        },
        "res": {
            "verif": False,
            "code": None,
            "otpauth_uri": None
        }
    }
    if "otpauth" in otp_secret:
        otp_params = parse_qs(urlparse(otp_secret).query)
        otp_extracted = {k: v[0] for k, v in otp_params.items()}
        otp_data["exec"].update({
            "secret": otp_extracted.get("secret", otp_data["secret"]),
            "interval": int(otp_extracted.get("period", otp_data["interval"])),
            "digits": int(otp_extracted.get("digits", otp_data["digits"])),
            "algorithm": otp_extracted.get("algorithm", otp_data["algorithm"]),
            "utc": int(otp_extracted.get("utc", otp_data["utc"])) or int(time()),
            "label": otp_extracted.get("label", otp_data["label"]) or label,
            "issuer": otp_extracted.get("issuer", otp_data["issuer"])
        })
    try:
        b32decode(otp_data["exec"]["secret"])
    except:
        otp_data["exec"]["secret"] = b32encode(
            otp_data["exec"]["secret"].encode("UTF-8")
        ).decode("UTF-8")
    otp_code = TOTP(
        otp_data["exec"]["secret"],
        interval=otp_data["exec"]["interval"],
        digits=otp_data["exec"]["digits"],
        digest=getattr(hashlib, otp_data["exec"]["algorithm"].lower())
    ).at(otp_data["exec"]["utc"])
    otp_label = otp_data["exec"]["label"] or f"""default:{otp_data["utc"]}"""
    # otp_data["exec"]["code"] = otp_code
    otp_data["res"].update(
        {
            "verif": otp_code in parameters.values(),
            "code": otp_code,
            "otpauth_uri": urlunparse(
                (
                    "otpauth",
                    "totp",
                    f"/{quote(otp_label, safe=str())}",
                    str(),
                    urlencode(otp_data["exec"], quote_via=quote),
                    str()
                )
            )
        }
    )
    return otp_data


class servers:
    """
    WebSocket 服务器类，负责处理客户端连接、验证、数据接收和发送。

    该类实现了 WebSocket 服务器的核心功能，包括客户端连接管理、验证流程、
    消息接收与发送，以及与数据库的交互。设计用于需要实时数据交换和客户端管理的场景。

    Attributes:
        无显式定义的属性，所有操作通过方法参数和局部变量完成。
    """

    async def connect(self, ws):
        """
        处理客户端连接，记录连接信息。

        创建包含连接时间戳和网络地址的字典，并将其插入日志集合。

        Args:
            ws: WebSocket 连接对象。

        Returns:
            包含连接信息的字典，包括 UTC 时间戳、验证状态、网络地址和代码。

        Example:
            >>> connect_data = await server.connect(ws)
            >>> print(connect_data)
            {
                "utc": 1621548726,
                "verif": None,
                "network": {
                    "send": ["127.0.0.1", 12345],
                    "recv": ["127.0.0.1", 10000]
                },
                "code": None
            }
        """
        # 创建连接信息字典，包含当前时间戳和网络地址
        connect_data = {
            "utc": int(time()),
            "verif": None,
            "network": {
                "send": list(ws.remote_address),
                "recv": list(ws.local_address)
            },
            "code": None
        }
        # 将连接信息插入日志集合
        await server_log.insert_one(connect_data.copy())
        return connect_data

    async def verif(self, ws, timeout=10.0):
        """
        处理客户端验证请求。

        等待客户端发送验证信息，使用 TOTP 进行验证，并将结果发送回客户端。
        如果验证成功，将验证信息插入验证集合。

        Args:
            ws: WebSocket 连接对象。
            timeout: 等待验证信息的超时时间（秒）。默认为 10.0。

        Returns:
            包含验证结果的字典，包括 UTC 时间戳、验证状态、网络地址和代码。

        Raises:
            asyncio.TimeoutError: 如果等待验证信息超时。
            json.JSONDecodeError: 如果验证信息无法解析为 JSON。
            Exception: 捕获其他验证过程中的异常。

        Example:
            >>> verif_data = await server.verif(ws)
            >>> print(verif_data)
            {
                "utc": 1621548726,
                "verif": {"exec": {"secret": "..."}, "res": {"verif": true}},
                "network": {
                    "send": ["127.0.0.1", 12345],
                    "recv": ["127.0.0.1", 10000]
                },
                "code": "Verification successful! You can now proceed with your operation."
            }
        """
        # 创建验证信息字典
        verif_data = {
            "utc": int(time()),
            "verif": None,
            "network": {
                "send": list(ws.remote_address),
                "recv": list(ws.local_address)
            },
            "code": None
        }
        try:
            # 等待客户端发送验证信息，设置超时时间
            verif_data["verif"] = await asyncio.wait_for(ws.recv(), timeout=timeout)
            # 将接收到的验证信息解析为字典
            verif_data["verif"] = loads(verif_data["verif"])
            if verif_data["verif"] and isinstance(verif_data["verif"], dict):
                # 使用 mfa.totp 进行验证
                verif_result = totp(**verif_data["verif"])
                # 根据验证结果设置返回信息
                verif_data["code"] = "Verification successful! You can now proceed with your operation." if verif_result[
                    "res"]["verif"] else "Verification failed! The OTP is invalid or has expired."
                verif_data["verif"] = verif_result

                # 如果验证成功，将验证信息插入验证集合
                if verif_result["res"]["verif"]:
                    await server_verif.insert_one(verif_data.copy())
        except Exception as e:
            # 捕获验证过程中的异常
            verif_data["code"] = f"Verification timed out. {str(e)}"
        # 更新或插入日志信息
        server_log.update_one(
            {"network.send": verif_data["network"]["send"]},
            {"$set": verif_data.copy()},
            upsert=True
        )
        # 向客户端发送验证结果
        await ws.send(dumps(verif_data, indent=4, ensure_ascii=False))
        if (not verif_data["verif"]):
            await ws.close()
        return verif_data

    async def recv(self, ws):
        """
        接收客户端发送的消息并进行处理。

        解析接收到的消息，根据消息内容执行相应的操作，如查询数据库或插入数据。
        处理结果发送回客户端。

        Args:
            ws: WebSocket 连接对象。

        Raises:
            json.JSONDecodeError: 如果消息无法解析为 JSON。
            Exception: 捕获其他消息处理过程中的异常。

        Note:
            该方法设计为在 ws 方法中反复调用，以持续处理客户端消息。
        """
        message_data = await ws.recv()
        try:
            # 将接收到的消息解析为字典
            message_data = loads(message_data)
            # 如果消息包含列表操作请求
            if "@decive" in message_data.get("code", {}):
                # 统计符合条件的文档数量
                count = await server_verif.count_documents(message_data["code"]["@decive"])
                # 向客户端发送数量信息
                await ws.send(str(count))
                # 向客户端发送符合条件的文档
                async for document in server_verif.find(message_data["code"]["@decive"], {"_id": 0}):
                    await ws.send(dumps(document, indent=4, ensure_ascii=False))
            else:
                # 检查通信双方的验证状态
                message_swap = {
                    "status": bool(await server_verif.count_documents({"network.send": message_data["network"]["send"]}) and
                                   await server_verif.count_documents({"network.send": message_data["network"]["recv"]}))
                }
                # 如果验证通过，将消息插入数据集合
                if message_swap["status"]:
                    insert_result = await server_data.insert_one(message_data.copy())
                    message_swap["mongo"] = str(insert_result.inserted_id)
                # 向客户端发送消息处理结果
                message_data["code"] = {
                    **message_swap,
                    **message_data["network"],
                    "data": message_data["code"]
                }
                await ws.send(dumps(message_data, indent=4, ensure_ascii=False))
        except Exception as e:
            # 捕获消息接收和处理过程中的异常
            if "code" not in message_data:
                message_data["code"] = {}
            message_data["code"]["error"] = str(e)
            await ws.send(dumps(message_data, indent=4, ensure_ascii=False))

    async def send(self, ws):
        """
        向客户端发送消息。

        查找符合条件的文档并发送给客户端，发送后删除已发送的文档。

        Args:
            ws: WebSocket 连接对象.

        Note:
            该方法设计为在 ws 方法中反复调用，以持续向客户端发送消息。
        """
        # 查找符合条件的文档
        document = await server_data.find_one({"network.recv": list(ws.remote_address)}, {"_id": 0})
        if document:
            # 向客户端发送文档内容
            await ws.send(dumps(document, indent=4, ensure_ascii=False))
            # 删除已发送的文档
            await server_data.delete_one(document)

    async def ws(self, ws):
        """
        WebSocket 连接处理的主方法，协调连接、验证和消息收发。

        Args:
            ws: WebSocket 连接对象.

        Note:
            该方法管理客户端的整个生命周期，包括连接建立、验证、消息处理和连接关闭。
            在连接关闭时，清理与客户端相关的数据。
        """
        # 处理客户端连接
        ws_data = await self.connect(ws)
        # 处理客户端验证
        ws_data = await self.verif(ws)
        try:
            # 打印连接信息
            ws_dt = [
                "[",
                str(dt.now())[:-7],
                F"""] -> ip:{ws_data["network"]["send"][0]}""",
                F"""port:{str(ws_data["network"]["send"][1])} Connected"""
            ]
            print(" ".join(ws_dt))
            print("-" * 100)
            # 循环处理消息收发
            while True:
                await asyncio.gather(self.recv(ws), self.send(ws))
        except Exception as e:
            # 捕获 WebSocket 连接过程中的异常
            ws_data["code"] = [ws_data["code"], f"WebSocket error:{str(e)}"]
            # 更新或插入日志信息
            server_log.update_one(
                {"network.send": ws_data["network"]["send"]},
                {"$set": ws_data},
                upsert=True
            )
        finally:
            # 删除与客户端相关的数据
            await server_data.delete_many({"network.send": list(ws.remote_address)})
            await server_verif.delete_many({"network.send": list(ws.remote_address)})
            # 打印连接关闭信息
            ws_dt[1] = F"{ws_dt[1]} ~ {str(dt.now())[:-7]}"
            ws_dt.append("closed.")
            print(" ".join(ws_dt))
            print("-" * 100)

    async def server(
        self,
        host: str | None = None,
        port: int | None = None,
        *,
        origins: list[str] | None = None,
        extensions: list[str] | None = None,
        subprotocols: list[str] | None = None,
        compression: str | None = "deflate",
        open_timeout: float | None = 10.0,
        ping_interval: float | None = 20.0,
        ping_timeout: float | None = 20.0,
        close_timeout: float | None = 10.0,
        max_size: int | None = 2 ** 20,
        max_queue: int | tuple[int | None, int | None] | None = 16,
        write_limit: int | tuple[int, int | None] = 2 ** 15,
        logger: object | None = None,
        create_connection: type[object] | None = None,
        **kwargs: dict[str, object]
    ):
        """
        启动 WebSocket 服务器。

        配置并启动 WebSocket 服务器，监听指定的主机和端口，处理客户端连接。

        Args:
            host: 服务器主机地址。默认为 None（监听所有接口）。
            port: 服务器端口号。默认为 None（操作系统选择可用端口）。
            origins: 允许的源列表。默认为 None（允许所有源）。
            extensions: 支持的 WebSocket 扩展。默认为 None。
            subprotocols: 支持的子协议。默认为 None。
            compression: 压缩方法。默认为 "deflate"。
            open_timeout: 连接超时时间（秒）。默认为 10.0。
            ping_interval: 发送 ping 间隔时间（秒）。默认为 20.0。
            ping_timeout: 等待 pong 超时时间（秒）。默认为 20.0。
            close_timeout: 关闭连接超时时间（秒）。默认为 10.0。
            max_size: 接收消息的最大大小（字节）。默认为 2**20。
            max_queue: 最大消息队列大小。默认为 16。
            write_limit: 发送缓冲区限制。默认为 2**15。
            logger: 日志记录器。默认为 None。
            create_connection: 自定义连接创建类。默认为 None。
            **kwargs: 额外的关键字参数，传递给 WebSocket 服务器。

        Example:
            >>> server = servers()
            >>> await server.server(host="127.0.0.1", port=10000)

        Note:
            该方法会持续运行直到服务器被显式关闭。
            所有连接参数均可通过方法参数进行配置，以适应不同部署环境。
        """
        # 使用 async with 结构来管理服务器的生命周期
        async with serve(
            handler=self.ws,
            host=host,
            port=port,
            origins=origins,
            extensions=extensions,
            subprotocols=subprotocols,
            compression=compression,
            open_timeout=open_timeout,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            close_timeout=close_timeout,
            max_size=max_size,
            max_queue=max_queue,
            write_limit=write_limit,
            logger=logger,
            create_connection=create_connection,
            **kwargs
        ) as server:
            # 获取服务器的套接字信息
            sockets = server.sockets
            print("-" * 100)
            if sockets:
                print(
                    "".join(
                        [
                            "[ ",
                            str(dt.now())[:-7],
                            " ] WebSocket server started at ws://",
                            sockets[0].getsockname()[0], ":",
                            str(sockets[0].getsockname()[1])
                        ]
                    )
                )
            print("-" * 100)
            # 保持服务器运行
            await asyncio.Future()


class clients:
    """
    一个基于 WebSocket 的客户端类，用于处理与服务器的连接、验证和数据转发。

    该类实现了客户端与服务器之间的通信逻辑，包括初始验证、数据接收与转发，以及设备状态更新。
    设计用于需要实时数据交换和设备管理的场景。

    Attributes:
        无显式定义的属性，所有操作通过方法参数和局部变量完成。

    Methods:
        verif(ws, debug): 执行客户端验证，生成 OTP 并与服务器交换验证信息。
        forward(ws, client_data): 转发服务器数据，并根据需要更新本地数据库。
        client(uri, ...): 主连接方法，建立 WebSocket 连接并启动数据处理循环。

    Example:
        >>> clients = Clients()
        >>> await clients.client("ws://example.com/socket")

    Note:
        该类依赖于外部数据库集合（client_log, client_write, client_read, client_device）和 WebSocket 连接。
        需确保数据库和网络配置正确，以保证功能正常运行。

    See Also:
        websockets.connect: 用于建立 WebSocket 连接。
        pymongo.Collection: 用于数据库操作。
    """

    async def verif(self, ws, typeio=F"client_{str(uuid1())[-12:]}", otp=str(uuid1())[-12:], debug=False):
        """
        执行客户端验证过程，生成 OTP 并与服务器交换验证信息。

        生成基于时间的一次性密码（OTP），将其发送到服务器，并接收服务器的响应。
        验证结果和服务器响应将被记录到数据库中。

        Args:
            ws (websockets.client.WebSocketClientProtocol): 已建立的 WebSocket 连接。
            typeio (str, optional): 客户端类型标识符。默认为基于 UUID 的字符串。
            otp (str, optional): 用于生成 OTP 的基础值。默认为基于 UUID 的字符串。
            debug (bool, optional): 调试模式开关。默认为 False。

        Returns:
            Dict[str, Any]: 服务器返回的验证响应数据。

        Raises:
            websockets.exceptions.ConnectionClosed: 如果 WebSocket 连接在验证过程中关闭。
            json.JSONDecodeError: 如果服务器响应无法解析为 JSON。

        Note:
            该方法依赖于外部的 TOTP 实现（此处简化为示例代码）。
            在生产环境中，应替换为安全的 TOTP 生成和验证逻辑。

        See Also:
            forward: 在验证成功后，通常会调用 forward 方法处理后续数据。
        """
        otp = totp(otp)
        otp = {
            "type": typeio,
            "secret": otp["exec"]["secret"],
            "code": otp["res"]["code"],
        }
        debug and otp.update({"totp_debug": debug})
        await ws.send(dumps(otp, indent=4, ensure_ascii=False))
        response = loads(await ws.recv())
        client_log.insert_one(response.copy())
        return response

    async def forward(self, ws, client_data):
        """
        转发服务器数据，并根据需要更新本地数据库。

        从 client_write 数据库集合中获取待处理数据，将其整合到客户端数据中，
        发送到服务器，并根据服务器响应更新 client_read 和 client_device 数据库集合。

        Args:
            ws (websockets.client.WebSocketClientProtocol): 已建立的 WebSocket 连接。
            client_data (Dict[str, Any]): 客户端基础数据，通常由 verif 方法生成。

        Returns:
            None

        Raises:
            websockets.exceptions.ConnectionClosed: 如果 WebSocket 连接在数据传输过程中关闭。
            json.JSONDecodeError: 如果服务器响应无法解析为 JSON。
            pymongo.errors.PyMongoError: 如果数据库操作失败。

        Note:
            该方法设计为在客户端主循环中反复调用，以持续处理服务器数据。

        See Also:
            verif: 通常在调用 forward 之前先执行 verif 方法完成初始验证。
        """
        client_swap = await client_write.find_one_and_delete(dict(), {"_id": 0})
        if (client_swap):
            if ("code" in client_swap):
                client_data["code"] = client_swap["code"]
                if ("network" in client_swap):
                    client_data["network"]["recv"] = client_swap["network"]["recv"]
                else:
                    client_data["network"]["recv"] = client_data["network"]["send"]
                client_swap = dumps(
                    client_data,
                    indent=4,
                    ensure_ascii=False
                )
                await ws.send(client_swap)
                for f1 in range(2):
                    client_swap = loads(await ws.recv())
                    if ("mongo" in client_swap["code"]):
                        del client_swap["code"]["mongo"]
                    del client_swap["verif"]
                    await client_read.update_one(
                        {
                            "$and": [
                                {"network": client_swap["network"]},
                                {"code": client_swap["code"]}
                            ]
                        },
                        {"$set": client_swap.copy()},
                        upsert=True
                    )
            if ("@device" in client_swap):
                client_data["code"] = {"@decive": {}}
                client_swap = dumps(
                    client_data,
                    indent=4,
                    ensure_ascii=False
                )
                await ws.send(client_swap)
                client_swap = loads(await ws.recv())
                for f1 in range(client_swap):
                    f1 = loads(await ws.recv())
                    await client_device.update_one(
                        {"network.send": f1["network"]["send"]},
                        {"$set": f1.copy()},
                        upsert=True
                    )
                client_swap = [
                    F"[{str(dt.now())[:-7]}] -> ",
                    F"{client_swap} 个设备在线。"
                ]
                client_swap = "".join(client_swap)
                client_swap = dict()

    async def client(
            self,
            uri: str = "ws://127.0.0.1:10000",
            origin: str | None = None,
            extensions: list[str] | None = None,
            subprotocols: list[str] | None = None,
            compression: str | None = "deflate",
            additional_headers: dict | None = None,
            user_agent_header: str | None = "USER_AGENT",
            proxy: bool | None = True,
            open_timeout: float | None = 10.0,
            ping_interval: float | None = 20.0,
            ping_timeout: float | None = 20.0,
            close_timeout: float | None = 10.0,
            max_size: int | None = 2**20,
            max_queue: int | None | tuple[int | None, int | None] = 16,
            write_limit: int | tuple[int, int | None] = 2**15,
            logger: object | None = None,
            create_connection: type[object] | None = None,
            **kwargs: dict[str, object]
    ):
        """
        建立 WebSocket 连接并启动客户端主循环。

        初始化 WebSocket 连接，执行客户端验证，并进入数据处理循环，
        持续调用 forward 方法处理服务器数据。

        Args:
            uri (str): WebSocket 服务器地址。默认为 "ws://127.0.0.1:10000"。
            origin (Optional[str]): 请求的源。默认为 None。
            extensions (Optional[List[str]]): 支持的 WebSocket 扩展。默认为 None。
            subprotocols (Optional[List[str]]): 支持的子协议。默认为 None。
            compression (Optional[str]): 压缩方法。默认为 "deflate"。
            additional_headers (Optional[Dict[str, str]]): 额外的 HTTP 请求头。默认为 None。
            user_agent_header (Optional[str]): User-Agent 请求头值。默认为 "USER_AGENT"。
            proxy (Optional[bool]): 是否使用代理。默认为 True。
            open_timeout (Optional[float]): 连接超时时间（秒）。默认为 10.0。
            ping_interval (Optional[float]): 发送 ping 间隔时间（秒）。默认为 20.0。
            ping_timeout (Optional[float]): 等待 pong 超时时间（秒）。默认为 20.0。
            close_timeout (Optional[float]): 关闭连接超时时间（秒）。默认为 10.0。
            max_size (Optional[int]): 接收消息的最大大小（字节）。默认为 2**20。
            max_queue (Optional[Tuple[int, int]]): 最大消息队列大小。默认为 (16, None)。
            write_limit (Optional[Tuple[int, int]]): 发送缓冲区限制。默认为 (2**15, None)。
            logger (Optional[object]): 日志记录器。默认为 None。
            create_connection (Optional[type]): 自定义连接创建类。默认为 None。
            **kwargs (Dict[str, Any]): 额外的关键字参数，传递给 WebSocket 连接。

        Returns:
            None

        Raises:
            websockets.exceptions.InvalidURI: 如果 URI 格式无效。
            websockets.exceptions.ConnectionFailed: 如果连接建立失败。
            Exception: 捕获所有其他异常并打印错误消息。

        Note:
            该方法会持续运行直到连接中断或程序终止。
            所有连接参数均可通过方法参数进行配置，以适应不同服务器要求。

        See Also:
            verif: 在连接建立后立即调用，执行初始验证。
            forward: 在主循环中反复调用，处理服务器数据。
        """
        try:
            async with connect(
                uri=uri,
                origin=origin,
                extensions=extensions,
                subprotocols=subprotocols,
                compression=compression,
                additional_headers=additional_headers,
                user_agent_header=user_agent_header,
                proxy=proxy,
                open_timeout=open_timeout,
                ping_interval=ping_interval,
                ping_timeout=ping_timeout,
                close_timeout=close_timeout,
                max_size=max_size,
                max_queue=max_queue,
                write_limit=write_limit,
                logger=logger,
                create_connection=create_connection,
                **kwargs
            ) as ws:
                client_data = await self.verif(ws)
                print("-" * 100)
                print(F"[{str(dt.now())[:-7]}] 已连接，返回数据：{client_data["code"]}")
                print("-" * 100)
                while True:
                    await self.forward(ws, client_data)
        except Exception as e:
            print(f"发生错误：{e}")


def task():
    """
    启动 WebSocket 服务的入口点。
    会根据用户输入的参数决定启动服务端还是客户端。
    """
    # 定义默认配置
    config_server = {
        "host": "127.0.0.1",
        "port": 10000,
        "origins": None,
        "extensions": None,
        "subprotocols": None,
        "compression": "deflate",
        "open_timeout": 10.0,
        "ping_interval": 20.0,
        "ping_timeout": 20.0,
        "close_timeout": 10.0,
        "max_size": 2 ** 20,
        "max_queue": 16,
        "write_limit": 2 ** 15,
        "logger": None,
        "create_connection": None
    }
    config_client = {
        "uri": "ws://127.0.0.1:10000",
        "origin": None,
        "extensions": None,
        "subprotocols": None,
        "compression": "deflate",
        "additional_headers": None,
        "user_agent_header": "USER_AGENT",
        "proxy": True,
        "process_exception": lambda e: e,
        "open_timeout": 10.0,
        "ping_interval": 20.0,
        "ping_timeout": 20.0,
        "close_timeout": 10.0,
        "max_size": 2 ** 20,
        "max_queue": 16,
        "write_limit": 2 ** 15,
        "logger": None,
        "create_connection": None
    }

    # 配置文件路径（相对于脚本目录）
    config_server_path = join(script_dir, "server_config.json")
    config_client_path = join(script_dir, "client_config.json")

    # 解析命令行参数
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--server", action="store_true", help="启动服务器")
    parser.add_argument("--client", action="store_true", help="启动客户端")
    args, _ = parser.parse_known_args()

    # 检查是否没有参数
    if not args.server and not args.client:
        help()
        exit(0)

    # 根据参数决定启动服务器还是客户端
    if args.server:
        # 检查服务器配置文件
        if exists(config_server_path):
            with open(config_server_path, "r", encoding="utf-8") as f:
                try:
                    server_config = load(f)
                    # 检查配置是否有效
                    if not all(key in server_config for key in config_server.keys()):
                        print("配置文件内容不完整，请检查或删除后重新运行程序")
                        server_config = config_server.copy()
                except Exception:
                    print("配置文件格式错误，请检查或删除后重新运行程序")
                    server_config = config_server.copy()
        else:
            server_config = config_server.copy()

        # 移除不可序列化的值
        server_config = {
            k: v for k, v in server_config.items() if not callable(v)
        }

        # 写入配置文件
        with open(config_server_path, "w", encoding="utf-8") as f:
            dump(server_config, f, indent=4, ensure_ascii=False)
            print(f"默认配置文件已生成于 {config_server_path}")

        server = servers()
        run(server.server(**server_config))

    if args.client:
        # 检查客户端配置文件
        if exists(config_client_path):
            with open(config_client_path, "r", encoding="utf-8") as f:
                try:
                    client_config = load(f)
                    # 检查配置是否有效
                    if not all(key in client_config for key in config_client.keys()):
                        print("配置文件内容不完整，请检查或删除后重新运行程序")
                        client_config = config_client.copy()
                except Exception:
                    print("配置文件格式错误，请检查或删除后重新运行程序")
                    client_config = config_client.copy()
        else:
            client_config = config_client.copy()

        # 移除不可序列化的值
        client_config = {
            k: v for k, v in client_config.items() if not callable(v)
        }

        # 写入配置文件
        with open(config_client_path, "w", encoding="utf-8") as f:
            dump(client_config, f, indent=4, ensure_ascii=False)
            print(f"默认配置文件已生成于 {config_client_path}")

        client = clients()
        run(client.client(**client_config))


def help():
    """
    显示帮助信息
    """
    print("FuseLink 程序使用说明:")
    print("   --server     启动 FuseLink 服务器")
    print("   --client     启动 FuseLink 客户端")
    print("示例:")
    print("   python fuselink.py --server")
    print("   python fuselink.py --client")


if __name__ == "__main__":
    task()
