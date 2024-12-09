from io import BytesIO
import time
from tkinter import Image
import requests
from selenium import webdriver  # Selenium WebDriver 核心库
from selenium.common.exceptions import WebDriverException  # WebDriver 异常类
from selenium.webdriver.edge.service import Service  # 用于管理 Edge WebDriver 的服务类
from webdriver_manager.microsoft import EdgeChromiumDriverManager  # 自动安装 Edge WebDriver
from selenium.webdriver.common.by import By  # 导入 By 模块



class Config:# 配置模块
    CHECK_LOGIN_URL = "https://kyfw.12306.cn/passport/web/checkqr" # 检查登录状态的 API 地址？？？？？？？？



class LoginModule:# 登录模块
    
    
    def __init__(self, check_login_url):# 初始化配置
        
        self.check_login_url = check_login_url
        self.session = requests.Session()#会话实例，用于发送 HTTP 请求
        self.driver = None  #浏览器WebDriver 对象，默认 None
        self.login_attempts = 0 #登录尝试次数，默认从 0 开始。


    def setup_driver(self):# 启动浏览器
        try:
            # 使用 Edge WebDriver
            service = Service(EdgeChromiumDriverManager().install())   # 安装并启动 Edge WebDriver
            self.driver = webdriver.Edge(service=service)  # 创建 Edge 浏览器实例
            print("Edge 浏览器启动成功！")
        except WebDriverException as e: 
            print(f"Edge 浏览器启动失败：{e}")
            raise #抛出异常


    def login_by_qrcode(self):# 扫码登录
        try:
            self.driver.get("https://kyfw.12306.cn/otn/resources/login.html")#加载登录页
            print("正在加载登录页...")
            time.sleep(5)
            qr_code_img = self.driver.find_element(By.ID, "J-qrImg")# 获取二维码图片的 HTML 元素（根据 ID 定位）
            qr_code_url = qr_code_img.get_attribute("src")# 获取二维码图片的 URL（src 属性）
            qr_code_data = self.get_qrcode(qr_code_url)# 调用 get_qrcode 方法，传入二维码 URL，获取二维码数据
            qr_code_data.show()
            print("请使用 12306 APP 扫描二维码登录...")
            self.wait_for_login()
        except NoSuchElementException as e:
            print(f"元素定位失败：{e}")
        except Exception as e:
            print(f"扫码登录过程中出现错误：{e}")


    def get_qrcode(self, qr_code_url):# 下载二维码图片
        try:
            response = self.session.get(qr_code_url, timeout=10) # 使用会话对象的get方法，向指定的二维码URL发起请求，并设置超时时间为10秒
            response.raise_for_status()# 检查HTTP响应状态码
            return Image.open(BytesIO(response.content))# 解析二维码图片
        except requests.RequestException as e:
            print(f"下载二维码图片失败：{e}")
            raise


    def wait_for_login(self):# 循环等待用户完成扫码登录
   
        while self.login_attempts < 10:  # 最大尝试次数为10次
            time.sleep(5)  # 每次检查间隔5秒
        
        # 检查登录状态
            if self.check_login_status():  # 如果检测到登录成功
                print("登录成功！")  # 输出成功信息
                return True  # 返回成功标志
        
        # 如果未登录成功，继续等待
            else:
                print("等待扫码或确认登录...")  # 提示用户继续操作
            
        # 增加登录尝试次数
            self.login_attempts += 1

        
        print("登录失败，尝试次数过多。")  # 输出失败信息
        return False  # 返回失败标志



    def check_login_status(self):# 检查当前登录状态的方法
        try:
            response = self.session.post(self.check_login_url, timeout=10)# 向服务器发送 POST 请求，检查登录状态
            response.raise_for_status()# 如果响应状态码不是 200，则抛出异常
            
            result = response.json()# 将服务器返回的数据解析为JSON
        
            return result.get("status") == "success"# 检查返回的 JSON 数据中 "status" 键的值是否为 "success"
        
        except requests.RequestException as e:# 如果请求过程出现异常，则打印错误信息并返回 False
            print(f"检查登录状态失败：{e}")
     
            return False
        
        
    def close(self):#关闭浏览器
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭。")


class QueryModule:#查询模块
 
    def search_tickets(self, from_station, to_station, date):
        # 访问车票查询页面
        self.driver.get(self.login_page_url)
        time.sleep(3)

        # 填写查询信息
        self.driver.find_element_by_id("fromStationText").click() #出发站
        # 使用 XPath 查找包含指定文本的 <li> 元素，并点击该元素
        self.driver.find_element_by_xpath(f"//li[contains(text(), '{from_station}')]").click()
        time.sleep(1)

        self.driver.find_element_by_id("toStationText").click() #目的站
        self.driver.find_element_by_xpath(f"//li[contains(text(), '{to_station}')]").click()
        time.sleep(1)

        self.driver.find_element_by_id("train_date").send_keys(date) #出发日期
        time.sleep(1)

        self.driver.find_element_by_id("query_ticket").click()
        time.sleep(5)

        # 获取查询结果
        tickets = self.driver.find_elements_by_xpath("//tr[@datatran]")
        ticket_list = []

        for ticket in tickets:
            ticket_info = ticket.text.split("\n")
            ticket_list.append(ticket_info)

        print(f"查询到的车票：{ticket_list}")
        return ticket_list


# 预订模块（示例）
class BookingModule:
    def submit_order(self, ticket):
        print(f"提交订单：{ticket}")
        return {"status": "success", "order_id": 12345}  # 模拟返回数据


# 支付模块（示例）
class PaymentModule:
    def pay_order(self, order_id):
        print(f"支付订单：{order_id}")
        return True  # 模拟支付成功

class Notify:# 通知模块
    @staticmethod
    def send_notification(message):
        print(f"通知：{message}")  # 此处可替换为实际推送逻辑


if __name__ == "__main__":# 程序入口
    # 创建登录、查询、订票、支付、通知模块的实例
    login = LoginModule(Config.CHECK_LOGIN_URL)  # 登录模块，传入登录状态检查URL
    query = QueryModule()  # 查询模块，负责查询票务信息
    booking = BookingModule()  # 订票模块，负责提交订单
    payment = PaymentModule()  # 支付模块，负责支付
    notify = Notify()  # 通知模块，用于发送通知提醒

    try:
        # 设置浏览器驱动
        login.setup_driver()

        # 执行扫码登录，返回登录成功或失败
        if login.login_by_qrcode():
            # 登录成功后，发送成功通知
            notify.send_notification("登录成功！")

            # 查询北京到上海的车票
            tickets = query.search_tickets(params={"from": "北京", "to": "上海"})
            # 过滤出符合条件的硬卧票
            available_tickets = query.filter_tickets(tickets, conditions={"seat": "硬卧"})

            # 如果有符合条件的票
            if available_tickets:
                # 提交订单，抢购第一张符合条件的票
                result = booking.submit_order(available_tickets[0])
                # 如果抢票成功
                if result.get("status") == "success":
                    # 发送抢票成功通知
                    notify.send_notification("抢票成功！请及时支付！")

                    # 尝试支付订单
                    if payment.pay_order(result["order_id"]):
                        # 支付成功通知
                        notify.send_notification("支付成功！")
                    else:
                        # 支付失败通知
                        notify.send_notification("支付失败，请重试！")
    except Exception as e:
        # 捕获程序执行过程中可能发生的任何异常，并打印错误信息
        print(f"程序运行过程中出错：{e}")
    finally:
        # 程序执行完毕后关闭浏览器驱动
        login.close()
