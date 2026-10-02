# Logos 核心组件 10：自然语言理解引擎 (Logos NLU Engine)

from vsa_engine import HyperVector
import re

class LogosNLU:
    def __init__(self, seed_library):
        self.library = seed_library
        
        self.lexicon = {
            "写代码": ["写", "弄", "搞", "生成", "编写"],
            "循环": ["循环", "反复", "遍历", "for", "while"],
            "打印": ["打印", "输出", "显示", "echo", "show"],
            "计算": ["计算", "求", "算"],
            "求和": ["求和", "累加", "和"],
            "乘积": ["乘积", "乘", "乘法"],
            "判断": ["判断", "如果", "if", "分支"],
            "C语言": ["c", "C语言", "c语言"],
            "C++": ["cpp", "C++", "c++"],
            "Python": ["python", "py", "Python"]
        }
        
        self.range_pattern = re.compile(r"(\d+)\s*(?:到|至|~|-)\s*(\d+)")

    def perceive_intent(self, text):
        text_lower = text.lower()
        code_keywords = ["用", "写", "弄", "搞", "生成", "打印", "循环", "c语言", "cpp", "python", "代码", "计算", "求", "判断", "乘积"]
        if any(word in text_lower for word in code_keywords):
            return "generate_code"
        if any(word in text_lower for word in ["你好", "在吗", "hello", "hi"]):
            return "greet"
        return "unknown"

    def extract_parameters(self, text):
        params = {
            "target_lang": "python",
            "actions": [],
            "loop_range": None,
            "math_op": None  # 新增：记录数学运算符
        }
        
        # 1. 提取目标语言
        if any(word in text for word in self.lexicon["C++"]):
            params["target_lang"] = "cpp"
        elif any(word in text for word in self.lexicon["C语言"]):
            params["target_lang"] = "c"
        elif any(word in text for word in self.lexicon["Python"]):
            params["target_lang"] = "python"
            
        # 2. 提取数学运算符
        if any(word in text for word in self.lexicon["乘积"]):
            params["math_op"] = "PRIM_MATH_MUL"
        elif any(word in text for word in self.lexicon["求和"]):
            params["math_op"] = "PRIM_MATH_ADD"
            
        # 3. 提取动作原语
        has_range = self.range_pattern.search(text) is not None
        if any(word in text for word in self.lexicon["循环"]) or has_range:
            params["actions"].append("PRIM_LOOP_FOR")
        if any(word in text for word in self.lexicon["打印"]):
            params["actions"].append("PRIM_PRINT")
            
        # 4. 提取数字范围
        match = self.range_pattern.search(text)
        if match:
            params["loop_range"] = (match.group(1), match.group(2))
            
        return params

    def parse(self, user_input):
        intent = self.perceive_intent(user_input)
        if intent != "generate_code":
            return {"intent": intent}
            
        params = self.extract_parameters(user_input)
        # 直接把参数传给 boot.py，让进化沙盒动态处理
        return {
            "intent": intent,
            "target_lang": params["target_lang"],
            "params": params
        }