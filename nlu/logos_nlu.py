# Logos 核心组件 10：自然语言理解引擎 (Logos NLU Engine)
# 纯 Python 标准库，依赖 vsa_engine.py 和 uce_seed_library.py

from vsa_engine import HyperVector
import re

class LogosNLU:
    def __init__(self, seed_library):
        self.library = seed_library
        
        self.lexicon = {
            "写代码": ["写", "弄", "搞", "生成", "编写"],
            "循环": ["循环", "反复", "遍历", "for", "while"],
            "打印": ["打印", "输出", "显示", "echo", "show"],
            "计算": ["计算", "求", "算", "求和", "累加"],
            "判断": ["判断", "如果", "if", "分支"],
            "C语言": ["c", "C语言", "c语言"],
            "C++": ["cpp", "C++", "c++"],
            "Python": ["python", "py", "Python"]
        }
        
        self.intents = {
            "generate_code": HyperVector.random(),
            "greet": HyperVector.random(),
            "query_memory": HyperVector.random()
        }
        
        self.range_pattern = re.compile(r"(\d+)\s*(?:到|至|~|-)\s*(\d+)")

    def perceive_intent(self, text):
        text_lower = text.lower()
        code_keywords = ["用", "写", "弄", "搞", "生成", "打印", "循环", "c语言", "cpp", "python", "代码", "计算", "求", "判断"]
        if any(word in text_lower for word in code_keywords):
            return "generate_code"
        if any(word in text_lower for word in ["你好", "在吗", "hello", "hi"]):
            return "greet"
        return "unknown"

    def extract_parameters(self, text):
        params = {
            "target_lang": "python",
            "actions": [],
            "loop_range": None
        }
        
        if any(word in text for word in self.lexicon["C++"]):
            params["target_lang"] = "cpp"
        elif any(word in text for word in self.lexicon["C语言"]):
            params["target_lang"] = "c"
        elif any(word in text for word in self.lexicon["Python"]):
            params["target_lang"] = "python"
            
        has_range = self.range_pattern.search(text) is not None
        
        # 注意：这里为了能让"求和"逻辑触发进化，我们把条件收紧
        if any(word in text for word in self.lexicon["循环"]) or (has_range and any(w in text for w in ["打印", "输出"])):
            params["actions"].append("PRIM_LOOP_FOR")
            
        if any(word in text for word in self.lexicon["打印"]):
            params["actions"].append("PRIM_PRINT")
            
        match = self.range_pattern.search(text)
        if match:
            params["loop_range"] = (match.group(1), match.group(2))
            
        return params

    def build_logic_tree(self, params):
        """核心转化：将参数转化为逻辑树"""
        actions = params["actions"]
        loop_range = params["loop_range"]
        
        # 如果识别到的是求和/计算，不生成常规树，返回错误信号，触发进化沙盒
        if "求和" in str(params) or "计算" in str(params):
             return {"error": "需要进化沙盒处理"}

        if "PRIM_LOOP_FOR" in actions and "PRIM_PRINT" in actions:
            if not loop_range:
                return {"error": "未指定循环范围"}
            return {
                "primitive": "PRIM_LOOP_FOR",
                "args": {
                    "iter_var": "i",
                    "start": loop_range[0],
                    "end": loop_range[1],
                    "body": {"primitive": "PRIM_PRINT", "args": {"content": "i"}}
                }
            }
            
        return {"error": "种子库未包含此逻辑组合"}

    def parse(self, user_input):
        intent = self.perceive_intent(user_input)
        if intent != "generate_code":
            return {"intent": intent}
            
        params = self.extract_parameters(user_input)
        logic_tree = self.build_logic_tree(params)
        
        if "error" in logic_tree:
            return {"intent": intent, "target_lang": params["target_lang"], "error": logic_tree["error"]}
            
        return {
            "intent": intent,
            "target_lang": params["target_lang"],
            "logic_tree": logic_tree
        }