
from playwright.sync_api import Browser, BrowserContext, Page, Locator, Response
from browserforge.fingerprints import Screen
from camoufox.sync_api import Camoufox
from time import sleep


class browser:
    def __init__(self, **kwargs):
        if (not kwargs):
            kwargs = {
                "user": "default",
                # "screen": {
                #         "min_width": 1920,
                #         "max_width": 1920,
                #         "min_height": 1080,
                #         "max_height": 1080
                # },
                # "proxy": {
                #     "server": "socks5://127.0.0.1:10809",
                #     # "username": None,
                #     # "password": None,
                # },
                "no_viewport": False
            }
            print(kwargs.get("proxy", None))
        self.swap = None
        self.device = Camoufox(
            ** {
                "os": "windows",
                "screen": Screen(
                    **kwargs.get(
                        "screen",
                        {
                            "min_width": 1440,
                            "max_width": 1440,
                            "min_height": 900,
                            "max_height": 900
                        }
                    )
                ),
                "persistent_context": True,
                "user_data_dir": f"data_user/{kwargs.get("user", "default")}",
                "config": {
                    "webrtc:ipv4": "",
                    "webrtc:ipv6": "fe80::1",
                    "timezone": "America/Los_Angeles"
                },
                "proxy": kwargs.get("proxy", None),
                "i_know_what_im_doing": False,
                "no_viewport": kwargs.get("no_viewport", False),
                "locale": "zh-CN"
            }
        )

    def call(Class=None, List=list()):
        from time import time
        swap_call = None
        for Dict in List:
            for f1 in Dict:
                swap_exec = getattr(Class, f1, None)
                try:
                    if (callable(swap_exec) and "params" in Dict[f1]):
                        swap_call = swap_exec(**Dict[f1]["params"].copy())
                        swap_exec = callable(swap_exec)
                except BaseException as e:
                    swap_exec = False
                Dict[f1] = {
                    "utc": time(),
                    "params": Dict[f1]["params"],
                    "exec": swap_exec,
                    "res": swap_call
                }
                swap_call = None
        return {Class.__name__ if isinstance(Class, type) else Class.__class__.__name__: List}

    def launch(self):
        self.device = self.device.start().pages[0]  # 获取启动后的页面对象

    def close(self):
        self.device.close()

    def goto(self, uri):
        self.device.goto(uri)
        return uri

    def delay(self, timeout=0.0):
        sleep(timeout)
        return timeout


def demo():
    device = browser()
    device.launch()  # 明确启动浏览器
    device.goto("https://www.devicescan.net/zh")  # 访问页面
    input("Press Enter to close the device...")  # 等待用户输入
    device.close()  # 关闭浏览器


if __name__ == '__main__':
    demo()
