import datetime
import traceback
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import asyncio
import os
import json

@register("astrbot_plugin_x", "hasmokan", "一个简单的获取X新闻插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        # self.config = config
        # self.target_groups = config.get("target_groups", [])
        # self.push_time = config.get("push_time", "08:00")
        
        # # 启动定时任务
        # asyncio.create_task(self.daily_task())

    @filter.on_astrbot_loaded()
    async def on_astrbot_loaded(self):
        if not hasattr(self, "client"):
            self.client = self.context.get_platform("aiocqhttp").get_client()
        return

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
    async def handle_x_news_command(self, event: AstrMessageEvent):
        await self.fetch_and_analyze_tweets_command(event)

    @filter.command("get_x_news_auto")
    async def handle_x_news_command_auto(self, event: AstrMessageEvent):
        await self.fetch_and_analyze_tweets_auto(event)

    async def fetch_and_analyze_tweets_command(self, event: AstrMessageEvent):
        '''获取x新闻'''
        message_chain = event.get_messages()
        logger.info(message_chain)
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 fetch-tweets.cjs 的绝对路径
        file_path = os.path.join(current_dir, 'fetch-tweets.cjs')
        command = ["node", file_path]

        func_tools_mgr = self.context.get_llm_tool_manager()

        # 获取用户当前与 LLM 的对话以获得上下文信息。
        curr_cid = await self.context.conversation_manager.get_curr_conversation_id(event.unified_msg_origin) # 当前用户所处对话的对话id，是一个 uuid。
        conversation = None # 对话对象
        context = [] # 上下文列表
        if curr_cid:
            conversation = await self.context.conversation_manager.get_conversation(event.unified_msg_origin, curr_cid)
            context = json.loads(conversation.history)
        try:
            # 创建异步子进程
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

             # 等待进程完成并获取输出
            stdout_bytes, stderr_bytes = await process.communicate()

             # 将字节流解码为字符串
            stdout = stdout_bytes.decode('utf-8') if stdout_bytes else ''
            stderr = stderr_bytes.decode('utf-8') if stderr_bytes else ''

            logger.info(stdout)

            yield event.request_llm(
                prompt="你必须分点表述，并且每句话结尾加上可爱的语气词,请根据以下电竞相关推文数据生成分析报告，重点关注战队人员变动、赛事进展与结果、选手动态等方面：梳理战队人员变动情况，包括选手加入、离开、转会等，说明对战队实力的潜在影响，如 m0NESY 离开 G2 加入 Falcons，degster 被 Falcons 板凳等事件。总结近期赛事的关键进展，如欧洲 MRQ 各轮次的比赛结果、重要对决，以及 PGL Bucharest 的比赛进程和最终排名。分析选手动态，例如 degster 获得 MVP，m0NESY 在比赛中的表现，以及选手之间的互动和相关言论。指出数据中体现的电竞行业趋势或值得关注的现象，如战队的战术调整、选手的市场价值变化等。以清晰的结构呈现分析内容，分点阐述，突出重点信息。" + stdout,
                func_tool_manager=func_tools_mgr,
                session_id=curr_cid, # 对话id。如果指定了对话id，将会记录对话到数据库
                contexts=context, # 列表。如果不为空，将会使用此上下文与 LLM 对话。
                system_prompt="必须分点阐述，并且带上可爱的语气词",
                image_urls=[], # 图片链接，支持路径和网络链接
                conversation=conversation # 如果指定了对话，将会记录对话
            )

        except Exception as e:
            logger.info(f"执行命令时发生错误: {str(e)}")

    async def fetch_and_analyze_tweets_auto(self, event: AstrMessageEvent):
        '''获取x新闻'''
        message_chain = event.get_messages()
        logger.info(message_chain)
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 fetch-tweets.cjs 的绝对路径
        file_path = os.path.join(current_dir, 'fetch-tweets.cjs')
        command = ["node", file_path]

        func_tools_mgr = self.context.get_llm_tool_manager()

        # 获取用户当前与 LLM 的对话以获得上下文信息。
        curr_cid = await self.context.conversation_manager.get_curr_conversation_id(event.unified_msg_origin) # 当前用户所处对话的对话id，是一个 uuid。
        conversation = None # 对话对象
        context = [] # 上下文列表
        if curr_cid:
            conversation = await self.context.conversation_manager.get_conversation(event.unified_msg_origin, curr_cid)
            context = json.loads(conversation.history)
        try:
            # 创建异步子进程
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

             # 等待进程完成并获取输出
            stdout_bytes, stderr_bytes = await process.communicate()

             # 将字节流解码为字符串
            stdout = stdout_bytes.decode('utf-8') if stdout_bytes else ''
            stderr = stderr_bytes.decode('utf-8') if stderr_bytes else ''

            logger.info(stdout)

            llm_response = await self.context.get_using_provider().text_chat(
                prompt="你必须分点表述，并且每句话结尾加上可爱的语气词,请根据以下电竞相关推文数据生成分析报告，重点关注战队人员变动、赛事进展与结果、选手动态等方面：梳理战队人员变动情况，包括选手加入、离开、转会等，说明对战队实力的潜在影响，如 m0NESY 离开 G2 加入 Falcons，degster 被 Falcons 板凳等事件。总结近期赛事的关键进展，如欧洲 MRQ 各轮次的比赛结果、重要对决，以及 PGL Bucharest 的比赛进程和最终排名。分析选手动态，例如 degster 获得 MVP，m0NESY 在比赛中的表现，以及选手之间的互动和相关言论。指出数据中体现的电竞行业趋势或值得关注的现象，如战队的战术调整、选手的市场价值变化等。以清晰的结构呈现分析内容，分点阐述，突出重点信息。如果推文数据中存在之前播报过的新闻，那么则删除相应的数据，只保留最新的数据" + stdout,
                session_id=None, # 此已经被废弃
                contexts=context,
                image_urls=[], # 图片链接，支持路径和网络链接
                system_prompt="必须分点阐述，并且带上可爱的语气词",
            )

            logger.info(llm_response.completion_text)
            
            yield event.plain_result(llm_response.completion_text)


        except Exception as e:
            logger.info(f"执行命令时发生错误: {str(e)}")


    # 计算到明天指定时间的秒数
    def calculate_sleep_time(self):
        """计算到下一次推送时间的秒数"""
        now = datetime.datetime.now()
        hour, minute = map(int, self.push_time.split(':'))
        
        tomorrow = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if tomorrow <= now:
            tomorrow += datetime.timedelta(days=1)
            
        seconds = (tomorrow - now).total_seconds()
        return seconds

    # 定时任务
    async def daily_task(self):
        """定时推送任务"""
        while True:
            try:
                # 计算到下次推送的时间
                sleep_time = self.calculate_sleep_time()
                print(f"下次推送将在 {sleep_time/3600:.2f} 小时后")
                
                # 等待到设定时间
                await asyncio.sleep(sleep_time)
                
                # 推送新闻
                await self.send_daily_news()
                
                # 再等待一段时间，避免重复推送
                await asyncio.sleep(60)
            except Exception as e:
                print(f"定时任务出错: {e}")
                traceback.print_exc()
                await asyncio.sleep(300)
    
    @filter.command("news_status")
    async def check_status(self, event: AstrMessageEvent):
        """检查插件状态"""
        sleep_time = self.calculate_sleep_time()
        hours = int(sleep_time / 3600)
        minutes = int((sleep_time % 3600) / 60)
        
        yield event.plain_result(
            f"每日x新闻插件正在运行\n"
            f"目标群组: {', '.join(map(str, self.target_groups))} \n"
            f"推送时间: {self.push_time}\n"
            f"距离下次推送还有: {hours}小时{minutes}分钟"
        )

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''