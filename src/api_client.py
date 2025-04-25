#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API客户端模块
负责与AI API的通信，发送请求并处理响应
"""

import json
import logging
import requests
from requests.exceptions import RequestException

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApiClient:
    """API客户端类，负责与AI API的通信"""
    
    def __init__(self, config=None):
        """
        初始化API客户端
        
        Args:
            config: API配置信息，包含api_url, model, api_key等
        """
        self.config = config or {}
        self.api_url = self.config.get('api_url', '')
        self.model = self.config.get('model', '')
        self.api_key = self.config.get('api_key', '')
        self.system_prompt = self.config.get('system_prompt', '')
        
    def update_config(self, config):
        """
        更新API配置
        
        Args:
            config: 新的配置信息
        """
        self.config = config
        self.api_url = config.get('api_url', self.api_url)
        self.model = config.get('model', self.model)
        self.api_key = config.get('api_key', self.api_key)
        self.system_prompt = config.get('system_prompt', self.system_prompt)
        
    def check_connection(self):
        """
        检查API连接是否正常
        
        Returns:
            tuple: (是否连接正常, 错误信息)
        """
        try:
            # 构建一个简单的请求来测试连接
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ],
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "API连接正常"
            else:
                return False, f"API连接异常，状态码: {response.status_code}, 响应: {response.text}"
                
        except RequestException as e:
            logger.error(f"API连接测试失败: {str(e)}")
            return False, f"API连接失败: {str(e)}"
    
    def proofread_sentence(self, sentence):
        """
        发送句子到API进行校对
        
        Args:
            sentence: 需要校对的句子
            
        Returns:
            tuple: (是否成功, 校对结果或错误信息)
        """
        if not sentence.strip():
            return False, "句子为空，跳过校对"
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": sentence}
                ],
                "stream": False
            }
            
            logger.info(f"发送API请求: {json.dumps(data, ensure_ascii=False)}")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return False, f"API请求失败，状态码: {response.status_code}"
                
            response_data = response.json()
            logger.info(f"API响应: {json.dumps(response_data, ensure_ascii=False)}")
            
            # 提取API返回的内容
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                
                # 尝试解析JSON响应
                try:
                    # 检查是否包含Markdown代码块标记
                    if content.strip().startswith('```') and '```' in content.strip()[3:]:
                        # 提取代码块中的JSON内容
                        content_parts = content.strip().split('```')
                        if len(content_parts) >= 3:
                            # 提取中间部分（JSON内容）
                            json_content = content_parts[1]
                            # 如果以'json'开头，去掉它
                            if json_content.startswith('json'):
                                json_content = json_content[4:].strip()
                            else:
                                json_content = json_content.strip()
                            # 尝试解析提取的JSON
                            result = json.loads(json_content)
                        else:
                            # 如果分割后的部分不足3个，尝试直接解析
                            result = json.loads(content)
                    else:
                        # 没有Markdown标记，直接解析
                        result = json.loads(content)
                    
                    # 验证返回的JSON是否包含必要的字段
                    if all(key in result for key in ['content_0', 'wrong', 'annotation', 'content_1']):
                        return True, result
                    else:
                        logger.error(f"API返回的JSON格式不符合预期: {content}")
                        return False, f"API返回的JSON格式不符合预期: {content}"
                except json.JSONDecodeError as e:
                    logger.error(f"API返回的内容不是有效的JSON: {content}, 错误: {str(e)}")
                    return False, f"API返回的内容不是有效的JSON: {content}"
            else:
                logger.error(f"API响应中没有找到有效内容: {response_data}")
                return False, f"API响应中没有找到有效内容"
                
        except Exception as e:
            logger.error(f"校对句子时发生错误: {str(e)}")
            return False, f"校对句子时发生错误: {str(e)}"


# 测试代码
if __name__ == "__main__":
    # 测试配置
    test_config = {
        'api_url': 'https://api.deepseek.com/chat/completions',
        'model': 'deepseek-chat',
        'api_key': 'your_api_key_here',
        'system_prompt': """作为一个细致耐心的文字秘书，对下面的句子进行错别字检查，按如下结构以 JSON 格式输出（不要包含代码块标记）：
{
"content_0":"原始句子",
"wrong":true,//是否有需要被修正的错别字，布尔类型
"annotation":"",//批注内容，string类型。如果wrong为true给出修正的解释；如果 wrong 字段为 false，则为空值
"content_1":""//修改后的句子，string类型。如果wrong为false则留空
}"""
    }
    
    api_client = ApiClient(test_config)
    
    # 测试连接
    connected, message = api_client.check_connection()
    print(f"连接状态: {connected}, 消息: {message}")
    
    # 测试校对句子（需要有效的API密钥）
    # success, result = api_client.proofread_sentence("这是一个测试句子，看看有没有错别字。")
    # print(f"校对结果: {success}, 内容: {result}")
