# Logos 喂养脚本
import sys
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "core"))
sys.path.append(str(BASE_DIR / "db"))

try:
    from db.logos_db import LogosDB
except ImportError:
    from logos_db import LogosDB

def feed_seed_knowledge():
    db = LogosDB()
    print(">>> 开始喂食 Logos 初始认知...")

    words = [
        "加", "减", "乘", "除", "求和", "乘积", "计算", "循环", "打印", "变量",
        "如果", "判断", "奇偶", "代码", "Python", "C语言", "输出",
        # 日常词汇
        "你好", "天气", "心情", "无聊", "累", "开心", "难过", "今天", "明天"
    ]
    for w in words:
        db.add_concept(w)
    print(f"-> 已喂食 {len(words)} 个基础概念")

    relations = [
        ("加", "属于", "数学运算"), ("减", "属于", "数学运算"),
        ("乘", "属于", "数学运算"), ("除", "属于", "数学运算"),
        ("求和", "包含", "加"), ("乘积", "包含", "乘"),
        ("循环", "可以", "重复执行"), ("判断", "可以", "分支逻辑"),
        # 日常关系
        ("天气", "可以", "闲聊"), ("心情", "可以", "闲聊"), ("无聊", "可以", "闲聊")
    ]
    for subj, rel, obj in relations:
        db.add_relation(subj, rel, obj)
    print(f"-> 已喂食 {len(relations)} 条基础关系")

    print(">>> 喂食完毕！")
    db.close()

if __name__ == "__main__":
    feed_seed_knowledge()