
# from playwright.sync_api import Browser, BrowserContext, Page, Locator, Response
from browserforge.fingerprints import Screen
from camoufox.sync_api import Camoufox
from time import sleep


class browser:
    """
    用于创建和管理自定义浏览器实例的类，集成多种功能以模拟真实用户访问行为。

    该类设计用于自动化浏览器操作，支持通过 Playwright 和 Camoufox 库进行高级浏览器控制和设备指纹识别。它允许用户通过配置参数模拟不同的浏览环境，包括屏幕分辨率、地理位置、代理设置等。类中提供了启动、关闭浏览器，导航到 URL，执行延迟操作以及运行自定义命令的方法。

    Attributes:
        swap (any): 用于存储临时数据或供将来扩展使用。
        device (Camoufox): 底层的 Camoufox 实例，用于实际的浏览器控制和操作。

    Methods:
        __init__(**kwargs): 初始化一个新的浏览器实例，支持多种配置选项。
        call(Class, List): 在指定的类实例上执行一系列命令。
        launch(): 启动浏览器实例。
        close(): 关闭浏览器实例。
        goto(uri): 导航浏览器到指定的 URL。
        delay(timeout): 暂停执行指定的时间。
        demo(**kwargs): 演示方法，可扩展用于自定义功能。

    Example:
        >>> launcher = browser(user="test_user", screen={"min_width": 1920, "max_width": 1920, "min_height": 1080, "max_height": 1080})
        >>> launcher.launch()
        >>> launcher.goto("https://www.example.com")
        >>> launcher.delay(timeout=2.0)
        >>> launcher.close()

    Note:
        需要安装并配置 Playwright、Camoufox 等依赖库才能正常使用。
        浏览器实例在启动后会占用系统资源，使用完毕后务必调用 close() 方法释放资源。

    See Also:
        Camoufox: 提供底层浏览器控制和设备指纹识别功能。
        Playwright: 用于浏览器自动化操作的基础库。
    """

    def __init__(self, **kwargs):
        """
        初始化一个新的浏览器实例，支持多种配置选项来自定义浏览器行为。

        参数:
            **kwargs: 可变参数，用于配置浏览器实例。
                user (str): 指定用户配置文件名称，默认为 "default"。
                screen (dict): 屏幕分辨率设置，包含 min_width、max_width、min_height、max_height 参数。
                proxy (dict): 代理服务器设置，包含 server、username、password 参数。
                no_viewport (bool): 是否禁用视口模拟，默认为 False。

        注意:
            如果未提供参数，则使用默认配置创建浏览器实例。
            默认屏幕分辨率为 1440x900，代理设置为 None。
        """

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
        """
        在指定的类实例上执行一系列命令，支持批量操作。

        参数:
            Class (type 或 object): 要执行命令的目标类或实例。
            List (list): 包含命令字典的列表，每个字典包含命令名称和参数。

        返回:
            dict: 执行结果字典，包含每个命令的执行时间和结果。

        示例:
            >>> results = launcher.call(
            ...     Class=launcher,
            ...     List=[
            ...         {"launch": {"params": None}},
            ...         {"goto": {"params": {"uri": "https://www.example.com"}}}
            ...     ]
            ... )

        注意:
            命令字典中的 "params" 键对应方法的参数，可以为 None 或包含参数的字典。
        """

        from time import time
        swap_call = None
        for Dict in List:
            for f1 in Dict:
                try:
                    swap_exec = getattr(Class, f1, None)
                    if (callable(swap_exec) and "params" in Dict[f1]):
                        if (Dict[f1]["params"]):
                            swap_call = swap_exec(**Dict[f1]["params"].copy())
                        else:
                            swap_call = swap_exec()
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
        """
        启动浏览器实例，返回初始页面对象。

        此方法启动底层的 Camoufox 实例，并获取第一个页面对象供后续操作使用。

        注意:
            启动浏览器会消耗较多系统资源，建议在必要时才调用。
        """

        self.device = self.device.start().pages[0]  # 获取启动后的页面对象

    def close(self):
        """
        关闭浏览器实例，释放所有关联资源。

        调用此方法后，浏览器实例将无法再进行任何操作，需重新初始化并启动才能继续使用。

        注意:
            使用完毕后务必调用此方法释放资源，避免系统资源泄漏。
        """

        self.device.close()

    def goto(self, **kwargs):
        """
        导航浏览器到指定的 URL 地址。

        参数:
            **kwargs: 关键字参数，包含导航所需设置。
                uri (str): 要访问的目标 URL 地址。

        返回:
            str: 实际导航到的 URL 地址。

        异常:
            Exception: 如果导航过程中发生错误，如 URL 格式错误或网络问题。

        注意:
            导航操作会等待页面加载完成或达到超时时间。
        """

        uri = kwargs.get("uri", "data;")
        self.device.goto(uri)
        return uri

    def delay(self, **kwargs):
        """
        暂停当前执行流程，等待指定的时间间隔。

        参数:
            **kwargs: 关键字参数，包含延迟设置。
                timeout (float): 以秒为单位的延迟时间，默认为 0.0。

        返回:
            float: 实际延迟的时间。

        注意:
            延迟操作通常用于模拟用户行为或等待异步操作完成。
        """

        timeout = kwargs.get("timeout", 0.0)
        sleep(timeout)
        return timeout

    def demo(self, **kwargs):
        """
        演示方法，用于展示自定义功能的实现方式。

        参数:
            **kwargs: 关键字参数，用于传递演示所需的数据。

        示例:
            >>> launcher.demo(message="Hello, World!")

        注意:
            此方法需根据实际需求进行扩展或重写以实现具体功能。
        """

        print(**kwargs)


def demo():
    """
    展示 browser 类基本用法的演示函数。

    此函数创建并启动一个浏览器实例，导航到指定 URL，并等待用户输入后关闭浏览器。

    示例:
        >>> demo()

    注意:
        演示过程中会启动浏览器窗口，可能需要手动关闭或等待输入以继续。
    """
    
    launcher = browser()
    if (False):
        launcher.launch()  # 明确启动浏览器
        launcher.goto(**{"uri": "https://www.devicescan.net/zh"})  # 访问页面
    else:
        launcher.call(
            [
                {
                    "launch": {"params": None},
                    "goto": {"params": {"uri": "https://www.devicescan.net/zh"}},
                }
            ]
        )
    input("Press Enter to close the device...")  # 等待用户输入
    launcher.close()  # 关闭浏览器


if __name__ == '__main__':
    demo()
