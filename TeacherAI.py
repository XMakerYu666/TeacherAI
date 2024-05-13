import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
import json
import _thread as thread
import os
import time
import base64
import datetime
import hashlib
import hmac
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websocket
import openpyxl
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

#星火认知大模型v3.5的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = '54deebc4'
SPARKAI_API_SECRET = '07d9f8da7c0f9a4416657d5d947e7993'
SPARKAI_API_KEY = 'd849ba02df58723f7dcfa6ea437d1b01'
#星火认知大模型v3.5的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    global content
    global content1
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        content1=content1+content
        print(content,end='')
        if status == 2:
            print("#### 关闭会话")
            ws.close()
    


def gen_params(appid, query, domain):
    """
    通过appid和用户的提问来生成请参数
    """

    data = {
        "header": {
            "app_id": appid,
            "uid": "1234",           
            # "patch_id": []    #接入微调模型，对应服务发布后的resourceid          
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 4096,
                "auditing": "default",
            }
        },
        "payload": {
            "message": {
                "text": [{"role": "user", "content": query}]
            }
        }
    }
    return data


def xinghuoapi(appid, api_secret, api_key, gpt_url, domain, query):
    wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()

    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.query = query
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})



class ScienceTeacherAssistant:
    def __init__(self, master):
        self.master = master
        master.title("AI课程反馈助手")
        self.df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
        self.re = pd.read_excel('data.xlsx', sheet_name='Sheet2')
        pd.set_option('display.max_colwidth', None)


      # 添加课程下拉菜单
        self.course_label = tk.Label(master, text="选择课程:")
        self.course_label.grid(row=0,column=0)
        self.course_var = tk.StringVar(master)
        self.course_var.set("智能硬件编程")
        self.course_menu = tk.OptionMenu(master, self.course_var, *self.df['课程'].unique(),command=self.get_answer)
        self.course_menu.grid(row=0,column=1)

        # 添加阶段下拉菜单
        self.stage_label = tk.Label(master, text="选择阶段:")
        self.stage_label.grid(row=0,column=2)
        self.stage_var = tk.StringVar(master)
        self.stage_var.set("Level1")
        self.stage_menu = tk.OptionMenu(master, self.stage_var, *self.df['阶段'].unique(),command=self.get_answer)
        self.stage_menu.grid(row=0,column=3)

        # 添加课时下拉菜单
        self.lesson_label = tk.Label(master, text="选择课时:")
        self.lesson_label.grid(row=0,column=4)
        self.lesson_var = tk.StringVar(master)
        self.lesson_var.set("1")
        self.lesson_menu = tk.OptionMenu(master, self.lesson_var, *self.df['课时'].unique(),command=self.get_answer)
        self.lesson_menu.grid(row=0,column=5)

        # 获取回答的文本框
        self.answer_text = scrolledtext.ScrolledText(master, width=60, height=20, wrap=tk.WORD)
        self.answer_text.grid(row=1,column=0,columnspan=6)






    def get_answer(self, event=None):
        # 这里是一个简单的示例，你需要根据实际需求编写回答逻辑
        course = self.course_var.get()
        stage = self.stage_var.get()
        lesson = self.lesson_var.get()
        answer = self.generate_answer(course, stage, lesson)
                # 清空文本框内容
        self.answer_text.delete('1.0', tk.END)
        



    def generate_answer(self, course, stage, lesson):
        filtered_data = self.re[(self.re['课程'] == course) & (self.re['阶段'] == stage) & (self.re['课时'] == int(lesson))]
        #print((self.re['课程'] == course) , (self.re['阶段'] == stage), (self.re['课时'] == lesson))
        #print(course,stage,lesson)
        #print(filtered_data)
        
        # 如果找到匹配的数据，则生成对应的回答
        if not filtered_data.empty:
            # 这里假设我们想要显示所有匹配的数据，你可以根据需要修改显示的格式
            answer = filtered_data["课程内容"].to_string(index=False, header=False)
        else:
            answer = "未找到匹配的数据"
        xinghuoapi(
            appid="54deebc4",
            api_secret="07d9f8da7c0f9a4416657d5d947e7993",
            api_key="d849ba02df58723f7dcfa6ea437d1b01",

            #appid、api_secret、api_key三个服务认证信息请前往开放平台控制台查看（https://console.xfyun.cn/services/bm35）
            gpt_url="wss://spark-api.xf-yun.com/v3.5/chat",
            # Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v3.0环境的地址
            # Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址
            # Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址
            domain="generalv3.5",
            # domain = "generalv3"    # v3.0版本
            # domain = "generalv2"    # v2.0版本
            # domain = "general"    # v2.0版本
            query="我是一名青少年科创教育老师，请结合课程内容写一个课程反馈,两百字以内："+answer
        )
        
        return content1

def main():
    root = tk.Tk()
    app = ScienceTeacherAssistant(root)
    root.mainloop()

if __name__ == "__main__":

  
    main()





