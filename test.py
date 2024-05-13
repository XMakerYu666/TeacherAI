import tkinter as tk
from tkinter import scrolledtext
import pandas as pd


class ScienceTeacherAssistant:
    def __init__(self, master):
        self.master = master
        master.title("AI课程反馈助手")
        self.df = pd.read_excel('data.xlsx')

        # 添加课程下拉菜单
        self.course_label = tk.Label(master, text="选择课程:")
        self.course_label.grid(row=0, column=0)
        self.course_var = tk.StringVar(master)
        self.course_var.set("请选择课程")
        self.course_menu = tk.OptionMenu(master, self.course_var, *self.df['课程'].unique(), command=self.get_answer)
        self.course_menu.grid(row=0, column=1)

        # 添加阶段下拉菜单
        self.stage_label = tk.Label(master, text="选择阶段:")
        self.stage_label.grid(row=0, column=2)
        self.stage_var = tk.StringVar(master)
        self.stage_var.set("请选择阶段")
        self.stage_menu = tk.OptionMenu(master, self.stage_var, *self.df['阶段'].unique(), command=self.get_answer)
        self.stage_menu.grid(row=0, column=3)

        # 添加课时下拉菜单
        self.lesson_label = tk.Label(master, text="选择课时:")
        self.lesson_label.grid(row=0, column=4)
        self.lesson_var = tk.StringVar(master)
        self.lesson_var.set("请选择课时")
        self.lesson_menu = tk.OptionMenu(master, self.lesson_var, *self.df['课时'].unique(), command=self.get_answer)
        self.lesson_menu.grid(row=0, column=5)

        # 获取回答的文本框
        self.answer_text = scrolledtext.ScrolledText(master, width=60, height=10)
        self.answer_text.grid(row=1, column=0, columnspan=6)

    def get_answer(self, *args):
        # 获取选定的课程、阶段和课时
        course = self.course_var.get()
        stage = self.stage_var.get()
        lesson = self.lesson_var.get()
        
        # 根据选定的课程、阶段和课时从 DataFrame 中获取对应的数据
        answer = self.generate_answer(course, stage, lesson)
        
        # 清空文本框内容
        self.answer_text.delete('1.0', tk.END)
        
        # 将答案显示在回答的文本框中
        self.answer_text.insert(tk.END, answer)

    def generate_answer(self, course, stage, lesson):
        # 从 Sheet2 中根据选定的课程、阶段和课时获取对应的数据
        filtered_data = self.df[(self.df['课程'] == course) & (self.df['阶段'] == stage) & (self.df['课时'] == lesson)]
        
        # 如果找到匹配的数据，则生成对应的回答
        if not filtered_data.empty:
            # 这里假设我们想要显示所有匹配的数据，你可以根据需要修改显示的格式
            answer = filtered_data.to_string(index=False)
        else:
            answer = "未找到匹配的数据"
        
        return answer


def main():
    root = tk.Tk()
    app = ScienceTeacherAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()
