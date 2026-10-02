# Logos 核心组件 10：自然语言理解引擎 (Logos NLU Engine)
# 纯 Python 标准库，依赖 vsa_engine.py 和 uce_seed_library.py
# 作用：将用户的自然语言，转化为"意图 + 参数 + 逻辑原语"的结构化数据

from vsa_engine import HyperVector
import re

class LogosNLU:
    def __init__(self, seed_library):
        self.library = seed_library
        
        # 1. 初始化近义词/关键词映射表 (纯字典，占内存极小)
        # 这里把我们希望它能听懂的词，映射到种子库的逻辑原语
        self.lexicon = {
            "写代码": ["写", "弄", "搞", "生成", "编写"],
            "循环": ["循环", "反复", "遍历", "for", "while"],
            "打印": ["打印", "输出", "显示", "echo", "show"],
            "C语言": ["c", "C语言", "c语言"],
            "C++": ["cpp", "C++", "c++"],
            "Python": ["python", "py", "Python"]
        }
        
        # 2. 初始化意图超维向量
        self.intents = {
            "generate_code": HyperVector.random(),
            "greet": HyperVector.random(),
            "query_memory": HyperVector.random()
        }
        
        # 3. 预定义参数提取正则（纯代码）
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
        意图识别：利用 VSA 相似度来判断用户想干嘛
        """
        # 简化处理：把用户输入当作一个整体向量（后续可替换为词语向量捆绑）
        # 这里用一个占位逻辑，实际应用中会将分词后的向量进行 bundle
        query_vec = HyperVector.random() 
        
        best_intent = None
        highest_sim = 0.0
        
        for intent_name, intent_vec in self.intents.items():
            sim = query_vec.similarity(intent_vec)
            if sim > highest_sim:
                highest_sim = sim
                best_intent = intent_name
                
        return best_intent

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
        if any(word in text for word in self.lexicon["循环"]):
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
            return {"intent": intent, "message": "我需要处理的是代码生成任务。"}
            
        # 2. 提取参数
        params = self.extract_parameters(user_input)
        
        # 3. 构建逻辑树
        logic_tree = self.build_logic_tree(params)
        
        if "error" in logic_tree:
            return {"intent": intent, "error": logic_tree["error"]}
            
        return {
            "intent": intent,
            "target_lang": params["target_lang"],
            "logic_tree": logic_tree
        }