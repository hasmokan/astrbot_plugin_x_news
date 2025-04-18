from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import subprocess

@register("astrbot_plugin_x", "hasmokan", "一个简单的获取X新闻插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    @filter.command("get_x_news")
    async def get_x_news(self, event: AstrMessageEvent):
        '''获取彩虹六号新闻'''
        user_name = event.get_sender_name()
        message_str = event.message_str
        message_chain = event.get_messages()
        logger.info(message_chain)
        
        result = subprocess.run(['node', 'fetch_tweets.cjs'], capture_output=True, text=True, check=True)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {result.stdout}!") # 发送一条纯文本消息
        # try:
        #     # 执行 node 命令来运行 JavaScript 文件
        #     result = subprocess.run(['node', 'fetch_tweets.cjs'], capture_output=True, text=True, check=True)
        #     # 打印标准输出
        #     print("标准输出:")
        #     print(result.stdout)
        #     yield event.plain_result(f"Hello, {user_name}, 你发了 {result.stdout}!") # 发送一条纯文本消息
            
        # except subprocess.CalledProcessError as e:
        #     # 若执行出错，打印错误信息
        #     print(f"执行出错，错误代码: {e.returncode}")
        #     print("错误输出:")
        #     print(e.stderr) 
        
    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
