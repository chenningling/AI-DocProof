#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导出对话框模块
负责日志导出界面的展示和交互
"""

import sys
import os
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QRadioButton, QButtonGroup,
                            QFileDialog, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExportDialog(QDialog):
    """导出对话框类，负责日志导出界面的展示和交互"""
    
    # 定义信号
    exportRequested = pyqtSignal(str, bool)
    
    def __init__(self, default_path=None, parent=None):
        """
        初始化导出对话框
        
        Args:
            default_path: 默认导出路径
            parent: 父窗口
        """
        super().__init__(parent)
        self.default_path = default_path
        self.initUI()
        
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle('导出校对日志')
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 添加标题标签
        title_label = QLabel('选择导出内容')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; margin-bottom: 10px;')
        main_layout.addWidget(title_label)
        
        # 创建单选按钮组
        self.radio_group = QButtonGroup(self)
        
        # 导出全部日志选项
        self.all_radio = QRadioButton('导出全部日志')
        self.all_radio.setChecked(True)
        main_layout.addWidget(self.all_radio)
        self.radio_group.addButton(self.all_radio, 1)
        
        # 仅导出错误日志选项
        self.errors_radio = QRadioButton('仅导出错误日志')
        main_layout.addWidget(self.errors_radio)
        self.radio_group.addButton(self.errors_radio, 2)
        
        # 添加间隔
        main_layout.addSpacing(20)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 导出按钮
        self.export_button = QPushButton('导出')
        self.export_button.clicked.connect(self.export_logs)
        
        # 取消按钮
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.reject)
        
        # 添加按钮到按钮布局
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加按钮布局到主布局
        main_layout.addLayout(button_layout)
        
        # 设置对话框布局
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #202124;
            }
            QRadioButton {
                font-size: 14px;
                color: #202124;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:checked {
                background-color: #1A73E8;
                border: 2px solid #1A73E8;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #5F6368;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #1A73E8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1967D2;
            }
            QPushButton:pressed {
                background-color: #185ABC;
            }
            QPushButton#cancel_button {
                background-color: #FFFFFF;
                color: #1A73E8;
                border: 1px solid #DADCE0;
            }
            QPushButton#cancel_button:hover {
                background-color: #F1F3F4;
            }
        """)
        
        # 设置按钮ID以便应用样式
        self.cancel_button.setObjectName("cancel_button")
        
    def export_logs(self):
        """导出日志"""
        # 确定是否只导出错误日志
        only_errors = self.errors_radio.isChecked()
        
        # 确定默认文件名
        default_name = "校对日志_全部.txt" if not only_errors else "校对日志_错误.txt"
        
        # 确定默认路径
        default_dir = os.path.dirname(self.default_path) if self.default_path else ""
        default_path = os.path.join(default_dir, default_name)
        
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存日志文件",
            default_path,
            "文本文件 (*.txt)"
        )
        
        if file_path:
            # 发送导出请求信号
            self.exportRequested.emit(file_path, only_errors)
            self.accept()


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dialog = ExportDialog("C:/test/document.docx")
    
    if dialog.exec_():
        print("导出请求已发送")
    else:
        print("取消导出")
