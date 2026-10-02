# Logos 核心组件 10：自然语言理解引擎 (Logos NLU Engine)
# 纯 Python 标准库，依赖 vsa_engine.py 和 uce_seed_library.py
# 作用：将用户的自然语言，转化为"意图 + 参数 + 逻辑原语"的结构化数据

from vsa_engine import HyperVector
import re

class LogosNLU:
    def __init__(self, seed_library):
        self.library = seed_library
        
        # 1. 初始化近义词/关键词映射表 (纯字典，占内存极小)
        self.lexicon = {
            "写代码": ["写", "弄", "搞", "生成", "编写"],
            "循环": ["循环", "反复", "遍历", "for", "while"],
            "打印": ["打印", "输出", "显示", "echo", "show"],
            "C语言": ["c", "C语言", "c语言"],
            "C++": ["cpp", "C++", "c++"],
            "Python": ["python", "py", "Python"]
        }
        
        # 2. 初始化意图超维向量 (保留以兼容未来 VSA 升级，目前先用规则匹配)
        self.intents = {
            "generate_code": HyperVector.random(),
            "greet": HyperVector.random(),
            "query_memory": HyperVector.random()
        }
        
        # 3. 预定义参数提取正则（纯代码）
        # 匹配：1到10, 1-10, 1~10, 1至10
        self.range_pattern = re.compile(r"(\d+)\s*(?:到|至|~|-)\s*(\d+)")

    def tokenize(self, text):
        """
        极简分词：基于字典的正向最大匹配
        """
        words = []
        text = text.lower()
        max_len = 4 # 假设最长词汇长度为 4
        i = 0
        while i < len(text):
            for j in range(min(max_len, len(text) - i), 0, -1):
                word = text[i:i+j]
                # 检查是否在词表、近义词或数字中
                if word in self.library.logic_primitives or self._is_known_word(word) or word.isdigit():
                    words.append(word)
                    i += j
                    break
            else:
                # 如果没匹配上，就跳过单个字符
                i += 1
        return words

    def _is_known_word(self, word):
        """检查是否在近义词表中"""
        for key, synonyms in self.lexicon.items():
            if word in synonyms or word == key:
                return True
        return False

    def perceive_intent(self, text):
        """
        意图识别：基于关键词的精准规则匹配（取代随机占位符）
        """
        text_lower = text.lower()
        
        # 1. 优先识别代码生成请求
        if any(word in text_lower for word in ["用", "写", "弄", "搞", "生成", "打印", "循环", "c语言", "cpp", "python", "代码"]):
            return "generate_code"
            
        # 2. 识别打招呼
        if any(word in text_lower for word in ["你好", "在吗", "hello", "hi"]):
            return "greet"
            
        # 3. 其他
        return "unknown"

    def extract_parameters(self, text):
        """
        槽位填充：提取语言、动作、范围等参数
        """
        params = {
            "target_lang": "python", # 默认语言
            "actions": [],
            "loop_range": None
        }
        
        # 1. 提取目标语言
        if any(word in text for word in self.lexicon["C++"]):
            params["target_lang"] = "cpp"
        elif any(word in text for word in self.lexicon["C语言"]):
            params["target_lang"] = "c"
        elif any(word in text for word in self.lexicon["Python"]):
            params["target_lang"] = "python"
            
        # 2. 提取动作原语
        has_range = self.range_pattern.search(text) is not None
        
        # 核心修复：如果提到"打印"并且有数字范围（如 1到10），自动推演出需要"循环"
        if any(word in text for word in self.lexicon["循环"]) or (has_range and "打印" in text):
            params["actions"].append("PRIM_LOOP_FOR")
            
        if any(word in text for word in self.lexicon["打印"]):
            params["actions"].append("PRIM_PRINT")
            
        # 3. 提取数字范围 (1到10)
        match = self.range_pattern.search(text)
        if match:
            params["loop_range"] = (match.group(1), match.group(2))
            
        return params

    def build_logic_tree(self, params):
        """
        核心转化：将参数转化为进化引擎能理解的"逻辑树"
        """
        actions = params["actions"]
        target_lang = params["target_lang"]
        loop_range = params["loop_range"]
        
        # 简单的组装逻辑：假设是"循环+打印"组合
        if "PRIM_LOOP_FOR" in actions and "PRIM_PRINT" in actions:
            if not loop_range:
                return {"error": "未指定循环范围"}
                
            logic_tree = {
                "primitive": "PRIM_LOOP_FOR",
                "args": {
                    "iter_var": "i",
                    "start": loop_range[0],
                    "end": loop_range[1],
                    "body": {
                        "primitive": "PRIM_PRINT",
                        "args": {"content": "i"}
                    }
                }
            }
            return logic_tree
            
        return {"error": "无法识别的动作组合"}

    # ================= 对外核心接口 =================
    def parse(self, user_input):
        """
        一站式解析：输入人类语言，输出逻辑树 + 目标语言
        """
        # 1. 识别意图
        intent = self.perceive_intent(user_input)
        
        if intent != "generate_code":
            return {"intent": intent}
            
        # 2. 提取参数
        params = self.extract_parameters(user_input)
        
        # 3. 构建逻辑树
        logic_tree = self.build_logic_tree(params)
        
        # 如果逻辑树里有 error，直接把 error 传回去，不再传 logic_tree
        if "error" in logic_tree:
            return {"intent": intent, "error": logic_tree["error"]}
            
        return {
            "intent": intent,
            "target_lang": params["target_lang"],
            "logic_tree": logic_tree
        }