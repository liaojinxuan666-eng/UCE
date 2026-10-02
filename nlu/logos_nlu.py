# Logos 核心组件 10：自然语言理解引擎 (Logos NLU Engine)
from vsa_engine import HyperVector
import re
import array
import random

class LogosNLU:
    def __init__(self, seed_library):
        self.library = seed_library
        
        self.lexicon = {
            "写代码": ["写", "弄", "搞", "生成", "编写", "代码", "程序"],
            "循环": ["循环", "反复", "遍历", "for", "while"],
            "打印": ["打印", "输出", "显示", "echo", "show"],
            "计算": ["计算", "求", "算", "求和", "累加", "乘积", "乘"],
            "判断": ["判断", "如果", "if", "分支", "奇偶"],
            "C语言": ["c", "C语言", "c语言"],
            "C++": ["cpp", "C++", "c++"],
            "Python": ["python", "py", "Python"],
            "问候": ["你好", "在吗", "hello", "hi", "嗨"],
            "闲聊": ["无聊", "天气", "心情", "累", "开心", "难过", "今天", "傻子", "笨"]
        }
        
        # 意图超维向量
        self.intents = {
            "generate_code": HyperVector.random(),
            "greet": HyperVector.random(),
            "chat": HyperVector.random(),
            "unknown": HyperVector.random()
        }

    def _get_word_vector(self, word):
        """从种子库获取词汇的超维向量"""
        # 使用固定哈希种子，保证同一个词每次生成一样的向量
        r = random.Random(hash(word))
        v = HyperVector()
        # 修正：直接给 bits 赋值
        v.bits = array.array('B', [r.getrandbits(1) for _ in range(v.DIM)])
        return v

    def perceive_intent(self, text):
        """基于 VSA 语义相似度的意图识别"""
        # 1. 分词
        words = [w for w in re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z0-9]+', text.lower()) if w.strip()]
        
        if not words:
            return "unknown"
        
        # 2. 构建句子的超维向量
        sentence_vector = self._get_word_vector(words[0])
        for w in words[1:]:
            sentence_vector = sentence_vector.bundle(self._get_word_vector(w))
            
        # 3. 与预定义的意图向量进行相似度比对
        best_intent = "unknown"
        highest_sim = 0.0
        
        for intent_name, intent_vec in self.intents.items():
            sim = sentence_vector.similarity(intent_vec)
            if sim > highest_sim:
                highest_sim = sim
                best_intent = intent_name
                
        # 4. 如果相似度太低，降级为未知
        if highest_sim < 0.55:
            return "unknown"
            
        return best_intent

    def extract_parameters(self, text):
        params = {
            "target_lang": "python",
            "actions": [],
            "loop_range": None,
            "math_op": None
        }
        
        if any(word in text for word in self.lexicon["C++"]): params["target_lang"] = "cpp"
        elif any(word in text for word in self.lexicon["C语言"]): params["target_lang"] = "c"
        elif any(word in text for word in self.lexicon["Python"]): params["target_lang"] = "python"
            
        if any(word in text for word in self.lexicon["计算"]):
            if "乘积" in text or "乘" in text: params["math_op"] = "PRIM_MATH_MUL"
            else: params["math_op"] = "PRIM_MATH_ADD"
            
        match = re.search(r"(\d+)\s*(?:到|至|~|-)\s*(\d+)", text)
        if match: params["loop_range"] = (match.group(1), match.group(2))
            
        return params

    def parse(self, user_input):
        intent = self.perceive_intent(user_input)
        
        if intent == "generate_code":
            params = self.extract_parameters(user_input)
            return {
                "intent": "generate_code",
                "target_lang": params["target_lang"],
                "params": params
            }
        else:
            return {"intent": intent}