# -*- coding: utf-8 -*-
__author__ = 'luhui.liu'
import requests
from scrapy.selector import Selector
import pymysql

conn = pymysql.connect(host="",user="",passwd="",db="",charset="utf8")
cur = conn.cursor()

def craw_ips():
    headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
    for i in range(1568):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers = headers)

        selector = Selector(re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in ip_list[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒"[0]))
            all_text = tr.css("td::text").extract()

            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]

            ip_list.append((ip,port,proxy_type,speed))
        
    for ip in ip_list:
        cur.execute(
            "insert proxy_ip(ip,port,speed,proxy_type) values ('{0}','{1}',{2},'HTTP'）"(
                ip_list[0], ip_list[1], ip_list[3]
            )
        )
        conn.commit()
    print(re.text)
class GetIP(object):
    def delete_ip(self,ip):
        #从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip WHERE ip='{0}'
        """.format(ip)
        cur.execute(delete_sql)
        conn.commit()
        return True
    def judge_ip(self,ip,port):
        #判断ip是否合法
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip,port)
        try:
            proxy_dict = {
                "http":proxy_url
            }
            response = requests.get(http_url,proxies=proxy_dict)
            return True
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False
    def get_random_ip(self):
        #从数据库中随机取出一个ip
        random_sql = """
              SELECT ip,port FROM proxy_ip ORDER BY RAND() LIMIT 1      
              """
        result = cur.execute(random_sql)
        for ip_info in cur.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.judge_ip(ip,port)
            if judge_re:
                return "http://{0}:{1}".format(ip,port)
            else:
                return self.get_random_ip()

if __name__ == '__main__':
    craw_ips()

