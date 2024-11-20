import requests  # 用于发送 HTTP 请求
import time  # 用于设置等待时间
from PIL import Image  # 用于处理二维码图片
from io import BytesIO  # 用于将二进制数据转换为文件流
from selenium import webdriver  # 使用 Selenium 控制浏览器操作
from selenium.webdriver.chrome.service import Service  # 导入 Service
from selenium.common.exceptions import NoSuchElementException, WebDriverException



##登录模块
class TicketBot:
    def __init__(self, driver_path, qr_code_url, check_login_url):
        """
        初始化抢票机器人
        :param driver_path: ChromeDriver 的路径
        :param qr_code_url: 获取二维码的接口 URL
        :param check_login_url: 检查登录状态的接口 URL
        """
        self.driver_path = driver_path
        self.qr_code_url = qr_code_url
        self.check_login_url = check_login_url
        self.session = requests.Session()
        self.driver = None

    def setup_driver(self):
        """初始化浏览器驱动"""
        try:
            service = Service(executable_path=self.driver_path)
            self.driver = webdriver.Chrome(service=service)
            print("浏览器启动成功！")
        except WebDriverException as e:
            print(f"浏览器启动失败：{e}")
            raise

    def login_by_qrcode(self):
        """通过扫码登录"""
        try:
            # 打开登录页面
            self.driver.get("https://kyfw.12306.cn/otn/resources/login.html")
            time.sleep(3)

            # 定位并获取二维码图片
            qr_code_img = self.driver.find_element("id", "J-login-img")
            qr_code_url = qr_code_img.get_attribute("src")
            qr_code_data = self.get_qrcode(qr_code_url)

            # 展示二维码图片
            qr_code_data.show()
            print("请使用 12306 APP 扫描二维码登录...")

            # 检查登录状态
            self.wait_for_login()
        except NoSuchElementException as e:
            print(f"元素定位失败：{e}")
        except Exception as e:
            print(f"扫码登录过程中出现错误：{e}")

    def get_qrcode(self, qr_code_url):
        """
        下载二维码图片
        :param qr_code_url: 二维码的 URL
        :return: PIL.Image 对象
        """
        try:
            response = self.session.get(qr_code_url, timeout=10)
            response.raise_for_status()  # 检查 HTTP 状态码
            return Image.open(BytesIO(response.content))
        except requests.RequestException as e:
            print(f"下载二维码图片失败：{e}")
            raise

    def wait_for_login(self):
        """等待用户扫码并登录"""
        while True:
            time.sleep(5)  # 每隔5秒检查一次
            try:
                if self.check_login_status():
                    print("登录成功！")
                    break
                else:
                    print("等待扫码或确认登录...")
            except Exception as e:
                print(f"检查登录状态时出现错误：{e}")
                break

    def check_login_status(self):
        """
        检查登录状态
        :return: bool
        """
        try:
            response = self.session.post(self.check_login_url, timeout=10)
            response.raise_for_status()  # 检查 HTTP 状态码
            result = response.json()
            return result.get("status") == "success"
        except requests.RequestException as e:
            print(f"检查登录状态失败：{e}")
            return False

    def close(self):
        """关闭浏览器并释放资源"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭。")

# 配置参数
CHROMEDRIVER_PATH = r'C:\Users\asus\Desktop\Grab-train-tickets\chromedriver-win64\chromedriver-win64\chromedriver.exe'
QR_CODE_URL = "https://kyfw.12306.cn/otn/login/conf"
CHECK_LOGIN_URL = "https://kyfw.12306.cn/otn/login/check"

# 主程序
if __name__ == "__main__":
    bot = TicketBot(CHROMEDRIVER_PATH, QR_CODE_URL, CHECK_LOGIN_URL)
    try:
        bot.setup_driver()
        bot.login_by_qrcode()
    except Exception as e:
        print(f"程序运行过程中出错：{e}")
    finally:
        bot.close()
