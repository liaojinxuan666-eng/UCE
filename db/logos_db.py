# Logos 数据库操作层
# 纯 Python 标准库，使用 SQLite（单文件，零配置，断电不丢数据）
import sqlite3
import json
import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(BASE_DIR / "core"))

try:
    from core.vsa_engine import HyperVector
except ImportError:
    from vsa_engine import HyperVector

class LogosDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = BASE_DIR / "db" / "logos.db"
        self.db_path = pathlib.Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        # 1. 概念表：存词汇、VSA向量
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                vsa_bits TEXT,
                type TEXT DEFAULT 'word'
            )
        ''')
        
        # 2. 关系表
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
        
        # 3. 代码经验表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                logic_tree TEXT,
                target_lang TEXT,
                success_count INTEGER DEFAULT 1,
                score REAL DEFAULT 1.0
            )
        ''')
        self.conn.commit()

    def add_concept(self, name, type="word"):
        if not name: return None
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
            self.cursor.execute("SELECT id FROM concepts WHERE name=?", (name,))
            return self.cursor.fetchone()[0]

    def add_relation(self, subject_name, relation, object_name):
        subj_id = self.add_concept(subject_name)
        obj_id = self.add_concept(object_name)
        if subj_id and obj_id:
            self.cursor.execute(
                "INSERT INTO relations (subject_id, relation, object_id) VALUES (?, ?, ?)",
                (subj_id, relation, obj_id)
            )
            self.conn.commit()

    def add_code_experience(self, logic_tree_dict, target_lang):
        self.cursor.execute(
            "INSERT INTO code_experience (logic_tree, target_lang) VALUES (?, ?)",
            (json.dumps(logic_tree_dict), target_lang)
        )
        self.conn.commit()

    def search_concept_by_vsa(self, query_vsa, threshold=0.7):
        """根据超维向量，模糊检索最相似的概念"""
        self.cursor.execute("SELECT name, vsa_bits FROM concepts")
        results = []
        for name, vsa_str in self.cursor.fetchall():
            if not vsa_str: continue
            # 将字符串转回二进制数组
            bits = [int(b) for b in vsa_str]
            stored_vsa = HyperVector(dim=10000)
            stored_vsa.bits = bits
            sim = query_vsa.similarity(stored_vsa)
            if sim >= threshold:
                results.append((sim, name))
        results.sort(reverse=True)
        return results[:5]

    def close(self):
        self.conn.close()