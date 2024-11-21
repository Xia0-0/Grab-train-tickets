import requests  # 用于发送 HTTP 请求
import time  # 用于设置等待时间
from PIL import Image  # 用于处理二维码图片
from io import BytesIO  # 用于将二进制数据转换为文件流
from selenium import webdriver  # 使用 Selenium 控制浏览器操作
from selenium.webdriver.chrome.service import Service  # 导入 Service
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager  # 自动管理 ChromeDriver
from selenium.webdriver.common.by import By


class TicketBot:
    def __init__(self, qr_code_url, check_login_url):
        """
        初始化抢票机器人
        :param qr_code_url: 获取二维码的接口 URL
        :param check_login_url: 检查登录状态的接口 URL
        """
        self.qr_code_url = qr_code_url
        self.check_login_url = check_login_url
        self.session = requests.Session()  # 用于保持会话
        self.driver = None  # 浏览器驱动初始化为空
        self.login_attempts = 0  # 登录重试次数

    def setup_driver(self):
        """初始化浏览器驱动，使用自动下载和配置的 ChromeDriver"""
        try:
            service = Service(ChromeDriverManager().install())  # 使用webdriver-manager自动安装最新的驱动
            self.driver = webdriver.Chrome(service=service)  # 创建浏览器实例
            print("浏览器启动成功！")
        except WebDriverException as e:
            print(f"浏览器启动失败：{e}")
            raise  # 如果浏览器启动失败，抛出异常

    def login_by_qrcode(self):
        """通过扫码登录"""
        try:
            # 打开登录页面
            self.driver.get("https://kyfw.12306.cn/otn/resources/login.html")
            time.sleep(5)  # 等待页面加载

            # 定位并获取二维码图片
            qr_code_img = self.driver.find_element("id", "J-qrImg")  # 使用 id 定位二维码图片
            qr_code_url = qr_code_img.get_attribute("src")  # 获取二维码图片的 src 属性，即 Base64 编码的图像数据
            qr_code_data = self.get_qrcode(qr_code_url)  # 下载二维码图片

            # 展示二维码图片
            qr_code_data.show()  # 使用PIL打开图片展示
            print("请使用 12306 APP 扫描二维码登录...")

            # 检查登录状态
            self.wait_for_login()
        except NoSuchElementException as e:
            print(f"元素定位失败：{e}")  # 捕获元素定位错误
        except Exception as e:
            print(f"扫码登录过程中出现错误：{e}")  # 捕获其他异常

    def get_qrcode(self, qr_code_url):
        """
        下载二维码图片并转换为PIL.Image对象
        :param qr_code_url: 二维码的 URL
        :return: PIL.Image 对象
        """
        try:
            response = self.session.get(qr_code_url, timeout=10)  # 发送请求获取二维码
            response.raise_for_status()  # 检查响应状态码
            return Image.open(BytesIO(response.content))  # 将二进制数据转换为图片
        except requests.RequestException as e:
            print(f"下载二维码图片失败：{e}")  # 如果请求失败，打印错误
            raise  # 抛出异常，停止执行

    def wait_for_login(self):
        """等待用户扫码并登录"""
        while self.login_attempts < 10:  # 设置最大登录尝试次数
            time.sleep(5)  # 每隔5秒检查一次登录状态
            try:
                if self.check_login_status():  # 调用检查登录状态的方法
                    print("登录成功！")
                    break  # 登录成功，跳出循环
                else:
                    print("等待扫码或确认登录...")
            except Exception as e:
                print(f"检查登录状态时出现错误：{e}")  # 捕获异常，停止检查
                break
            self.login_attempts += 1

        if self.login_attempts >= 5:
            print("登录失败，尝试次数过多。请检查二维码扫描是否成功。")

    def check_login_status(self):
        """
        检查登录状态，返回是否登录成功
        :return: bool - 登录状态
        """
        try:
            response = self.session.post(self.check_login_url, timeout=10)  # 发送POST请求检查登录
            response.raise_for_status()  # 检查响应状态码
            result = response.json()  # 解析JSON响应
            return result.get("status") == "success"  # 如果状态是success，说明登录成功
        except requests.RequestException as e:
            print(f"检查登录状态失败：{e}")  # 如果请求失败，打印错误
            return False  # 返回登录失败

    def close(self):
        """关闭浏览器并释放资源"""
        if self.driver:
            self.driver.quit()  # 关闭浏览器
            print("浏览器已关闭。")

# 配置参数
QR_CODE_URL = "https://kyfw.12306.cn/otn/login/conf"  # 获取二维码URL
CHECK_LOGIN_URL = "https://kyfw.12306.cn/otn/login/check"  # 检查登录状态URL

# 主程序
if __name__ == "__main__":
    bot = TicketBot(QR_CODE_URL, CHECK_LOGIN_URL)  # 初始化抢票机器人
    try:
        bot.setup_driver()  # 设置浏览器驱动
        bot.login_by_qrcode()  # 执行扫码登录流程
    except Exception as e:
        print(f"程序运行过程中出错：{e}")  # 捕获并输出运行过程中的异常
    finally:
        bot.close()  # 无论是否成功，都关闭浏览器并释放资源
