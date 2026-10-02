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
        
        # 3. 代码经验表（带签名，用于记忆复用）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature TEXT UNIQUE,
                logic_tree TEXT,
                target_lang TEXT,
                success_count INTEGER DEFAULT 1,
                score REAL DEFAULT 1.0
            )
        ''')
        self.conn.commit()

    # ================= 概念与关系操作 =================
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

    # ================= 记忆复用操作 =================
    def get_experience_by_signature(self, signature):
        """根据签名查询是否有现成的逻辑经验"""
        self.cursor.execute(
            "SELECT logic_tree, target_lang FROM code_experience WHERE signature=?",
            (signature,)
        )
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0]), row[1]
        return None, None

    def add_code_experience(self, signature, logic_tree_dict, target_lang):
        """将成功的逻辑树存入数据库"""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO code_experience (signature, logic_tree, target_lang) VALUES (?, ?, ?)",
                (signature, json.dumps(logic_tree_dict), target_lang)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"保存经验失败: {e}")
            return False

    def close(self):
        self.conn.close()