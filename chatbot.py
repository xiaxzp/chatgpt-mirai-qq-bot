# from revChatGPT.Official import Chatbot, Prompt
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend, Group
from graia.ariadne.message import Source
from typing import Union, Any, Dict, Tuple
from config import Config
from loguru import logger
import os
import asyncio
import uuid
from time import sleep
import json
import openai
import re

config = Config.load_config()
openai.api_key = config.openai.api_key;
# bot = Chatbot(api_key=config.openai.api_key)
def getChatResp(history: list):
    print(history);
    return openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=history,
        temperature=config.openai.temperature,
        max_tokens=2048,
        presence_penalty=0.6,
        frequency_penalty=1,
        top_p=1,
        # stop=["<|im_end|>"]
    )
class ChatSession:
    chat_history: list
    __default_chat_history: list = []
    def __init__(self):
        self.load_conversation()

    def load_conversation(self, keyword='default'):
        if not keyword in config.presets.keywords:
            if keyword == 'default':
                self.__default_chat_history = []
            else:
                raise ValueError("预设不存在，请检查你的输入是否有问题！")
        else:
            self.__default_chat_history = {
                "role": "system",
                "content": config.load_preset(keyword),
            }
        self.reset_conversation()
        return config.presets.loaded_successful

    def reset_conversation(self):
        self.chat_history = []

    def rollback_conversation(self) -> bool:
        if len(self.chat_history) < 1:
            return False
        self.chat_history.pop()
        if len(self.chat_history)  == 0:
            return ''
        else:
            return self.chat_history[-1]["content"];

    async def get_chat_response(self, message) -> str:
        # bot.prompt.chat_history = self.chat_history
        if len(self.chat_history) > 10:
            self.chat_history.pop(0);
            self.chat_history.pop(0);
        self.chat_history.append({
            "role": "user", #assistant
            "content": message,
        });

        loop = asyncio.get_event_loop()
        final_resp = await loop.run_in_executor(
            None,
            getChatResp,
            self.__default_chat_history + self.chat_history,
        )
        print('final resp');
        print(final_resp["choices"]);
        # final_resp = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt="Say this is a test",
        #     temperature=config.openai.temperature,
        #     max_tokens=7,
        #     stop="<|im_end|>"
        # )
        final_resp = final_resp["choices"][0]["message"]["content"]
        final_resp = final_resp if final_resp else '阿巴阿巴'
        # final_resp = re.sub("^\s*\n*骰娘:", '', final_resp)

        for item in ['台灣', '台湾','taiwan',]:
            if final_resp.strip().find(item) > -1:
                final_resp = '阿巴阿巴阿巴'
        self.chat_history.append({
            "role": "assistant",
            "content": final_resp,
        });
        print(final_resp);
        return final_resp

__sessions = {}

def get_chat_session(id: str) -> ChatSession:
    if id not in __sessions:
        __sessions[id] = ChatSession()
    return __sessions[id]
