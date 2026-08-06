import json

with open("C:/Users/HP/Desktop/stage_onssa/code/parser/chunks_v2.json", encoding="utf-8") as f:
    data = json.load(f)

print(data[0]["metadata"])