# 导入需要的库
import requests  # 用于发送HTTP请求，获取网页数据
from PIL import Image  # 用于处理图像，尤其是验证码图片
import pytesseract  # 用于图像文字识别（OCR），主要用来识别验证码
from io import BytesIO  # 用于处理字节数据，转换为图像
from selenium import webdriver  # 用于自动化浏览器操作
import time  # 用于控制程序暂停时间，模拟用户等待时间


#模拟登录
class TicketBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.driver = webdriver.Chrome()  # 使用 Chrome 浏览器
        self.login_url = "https://kyfw.12306.cn/otn/login/init"
        self.login_page_url = "https://kyfw.12306.cn/otn/leftTicket/init"

    def login(self):
        # 打开 12306 登录页面
        self.driver.get(self.login_url)
        time.sleep(3)

        # 获取验证码图片
        captcha_img = self.driver.find_element_by_xpath("//img[@id='J-login-img']")
        captcha_url = captcha_img.get_attribute('src')
        captcha_data = self.get_captcha(captcha_url)

        # 识别验证码
        captcha_text = self.recognize_captcha(captcha_data)
        print(f"验证码识别结果：{captcha_text}")

        # 输入账号、密码和验证码
        self.driver.find_element_by_id("J-userName").send_keys(self.username)
        self.driver.find_element_by_id("J-password").send_keys(self.password)
        self.driver.find_element_by_id("J-captcha").send_keys(captcha_text)
        
        # 点击登录
        self.driver.find_element_by_id("J-login").click()
        time.sleep(5)

        print("登录成功！")

    def get_captcha(self, url):
        response = self.session.get(url)
        return Image.open(BytesIO(response.content))

    def recognize_captcha(self, captcha_img):
        # 使用 pytesseract 识别验证码
        return pytesseract.image_to_string(captcha_img, config='--psm 6')

    def close(self):
        self.driver.quit()

# 实例化并登录
bot = TicketBot('your_username', 'your_password')
bot.login()
bot.close()
