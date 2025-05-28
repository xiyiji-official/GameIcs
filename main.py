# -*- coding: utf-8 -*-
"""
此脚本用于从YYSTV获取游戏数据并生成ICS日历文件。
它使用了requests库来获取数据，pydantic库来处理数据模型，ics库来创建ICS日历文件。

created by: xiyiji-official
created at: 2025-01-14
updated at: 2025-05-28
"""

import requests
from pydantic import BaseModel, model_validator
from typing import Union
from typing_extensions import Self
import time
from ics import Calendar, Event


# 定义数据模型
class GameData(BaseModel):
    name: str
    releasetime: str
    platform: Union[list, str]
    tags: Union[list, str]
    preface: str
    price: str

    def toList(self, oldList: Union[list, str], keyWord: str) -> str:
        """
        将游戏发售平台和标签列表转换为字符串。

        :param oldList: 原始列表或字符串
        :param keyWord: 用于提取的关键字
        :return newList: 以空格分隔的字符串
        """
        newList = ""
        if isinstance(oldList, str):
            return oldList
        if isinstance(oldList, list):
            for i in oldList:
                newList = newList + i[keyWord] + " "
            return newList

    @model_validator(mode="after")
    def transform(self) -> Self:
        self.platform = self.toList(self.platform, "name")
        self.tags = self.toList(self.tags, "name")
        return self


def addEvent(calendar: Calendar, data: GameData) -> bool:
    """
    将游戏数据转化为ICS日历事件。

    :param calendar: ics.Calendar对象
    :param data: GameData对象，包含游戏信息
    :return: bool，表示事件是否成功添加
    """
    try:
        event = Event()
        event.name = data.name
        event.begin = f"{data.releasetime}"  # type: ignore
        event.make_all_day()
        event.categories = ["GameIcs"]  # type: ignore
        event.description = (
            f"{data.preface}\n{data.platform}\n{data.tags}\n{data.price}"  
        )  # 使用换行符在事件的描述部分添加所需展示的信息
        calendar.events.add(event)
    except Exception as e:
        print(e)
        return False
    return True


# 获取游戏数据的URL和请求头
url = "https://www.yystv.cn/games/game_calendar/get_games"
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36 Edg/129.0.0.0",
}


if __name__ == "__main__":
    calendar = Calendar()
    for num in range(0, 100):
        res = requests.get(
            url=url,
            headers=headers,
            params={
                "time": "",
                "page": num,
                "tab_id": 0,
                "past": "",
                "begintime": f"{time.localtime().tm_year}-01-01",
                "endtime": f"{time.localtime().tm_year + 1}-12-31",
                "chinese": "",
                "tag_id": "",
            },
        )
        if res.status_code != 200:
            print(f"Error: {res.status_code}")
            break
        result = res.json()["data"]
        if result:
            for i in result:
                response = addEvent(calendar, GameData(**i))
        else:
            break
    print("All data processed, writing to file...")
    # 将生成的日历事件写入ICS文件
    with open("my.ics", "w", encoding="UTF-8") as f:
        f.writelines(calendar.serialize_iter())
        f.close()
    print("ok")

"""
如果需要将网站爬取的数据保存为JSON文件查看，可以取消以下注释
"""
# import json
# with open("data.json", "w", encoding="UTF-8") as f:
#     f.write(json.dumps(result[0]).encode("UTF-8").decode("unicode_escape"))
#     f.close()
# print("ok")
