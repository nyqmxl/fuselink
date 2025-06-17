#!/usr/bin/env python
"""
Time-based One-Time Password (TOTP) Generator Module

This module provides functionality for generating Time-based One-Time Passwords (TOTPs) and constructing otpauth URIs.
It implements the TOTP algorithm as specified in RFC 6238 and supports parsing otpauth URIs to extract parameters.
The module is designed to be used in applications requiring two-factor authentication (2FA) and supports customization of TOTP parameters such as secret key, time interval, and hashing algorithm.



基于时间的一次性密码（TOTP）生成模块

本模块实现了 RFC 6238 中指定的 TOTP 算法，用于生成基于时间的一次性密码（TOTP），并构造 otpauth URI。
它支持解析 otpauth URI 以提取参数，并基于这些参数生成 TOTP 代码。该模块适用于需要双因素认证（2FA）的应用场景，
并支持自定义 TOTP 参数，如密钥、时间间隔和哈希算法。
"""


import hashlib
from time import time
from pyotp import TOTP
from typing import Dict, Any, Optional
from base64 import b32encode, b32decode
from urllib.parse import urlparse, parse_qs, urlunparse, quote, urlencode


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
    otp_label = otp_data["exec"]["label"] or f'''default:{otp_data["utc"]}'''
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
