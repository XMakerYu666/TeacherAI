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

        
        return answer

def main():
    root = tk.Tk()
    app = ScienceTeacherAssistant(root)
    root.mainloop()

if __name__ == "__main__":

    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content='你好呀'
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    for mess in a:
        print(mess)

    main()





