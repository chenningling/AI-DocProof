#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志管理模块
负责记录和导出校对日志
"""

import os
import logging
import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LogManager:
    """日志管理类，负责记录和导出校对日志"""
    
    def __init__(self):
        """初始化日志管理器"""
        self.logs = []
        self.error_count = 0
        self.total_count = 0
        self.start_time = None
        self.end_time = None
        self.save_path = None
        
    def start_logging(self):
        """开始记录日志"""
        self.logs = []
        self.error_count = 0
        self.total_count = 0
        self.start_time = datetime.datetime.now()
        logger.info("开始记录校对日志")
        
    def log_sentence(self, sentence, result, has_error=False):
        """
        记录句子校对日志
        
        Args:
            sentence: 校对的句子
            result: 校对结果，包含错误信息或API返回的内容
            has_error: 是否有错误
        """
        self.total_count += 1
        
        if has_error:
            self.error_count += 1
            log_entry = {
                'time': datetime.datetime.now(),
                'sentence': sentence,
                'has_error': True,
                'annotation': result.get('annotation', ''),
                'corrected': result.get('content_1', '')
            }
            log_text = f"正在校对：{sentence}\n发现错误：{log_entry['annotation']}\n已在文档中批注\n"
        else:
            log_entry = {
                'time': datetime.datetime.now(),
                'sentence': sentence,
                'has_error': False,
                'annotation': '',
                'corrected': ''
            }
            log_text = f"正在校对：{sentence}\n没有错误\n"
            
        self.logs.append(log_entry)
        logger.info(log_text)
        return log_text
        
    def log_error(self, sentence, error_message):
        """
        记录处理错误
        
        Args:
            sentence: 校对的句子
            error_message: 错误信息
        """
        log_entry = {
            'time': datetime.datetime.now(),
            'sentence': sentence,
            'has_error': False,
            'is_process_error': True,
            'error_message': error_message
        }
        
        log_text = f"正在校对：{sentence}\n处理错误：{error_message}\n"
        self.logs.append(log_entry)
        logger.error(log_text)
        return log_text
        
    def finish_logging(self, save_path=None):
        """
        完成日志记录
        
        Args:
            save_path: 文档保存路径
            
        Returns:
            str: 日志摘要
        """
        self.end_time = datetime.datetime.now()
        self.save_path = save_path
        
        duration = (self.end_time - self.start_time).total_seconds()
        summary = f"校对完成！\n"
        summary += f"检查句子总数: {self.total_count}\n"
        summary += f"错误数量: {self.error_count}\n"
        summary += f"校对用时: {duration:.2f} 秒\n"
        
        if save_path:
            summary += f"文档保存位置: {save_path}\n"
            
        logger.info(summary)
        return summary
        
    def export_logs(self, output_path, only_errors=False):
        """
        导出日志到文本文件
        
        Args:
            output_path: 输出文件路径
            only_errors: 是否只导出错误日志
            
        Returns:
            tuple: (是否成功, 输出路径或错误信息)
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("AI文档校对工具 - 校对日志\n")
                f.write("=" * 50 + "\n\n")
                
                # 检查时间值是否为None
                if self.start_time:
                    f.write(f"校对开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                else:
                    f.write("校对开始时间: 未记录\n")
                    
                if self.end_time:
                    f.write(f"校对结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                else:
                    f.write("校对结束时间: 未记录\n")
                    
                if self.start_time and self.end_time:
                    f.write(f"校对用时: {(self.end_time - self.start_time).total_seconds():.2f} 秒\n")
                else:
                    f.write("校对用时: 未记录\n")
                f.write(f"检查句子总数: {self.total_count}\n")
                f.write(f"错误数量: {self.error_count}\n")
                
                if self.save_path:
                    f.write(f"文档保存位置: {self.save_path}\n")
                    
                f.write("\n" + "=" * 50 + "\n\n")
                f.write("校对详情:\n\n")
                
                for i, log in enumerate(self.logs):
                    # 如果只导出错误日志，则跳过没有错误的条目
                    if only_errors and not log.get('has_error') and not log.get('is_process_error', False):
                        continue
                        
                    # 检查日志时间是否为None
                    if log.get('time'):
                        f.write(f"[{i+1}/{len(self.logs)}] {log['time'].strftime('%H:%M:%S')}\n")
                    else:
                        f.write(f"[{i+1}/{len(self.logs)}] 时间未记录\n")
                    f.write(f"句子: {log['sentence']}\n")
                    
                    if log.get('is_process_error', False):
                        f.write(f"处理错误: {log['error_message']}\n")
                    elif log['has_error']:
                        f.write(f"错误: {log['annotation']}\n")
                        f.write(f"修正: {log['corrected']}\n")
                    else:
                        f.write("没有错误\n")
                        
                    f.write("\n" + "-" * 30 + "\n\n")
                    
            logger.info(f"成功导出日志到: {output_path}")
            return True, output_path
            
        except Exception as e:
            logger.error(f"导出日志失败: {str(e)}")
            return False, f"导出日志失败: {str(e)}"
    
    def get_log_summary(self):
        """
        获取日志摘要
        
        Returns:
            dict: 日志摘要信息
        """
        return {
            'total_count': self.total_count,
            'error_count': self.error_count,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'save_path': self.save_path
        }


# 测试代码
if __name__ == "__main__":
    # 测试日志管理
    log_manager = LogManager()
    log_manager.start_logging()
    
    # 测试记录句子
    log_manager.log_sentence("这是一个测试句子。", {"wrong": False}, False)
    log_manager.log_sentence("这是一个有错误的句子。", {
        "content_0": "这是一个有错误的句子。",
        "wrong": True,
        "annotation": "句子中'错误'应为'错别字'",
        "content_1": "这是一个有错别字的句子。"
    }, True)
    
    # 测试记录错误
    log_manager.log_error("处理失败的句子", "API调用失败")
    
    # 测试完成日志
    summary = log_manager.finish_logging("test_output.docx")
    print(summary)
    
    # 测试导出日志
    success, path = log_manager.export_logs("test_log.txt")
    print(f"导出日志: {success}, 路径: {path}")
    
    # 测试只导出错误日志
    success, path = log_manager.export_logs("test_error_log.txt", only_errors=True)
    print(f"导出错误日志: {success}, 路径: {path}")
