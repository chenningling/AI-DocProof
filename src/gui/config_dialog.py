#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置对话框模块
负责API配置界面的展示和交互
"""

import sys
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigDialog(QDialog):
    """配置对话框类，负责API配置界面的展示和交互"""
    
    # 定义信号
    configUpdated = pyqtSignal(dict)
    
    def __init__(self, config=None, parent=None):
        """
        初始化配置对话框
        
        Args:
            config: 当前配置信息
            parent: 父窗口
        """
        super().__init__(parent)
        self.config = config or {}
        self.initUI()
        
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle('API配置')
        self.setFixedSize(520, 230)  # 进一步减小窗口大小，使布局更紧凑
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)  # 减小上下边距
        main_layout.setSpacing(10)  # 减小间距
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 标签右对齐
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # 字段可扩展
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # 不换行
        form_layout.setVerticalSpacing(12)  # 减小垂直间距
        form_layout.setHorizontalSpacing(8)  # 减小水平间距
        
        # API URL输入框
        self.api_url_edit = QLineEdit(self.config.get('api_url', ''))
        self.api_url_edit.setPlaceholderText('例如：https://api.deepseek.com/chat/completions')
        self.api_url_edit.setFixedHeight(28)  # 减小输入框高度
        form_layout.addRow('API URL:', self.api_url_edit)
        
        # 模型名称输入框
        self.model_edit = QLineEdit(self.config.get('model', ''))
        self.model_edit.setPlaceholderText('例如：deepseek-chat')
        self.model_edit.setFixedHeight(28)  # 减小输入框高度
        form_layout.addRow('模型名称:', self.model_edit)
        
        # API Key输入框
        self.api_key_edit = QLineEdit(self.config.get('api_key', ''))
        self.api_key_edit.setPlaceholderText('输入您的API密钥')
        self.api_key_edit.setEchoMode(QLineEdit.Password)  # 密码模式
        self.api_key_edit.setFixedHeight(28)  # 减小输入框高度
        form_layout.addRow('API Key:', self.api_key_edit)
        
        # 保存System Prompt值，但不显示输入框
        self.system_prompt = self.config.get('system_prompt', '')
        
        # 添加表单布局到主布局
        main_layout.addLayout(form_layout)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 8, 0, 0)  # 减小上边距
        
        # 测试连接按钮
        self.test_button = QPushButton('测试连接')
        self.test_button.clicked.connect(self.test_connection)
        self.test_button.setFixedHeight(32)  # 减小按钮高度
        self.test_button.setMinimumWidth(90)  # 减小按钮宽度
        self.test_button.setObjectName("test_button")  # 设置对象名称以应用特定样式
        
        # 保存按钮
        self.save_button = QPushButton('保存')
        self.save_button.clicked.connect(self.save_config)
        self.save_button.setFixedHeight(32)  # 减小按钮高度
        self.save_button.setMinimumWidth(75)  # 减小按钮宽度
        
        # 取消按钮
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedHeight(32)  # 减小按钮高度
        self.cancel_button.setMinimumWidth(75)  # 减小按钮宽度
        
        # 添加按钮到按钮布局
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加说明文字和链接
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 5, 0, 5)  # 设置边距
        
        # 将说明文字和链接合并为一句话
        info_text = QLabel()
        info_text.setOpenExternalLinks(True)
        info_text.setText('推荐使用DeepSeek模型，也可更换其他模型。<a href="https://platform.deepseek.com/api_keys" style="color: #1A73E8; text-decoration: none;">👉点击获取 DeepSeek API key</a>')
        info_text.setStyleSheet('color: #5F6368; font-size: 12px;')
        
        info_layout.addWidget(info_text)
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout)
        
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
                font-size: 14px;
                color: #202124;
                padding-right: 10px;
            }
            QLineEdit {
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 6px 8px;
                background-color: #FFFFFF;
                color: #202124;
                font-size: 14px;
                min-width: 360px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #1A73E8;
            }
            QPushButton {
                background-color: #1A73E8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 14px;
                min-width: 80px;
                margin: 0 3px;
            }
            QPushButton:hover {
                background-color: #1967D2;
            }
            QPushButton:pressed {
                background-color: #185ABC;
            }
            QPushButton#test_button {
                background-color: #34A853;  /* 绿色按钮 */
                color: white;
                border: none;
            }
            QPushButton#test_button:hover {
                background-color: #2E8B57;  /* 悬停时的颜色 */
            }
            QPushButton#test_button:pressed {
                background-color: #228B22;  /* 按下时的颜色 */
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
        
    def get_config(self):
        """
        获取当前配置
        
        Returns:
            dict: 当前配置信息
        """
        return {
            'api_url': self.api_url_edit.text().strip(),
            'model': self.model_edit.text().strip(),
            'api_key': self.api_key_edit.text().strip(),
            'system_prompt': self.system_prompt  # 使用保存的system_prompt值
        }
        
    def save_config(self):
        """保存配置"""
        config = self.get_config()
        
        # 验证配置
        if not config['api_url']:
            QMessageBox.warning(self, '配置错误', 'API URL不能为空')
            return
            
        if not config['model']:
            QMessageBox.warning(self, '配置错误', '模型名称不能为空')
            return
            
        if not config['api_key']:
            QMessageBox.warning(self, '配置错误', 'API Key不能为空')
            return
            
        # 发送配置更新信号
        self.configUpdated.emit(config)
        
        # 关闭对话框
        self.accept()
        
    def test_connection(self):
        """测试API连接"""
        config = self.get_config()
        
        # 验证配置
        if not config['api_url'] or not config['model'] or not config['api_key']:
            QMessageBox.warning(self, '配置错误', '请填写完整的API配置信息')
            return
            
        # 通知父窗口测试连接
        self.parent().test_api_connection(config)


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试配置
    test_config = {
        'api_url': 'https://api.deepseek.com/chat/completions',
        'model': 'deepseek-chat',
        'api_key': 'your_api_key_here',
        'system_prompt': """作为一个细致耐心的文字秘书，对下面的句子进行错别字检查，按如下结构以 JOSN 格式输出：
{
"content_0":"原始句子",
"wrong":true,//是否有需要被修正的错别字，布尔类型
"annotation":"",//批注内容，string类型。如果wrong为true给出修正的解释；如果 wrong 字段为 false，则为空值
"content_1":""//修改后的句子，string类型。如果wrong为false则留空
}"""
    }
    
    dialog = ConfigDialog(test_config)
    
    if dialog.exec_():
        print("配置已保存:", dialog.get_config())
    else:
        print("取消配置")
