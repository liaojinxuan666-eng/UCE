# Logos 喂养脚本：给全新的模型喂入基础知识和语用模板
# 运行方式：python trainer/data_feeder.py

import sys
import pathlib
# 将项目根目录加入路径，方便导入
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from db.logos_db import LogosDB

def feed_seed_knowledge():
    db = LogosDB()
    print(">>> 开始喂食 Logos 初始种子...")

    # ================= 1. 喂食基础概念（词表） =================
    words = [
        "苹果", "水果", "香蕉", "吃", "红色", "黄色", "你好", "累", 
        "循环", "打印", "变量", "加法", "C语言", "Python", "代码"
    ]
    for w in words:
        db.add_concept(w)
    print(f"-> 已喂食 {len(words)} 个基础词汇")

    # ================= 2. 喂食常识关系（逻辑图谱） =================
    relations = [
        ("苹果", "属于", "水果"),
        ("香蕉", "属于", "水果"),
        ("水果", "可以", "吃"),
        ("苹果", "是", "红色"),  # 简化表示
        ("C语言", "属于", "代码"),
        ("Python", "属于", "代码")
    ]
    for subj, rel, obj in relations:
        db.add_relation(subj, rel, obj)
    print(f"-> 已喂食 {len(relations)} 条常识关系")

    # ================= 3. 喂食基础代码经验（逻辑树） =================
    # 这是一条"用 C 语言打印 1 到 10"的成功经验，直接预装进去，让模型起跑就带技能
    seed_logic = {
        "primitive": "PRIM_LOOP_FOR",
        "args": {
            "iter_var": "i",
            "start": "1",
            "end": "10",
            "body": {
                "primitive": "PRIM_PRINT",
                "args": {"content": "i"}
            }
        }
    }
    db.add_code_experience(seed_logic, "c")
    
    # 再预装一个 Python 版本的
    db.add_code_experience(seed_logic, "python")
    print(f"-> 已喂食 2 条基础代码经验（C语言和Python版）")

    print(">>> 喂食完毕！Logos 的初始数据库已建立。")
    db.close()

if __name__ == "__main__":
    feed_seed_knowledge()