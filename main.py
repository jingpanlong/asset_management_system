import sys
import os
from PyQt5.QtWidgets import QApplication

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login import LoginDialog
from ui.main_window import MainWindow

def main():
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("资产管理系统")
    
    while True:  # 使用循环支持登出后重新登录
        # 显示登录对话框
        login_dialog = LoginDialog()
        if login_dialog.exec_():
            # 登录成功，显示主窗口
            main_window = MainWindow(login_dialog.user)
            main_window.show()
            # 等待主窗口关闭
            app.exec_()
        else:
            # 登录取消，退出程序
            sys.exit(0)

if __name__ == "__main__":
    main()
