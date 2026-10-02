# Logos 数据库操作层
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
        # 重建表，增加 signature 字段用于快速匹配
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

    # 核心：查询是否存在类似的逻辑经验
    def get_experience_by_signature(self, signature):
        self.cursor.execute(
            "SELECT logic_tree, target_lang FROM code_experience WHERE signature=?",
            (signature,)
        )
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0]), row[1]
        return None, None

    # 核心：保存成功的逻辑树
    def add_code_experience(self, signature, logic_tree_dict, target_lang):
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