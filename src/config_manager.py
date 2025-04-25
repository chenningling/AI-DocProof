#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
负责管理API配置信息的保存和读取
"""

import json
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理类，负责API配置信息的保存和读取"""
    
    def __init__(self, config_file=None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为程序所在目录下的config.json
        """
        if config_file is None:
            # 获取程序所在目录
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_file = os.path.join(base_dir, 'config.json')
        else:
            self.config_file = config_file
            
        # 默认配置
        self.default_config = {
            'api_url': 'https://api.deepseek.com/chat/completions',
            'model': 'deepseek-chat',
            'api_key': '',
            'system_prompt': """作为一个细致耐心的文字秘书，对下面的句子进行错别字检查，按如下结构以 JOSN 格式输出：
{
"content_0":"原始句子",
"wrong":true,//是否有需要被修正的错别字，布尔类型
"annotation":"",//批注内容，string类型。如果wrong为true给出修正的解释；如果 wrong 字段为 false，则为空值
"content_1":""//修改后的句子，string类型。如果wrong为false则留空
}"""
        }
        
        # 当前配置
        self.config = self.load_config()
        
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置信息字典
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"成功从 {self.config_file} 加载配置")
                return config
            else:
                logger.info(f"配置文件 {self.config_file} 不存在，使用默认配置")
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置，默认为当前配置
        
        Returns:
            bool: 保存是否成功
        """
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            logger.info(f"成功保存配置到 {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def update_config(self, new_config):
        """
        更新配置
        
        Args:
            new_config: 新的配置信息
            
        Returns:
            bool: 更新是否成功
        """
        try:
            self.config.update(new_config)
            return self.save_config()
        except Exception as e:
            logger.error(f"更新配置失败: {str(e)}")
            return False
    
    def get_config(self):
        """
        获取当前配置
        
        Returns:
            dict: 当前配置信息
        """
        return self.config
    
    def reset_config(self):
        """
        重置为默认配置
        
        Returns:
            bool: 重置是否成功
        """
        self.config = self.default_config.copy()
        return self.save_config()
    
    def validate_config(self):
        """
        验证配置是否有效
        
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查必要的配置项是否存在
        required_fields = ['api_url', 'model', 'api_key']
        for field in required_fields:
            if field not in self.config or not self.config[field]:
                return False, f"缺少必要的配置项: {field}"
        
        # 检查API URL格式
        if not self.config['api_url'].startswith(('http://', 'https://')):
            return False, "API URL 格式不正确，应以 http:// 或 https:// 开头"
        
        return True, ""


# 测试代码
if __name__ == "__main__":
    config_manager = ConfigManager()
    print(config_manager.get_config())
    
    # 测试更新配置
    new_config = {
        'api_key': 'test_key',
        'model': 'test_model'
    }
    config_manager.update_config(new_config)
    print(config_manager.get_config())
    
    # 测试验证配置
    valid, msg = config_manager.validate_config()
    print(f"配置有效性: {valid}, 消息: {msg}")
