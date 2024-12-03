##查询模块
import time


class QueryModule:
 
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


    

