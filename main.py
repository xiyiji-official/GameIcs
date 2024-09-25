import requests
from pydantic import BaseModel, model_validator
from typing_extensions import Self
import time


class GameData(BaseModel):
    name: str
    releasetime: str
    platform: list
    tags: list
    preface: str
    price: str

    def toList(self, oldList: list, keyWord: str) -> list:
        newList = []
        for i in oldList:
            newList.append(i[keyWord])
        return newList

    @model_validator(mode="after")
    def transform(self) -> Self:
        self.platform = self.toList(self.platform, "name")
        self.tags = self.toList(self.tags, "name")
        return self


url = "https://www.yystv.cn/games/game_calendar/get_games"

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36 Edg/129.0.0.0",
}

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
            print(fin_data.model_dump())
    else:
        break
print("ok")


# with open("data.json", "w", encoding="UTF-8") as f:
#     f.write(json.dumps(result[0]).encode("UTF-8").decode("unicode_escape"))
#     f.close()
# print("ok")
