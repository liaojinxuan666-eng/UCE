# Logos 数据库操作层
# 纯 Python 标准库，使用 SQLite（单文件，零配置，断电不丢数据）
# 作用：持久化存储概念、关系、代码经验

import sqlite3
import json
import pathlib
from core.vsa_engine import HyperVector

class LogosDB:
    def __init__(self, db_path="db/logos.db"):
        self.db_path = pathlib.Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        # 1. 概念表：存词汇、代码原语、VSA向量
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                vsa_bits TEXT, -- 存储 10000 维二进制的字符串形式
                type TEXT DEFAULT 'word'
            )
        ''')
        
        # 2. 关系表：存逻辑关系（例如：苹果 -> 属于 -> 水果）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                relation TEXT,
                object_id INTEGER,
                FOREIGN KEY(subject_id) REFERENCES concepts(id),
                FOREIGN KEY(object_id) REFERENCES concepts(id)
            )
        ''')
        
        # 3. 代码经验表：存进化成功过的逻辑树，用来实现"越用越聪明"
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                logic_tree TEXT, -- 存 JSON 字符串
                target_lang TEXT,
                success_count INTEGER DEFAULT 1,
                score REAL DEFAULT 1.0
            )
        ''')
        self.conn.commit()

    def add_concept(self, name, type="word"):
        """添加概念，并自动生成超维向量"""
        v = HyperVector.random()
        vsa_str = ''.join(str(b) for b in v.bits)
        try:
            self.cursor.execute(
                "INSERT INTO concepts (name, vsa_bits, type) VALUES (?, ?, ?)",
                (name, vsa_str, type)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # 如果已存在，返回已有的 id
            self.cursor.execute("SELECT id FROM concepts WHERE name=?", (name,))
            return self.cursor.fetchone()[0]

    def add_relation(self, subject_name, relation, object_name):
        """添加逻辑关系"""
        subj_id = self.add_concept(subject_name)
        obj_id = self.add_concept(object_name)
        self.cursor.execute(
            "INSERT INTO relations (subject_id, relation, object_id) VALUES (?, ?, ?)",
            (subj_id, relation, obj_id)
        )
        self.conn.commit()

    def add_code_experience(self, logic_tree_dict, target_lang):
        """存入进化成功的代码逻辑树"""
        logic_tree_json = json.dumps(logic_tree_dict)
        self.cursor.execute(
            "INSERT INTO code_experience (logic_tree, target_lang) VALUES (?, ?)",
            (logic_tree_json, target_lang)
        )
        self.conn.commit()

    def get_experience_for_language(self, target_lang):
        """查询指定语言的历史经验"""
        self.cursor.execute(
            "SELECT logic_tree FROM code_experience WHERE target_lang=? ORDER BY score DESC",
            (target_lang,)
        )
        return [json.loads(row[0]) for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()