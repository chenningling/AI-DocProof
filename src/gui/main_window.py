#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块
负责主界面的展示和交互
"""

import sys
import os
import logging
import threading
import time
import subprocess
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QWidget, QTextEdit,
                            QProgressBar, QMessageBox, QApplication,
                            QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QTextCursor

from src.gui.config_dialog import ConfigDialog
from src.gui.export_dialog import ExportDialog
from src.config_manager import ConfigManager
from src.api_client import ApiClient
from src.doc_processor import DocProcessor
from src.log_manager import LogManager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProofreadWorker(QThread):
    """校对工作线程，负责在后台执行校对任务"""
    
    # 定义信号
    progressUpdated = pyqtSignal(int, int)  # 当前进度，总数
    logUpdated = pyqtSignal(str)  # 日志更新
    finished = pyqtSignal(bool, str)  # 是否成功，保存路径或错误信息
    
    def __init__(self, file_path, config, log_manager, parent=None):
        """
        初始化校对工作线程
        
        Args:
            file_path: 文档路径
            config: API配置
            log_manager: 日志管理器实例
            parent: 父对象
        """
        super().__init__(parent)
        self.file_path = file_path
        self.config = config
        self.log_manager = log_manager  # 使用传入的日志管理器
        self.is_running = True
        
    def run(self):
        """执行校对任务"""
        try:
            # 初始化组件
            doc_processor = DocProcessor(self.file_path)
            api_client = ApiClient(self.config)
            # 使用传入的日志管理器而不是创建新的实例
            
            # 加载文档
            if not doc_processor.load_document():
                self.finished.emit(False, "加载文档失败")
                return
                
            # 分割句子
            sentences = doc_processor.split_into_sentences()
            if not sentences:
                self.finished.emit(False, "文档中没有找到句子")
                return
                
            # 开始记录日志
            self.log_manager.start_logging()
            
            # 校对每个句子
            total = len(sentences)
            for i, sentence in enumerate(sentences):
                # 检查是否被停止
                if not self.is_running:
                    self.finished.emit(False, "校对已停止")
                    return
                    
                # 更新进度
                self.progressUpdated.emit(i + 1, total)
                
                # 校对句子
                success, result = api_client.proofread_sentence(sentence)
                
                if success:
                    # 处理校对结果
                    if result['wrong']:
                        # 添加批注
                        doc_processor.add_comment(i, result['annotation'])
                        # 记录日志
                        log_text = self.log_manager.log_sentence(sentence, result, True)
                    else:
                        # 记录日志
                        log_text = self.log_manager.log_sentence(sentence, result, False)
                else:
                    # 记录错误
                    log_text = self.log_manager.log_error(sentence, result)
                    
                # 发送日志更新信号
                self.logUpdated.emit(log_text)
                
                # 短暂暂停，避免API请求过于频繁
                time.sleep(0.5)
                
            # 保存文档
            success, save_path = doc_processor.save_document()
            
            if success:
                # 完成日志记录
                summary = self.log_manager.finish_logging(save_path)
                self.logUpdated.emit(summary)
                self.finished.emit(True, save_path)
            else:
                self.finished.emit(False, save_path)
                
        except Exception as e:
            logger.error(f"校对过程发生错误: {str(e)}")
            self.finished.emit(False, f"校对过程发生错误: {str(e)}")
            
    def stop(self):
        """停止校对任务"""
        self.is_running = False


class MainWindow(QMainWindow):
    """主窗口类，负责主界面的展示和交互"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.api_client = ApiClient(self.config_manager.get_config())
        self.log_manager = LogManager()
        
        # 状态变量
        self.file_path = None
        self.last_directory = os.path.expanduser("~")  # 默认为用户主目录
        self.worker = None
        self.is_proofreading = False
        
        # 初始化界面
        self.initUI()
        
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle('AI文档校对工具')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部区块
        top_layout = QHBoxLayout()
        
        # 文件选择区域
        file_label = QLabel('文档:')
        self.file_path_label = QLabel('未选择文档')
        self.file_path_label.setStyleSheet('color: #5F6368;')
        self.select_file_button = QPushButton('选择文档')
        self.select_file_button.clicked.connect(self.select_file)
        
        top_layout.addWidget(file_label)
        top_layout.addWidget(self.file_path_label, 1)
        top_layout.addWidget(self.select_file_button)
        
        # 模型配置按钮
        self.config_button = QPushButton('模型配置')
        self.config_button.clicked.connect(self.show_config_dialog)
        top_layout.addWidget(self.config_button)
        
        # 添加顶部区块到主布局
        main_layout.addLayout(top_layout)
        
        # 创建中间区块（日志显示区域）
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #202124;
                font-size: 14px;
            }
        """)
        main_layout.addWidget(self.log_text, 1)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #DADCE0;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #1A73E8;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 创建底部区块
        bottom_layout = QHBoxLayout()
        
        # 开始校对按钮
        self.start_button = QPushButton('开始校对')
        self.start_button.clicked.connect(self.start_proofreading)
        self.start_button.setEnabled(False)
        
        # 停止校对按钮
        self.stop_button = QPushButton('停止校对')
        self.stop_button.clicked.connect(self.stop_proofreading)
        self.stop_button.setEnabled(False)
        
        # 导出记录按钮
        self.export_button = QPushButton('导出记录')
        self.export_button.clicked.connect(self.show_export_dialog)
        self.export_button.setEnabled(False)
        
        # 添加按钮到底部布局
        bottom_layout.addWidget(self.start_button)
        bottom_layout.addWidget(self.stop_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.export_button)
        
        # 添加底部区块到主布局
        main_layout.addLayout(bottom_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QLabel {
                font-size: 14px;
                color: #202124;
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
            QPushButton:disabled {
                background-color: #BDC1C6;
                color: #FFFFFF;
            }
            QPushButton#config_button, QPushButton#export_button {
                background-color: #FFFFFF;
                color: #1A73E8;
                border: 1px solid #DADCE0;
            }
            QPushButton#config_button:hover, QPushButton#export_button:hover {
                background-color: #F1F3F4;
            }
            QPushButton#stop_button {
                background-color: #EA4335;
            }
            QPushButton#stop_button:hover {
                background-color: #D93025;
            }
        """)
        
        # 设置按钮ID以便应用样式
        self.config_button.setObjectName("config_button")
        self.export_button.setObjectName("export_button")
        self.stop_button.setObjectName("stop_button")
        
        # 显示欢迎信息
        self.log_text.append("欢迎使用AI文档校对工具！\n")
        self.log_text.append("请选择需要校对的Word文档，并配置API信息。\n")
        
        # 检查配置
        config = self.config_manager.get_config()
        if not config.get('api_key'):
            self.log_text.append("提示：您尚未配置API信息，请点击\"模型配置\"按钮进行配置。\n")
        
    def select_file(self):
        """选择文档文件"""
        # 使用上次选择的目录作为初始目录
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Word文档",
            self.last_directory,  # 使用上次选择的目录
            "Word文档 (*.docx *.doc)"
        )
        
        if file_path:
            self.file_path = file_path
            # 更新上次选择的目录
            self.last_directory = os.path.dirname(file_path)
            self.file_path_label.setText(os.path.basename(file_path))
            self.start_button.setEnabled(True)
            self.log_text.append(f"已选择文档: {file_path}\n")
            
    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.config_manager.get_config(), self)
        dialog.configUpdated.connect(self.update_config)
        dialog.exec_()
        
    def update_config(self, config):
        """
        更新配置
        
        Args:
            config: 新的配置信息
        """
        self.config_manager.update_config(config)
        self.api_client.update_config(config)
        self.log_text.append("API配置已更新\n")
        
    def test_api_connection(self, config):
        """
        测试API连接
        
        Args:
            config: API配置信息
        """
        # 创建临时API客户端
        temp_client = ApiClient(config)
        
        # 显示等待消息
        self.log_text.append("正在测试API连接...\n")
        QApplication.processEvents()
        
        # 测试连接
        connected, message = temp_client.check_connection()
        
        if connected:
            QMessageBox.information(self, "连接测试", "API连接测试成功！")
            self.log_text.append("API连接测试成功\n")
        else:
            QMessageBox.warning(self, "连接测试", f"API连接测试失败：{message}")
            self.log_text.append(f"API连接测试失败：{message}\n")
            
    def start_proofreading(self):
        """开始校对文档"""
        # 检查文档是否已选择
        if not self.file_path:
            QMessageBox.warning(self, "错误", "请先选择要校对的文档")
            return
            
        # 检查API配置
        config = self.config_manager.get_config()
        valid, msg = self.config_manager.validate_config()
        
        if not valid:
            QMessageBox.warning(self, "配置错误", f"API配置无效：{msg}\n请先完成API配置")
            self.show_config_dialog()
            return
            
        # 清空日志显示
        self.log_text.clear()
        self.log_text.append("开始校对文档...\n")
        
        # 更新UI状态
        self.is_proofreading = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.select_file_button.setEnabled(False)
        self.config_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # 创建并启动校对线程
        # 将主窗口的日志管理器传给校对线程
        self.worker = ProofreadWorker(self.file_path, self.config_manager.get_config(), self.log_manager)
        self.worker.progressUpdated.connect(self.update_progress)
        self.worker.logUpdated.connect(self.update_log)
        self.worker.finished.connect(self.proofreading_finished)
        
        # 启动工作线程
        self.worker.start()
        
    def stop_proofreading(self):
        """停止校对文档"""
        if self.worker and self.is_proofreading:
            self.log_text.append("正在停止校对...\n")
            self.worker.stop()
            
    def update_progress(self, current, total):
        """
        更新进度条
        
        Args:
            current: 当前进度
            total: 总数
        """
        percentage = int(current * 100 / total)
        self.progress_bar.setValue(percentage)
        
    def update_log(self, log_text):
        """
        更新日志显示
        
        Args:
            log_text: 日志文本
        """
        self.log_text.append(log_text)
        # 滚动到底部
        self.log_text.moveCursor(QTextCursor.End)
        
    def proofreading_finished(self, success, message):
        """
        校对完成处理
        
        Args:
            success: 是否成功
            message: 保存路径或错误信息
        """
        self.is_proofreading = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.select_file_button.setEnabled(True)
        self.config_button.setEnabled(True)
        self.export_button.setEnabled(True)
        
        if success:
            self.log_text.append(f"校对完成！文档已保存至: {message}\n")
            
            # 创建自定义消息框，带有“打开”按钮
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("校对完成")
            msg_box.setText(f"文档校对已完成，并保存至:\n{message}")
            msg_box.setIcon(QMessageBox.Information)
            
            # 添加“打开”和“确定”按钮
            open_button = msg_box.addButton("打开文档", QMessageBox.ActionRole)
            ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
            msg_box.setDefaultButton(ok_button)
            
            # 显示消息框并处理结果
            msg_box.exec_()
            
            # 如果点击了“打开”按钮
            if msg_box.clickedButton() == open_button:
                self.open_document(message)
        else:
            self.log_text.append(f"校对失败: {message}\n")
            QMessageBox.warning(self, "校对失败", f"文档校对失败: {message}")
            
    def open_document(self, file_path):
        """
        打开文档
        
        Args:
            file_path: 文档路径
        """
        try:
            # 根据不同的操作系统使用不同的命令打开文档
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            elif sys.platform == 'win32':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
                
            self.log_text.append(f"已打开文档: {file_path}\n")
        except Exception as e:
            self.log_text.append(f"打开文档失败: {str(e)}\n")
            QMessageBox.warning(self, "打开失败", f"无法打开文档: {str(e)}")
    
    def show_export_dialog(self):
        """显示导出对话框"""
        dialog = ExportDialog(self.file_path, self)
        dialog.exportRequested.connect(self.export_logs)
        dialog.exec_()
        
    def export_logs(self, file_path, only_errors):
        """
        导出日志
        
        Args:
            file_path: 导出文件路径
            only_errors: 是否只导出错误日志
        """
        success, message = self.log_manager.export_logs(file_path, only_errors)
        
        if success:
            self.log_text.append(f"日志已导出至: {file_path}\n")
            
            # 创建自定义消息框，带有“打开”按钮
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("导出成功")
            msg_box.setText(f"日志已导出至:\n{file_path}")
            msg_box.setIcon(QMessageBox.Information)
            
            # 添加“打开”和“确定”按钮
            open_button = msg_box.addButton("打开日志", QMessageBox.ActionRole)
            open_button.setStyleSheet("""
                background-color: #34A853;  /* 绿色按钮 */
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 14px;
                min-width: 80px;
                margin: 0 3px;
            """)
            ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
            msg_box.setDefaultButton(ok_button)
            
            # 显示消息框并处理结果
            msg_box.exec_()
            
            # 如果点击了“打开”按钮
            if msg_box.clickedButton() == open_button:
                self.open_document(file_path)
        else:
            self.log_text.append(f"导出日志失败: {message}\n")
            QMessageBox.warning(self, "导出失败", f"导出日志失败: {message}")
            
    def closeEvent(self, event):
        """
        窗口关闭事件处理
        
        Args:
            event: 关闭事件
        """
        # 检查是否正在校对
        if self.is_proofreading:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "校对任务正在进行中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 停止校对任务
                if self.worker:
                    self.worker.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
