import requests
from pydantic import BaseModel, model_validator
from typing import Union
from typing_extensions import Self
import time
from ics import Calendar, Event


class GameData(BaseModel):
    name: str
    releasetime: str
    platform: Union[list, str]
    tags: Union[list, str]
    preface: str
    price: str

    def toList(self, oldList: list, keyWord: str) -> str:
        newList = ""
        for i in oldList:
            newList = newList + i[keyWord] + " "
        return newList

    @model_validator(mode="after")
    def transform(self) -> Self:
        self.platform = self.toList(self.platform, "name")
        self.tags = self.toList(self.tags, "name")
        return self


def addEvent(c: Calendar, data: GameData) -> bool:
    try:
        e = Event()
        e.name = data.name
        e.begin = f"{data.releasetime}"
        e.make_all_day()
        e.categories = ["GameIcs"]
        e.description = f"{data.preface}\n{data.platform}\n{data.tags}\n{data.price}"
        c.events.add(e)
    except Exception as err:
        print(err)
        return False
    return True


url = "https://www.yystv.cn/games/game_calendar/get_games"

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36 Edg/129.0.0.0",
}


if __name__ == "__main__":
    c = Calendar()
    for num in range(0, 100):
        print(num)
        res = requests.get(
            url=url,
            headers=headers,
            params={
                "time": "",
                "page": num,
                "tab_id": 0,
                "past": "",
                "begintime": f"{time.localtime().tm_year}-01-01",
                "endtime": f"{time.localtime().tm_year+1}-12-31",
                "chinese": "",
                "tag_id": "",
            },
        )
        print(res.status_code)
        result = res.json()["data"]
        if result:
            for i in result:
                fin_data = GameData(**i)
                response = addEvent(c, fin_data)
        else:
            break
    with open("my.ics", "w", encoding="UTF-8") as f:
        f.writelines(c.serialize_iter())
        f.close()
    print("ok")


# with open("data.json", "w", encoding="UTF-8") as f:
#     f.write(json.dumps(result[0]).encode("UTF-8").decode("unicode_escape"))
#     f.close()
# print("ok")
