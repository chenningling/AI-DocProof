#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI文档校对工具主程序
负责启动整个应用程序
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from src.gui.main_window import MainWindow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_docproof.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """程序入口函数"""
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'icon.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
