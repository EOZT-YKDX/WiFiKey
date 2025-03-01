# -*- coding:utf-8 -*- #

# Author: YKDX
# Version: V1.0.25211
# Date Creation: 2025/2/11-2
# Date Modified: 2025/2/11-2
# Program Name: WK_System_Application_Window(WK_SAW)

import sv_ttk
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

window_size = "640x520"
window_title = "WiFi Key"
home_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\Home_LOGO.png"
eoct_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\EOZT_LOGO.png"
wifi_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\WiFi_LOGO.png"
return_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\Return_ICON.png"
window_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\Window_ICON.ico"
setting_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\Settings_LOGO.png"
codebook_icon_path = r"C:\programming\Other-Project\素材\WiFi项目\Codebook_LOGO.png"


# 退出事件
def window_quit() -> None:
    """
    退出事件
    参数:
        None
    返回:
        None
    """

    if messagebox.askokcancel(title=window_title, message=f"是否退出{window_title}？", icon="question", default="ok"):
        window.destroy()


# 窗口居中
def center_window(window) -> None:
    """
    窗口居中

    参数:
        window (tk.Tk): 窗口对象

    返回:
        None
    """

    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"+{x}+{y}")
    pass


# 侧边栏按钮
def sidebar_button(side: str, width: int, height: int, icon_path: str, command=None):
    """
    创建侧边栏图标按钮

    参数:
        side (str): 按钮放置位置，可选值为 "TOP" 或 "BOTTOM"
        width (int): 按钮宽度
        height (int): 按钮高度
        icon_path (str): 图标文件路径
        command (function): 按钮点击事件处理函数，默认为 None

    返回:
        None
    """

    try:
        # 打开图像文件
        image = Image.open(icon_path)
        # 调整图像大小
        image = image.resize((width, height))
        # 将PIL图像转换为Tkinter可用的图像对象
        sidebar_icon = ImageTk.PhotoImage(image)
    except FileNotFoundError:
        print(f"无法加载图像: {icon_path}")
    else:
        button = tk.Button(
            bg="#18191B",
            borderwidth=0,
            cursor="hand2",
            master=sidebar,
            command=None,
            image=sidebar_icon,
            activebackground="#18191B",
        )
        button.pack(
            pady=0,
            padx=0,
            side=side,
            anchor="nw",
        )
        button.image = sidebar_icon
        return button


# 设置按钮事件
def setting_events(button) -> None:
    button.config(bg="#FF0000", relief="sunken")
    pass


# 创建主窗口
window = tk.Tk()

# 设置窗口标题
window.title(window_title)
# 设置窗口大小
window.geometry(window_size)
# 设置窗口图标
window.iconbitmap(window_icon_path)
# 设置窗口透明度
window.attributes("-alpha", 0.95)
# 禁止调整窗口大小
window.resizable(False, False)
# 窗口退出提示
window.protocol("WM_DELETE_WINDOW", func=window_quit)

# 窗口居中
center_window(window=window)

# 封面
cover = tk.Canvas(
    master=window,
    highlightthickness=0,
    height=window.winfo_height(),
    width=window.winfo_width() - 55,
)
cover.pack(side=tk.RIGHT, fill=tk.X)

# 侧边栏
sidebar = tk.Canvas(
    width=55,
    bg="#18191B",
    master=window,
    highlightthickness=0,
    height=window.winfo_height(),
)
# 主页按钮
sidebar_button(
    width=50,
    height=50,
    side=tk.TOP,
    icon_path=home_icon_path,
)
# WiFi按钮
sidebar_button(
    width=50,
    height=50,
    side=tk.TOP,
    icon_path=wifi_icon_path,
)
# 密码本按钮
sidebar_button(
    width=50,
    height=50,
    side=tk.TOP,
    icon_path=codebook_icon_path,
)
# 设置按钮
setting_button = sidebar_button(
    width=50,
    height=50,
    side=tk.BOTTOM,
    icon_path=setting_icon_path,
)
setting_button.bind("<Enter>", lambda event: setting_events(button=setting_button))
sidebar.pack(side=tk.LEFT, fill=tk.Y)

# 设置成暗色主题
sv_ttk.set_theme("dark")
# 进入主事件循环
window.mainloop()
