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
        
        # 核心修复：基于词库构建真实的语义意图向量
        self.intents = {
            "generate_code": self._build_intent_vector(
                self.lexicon["写代码"] + self.lexicon["计算"] + self.lexicon["循环"] + self.lexicon["打印"]
            ),
            "greet": self._build_intent_vector(self.lexicon["问候"]),
            "chat": self._build_intent_vector(self.lexicon["闲聊"]),
            "unknown": HyperVector.random()
        }

    def _get_word_vector(self, word):
        """根据词汇生成稳定的超维向量"""
        r = random.Random(hash(word))
        v = HyperVector()
        # 直接给 bits 赋值
        v.bits = array.array('B', [r.getrandbits(1) for _ in range(v.DIM)])
        return v

    def _build_intent_vector(self, word_list):
        """将属于同一个意图的所有词汇向量捆绑起来，形成概念中心"""
        if not word_list:
            return HyperVector.random()
        v = self._get_word_vector(word_list[0])
        for w in word_list[1:]:
            v = v.bundle(self._get_word_vector(w))
        return v

    def perceive_intent(self, text):
        """基于 VSA 语义相似度的意图识别"""
        words = [w for w in re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z0-9]+', text.lower()) if w.strip()]
        
        if not words:
            return "unknown"
        
        # 构建用户输入的超维向量
        sentence_vector = self._get_word_vector(words[0])
        for w in words[1:]:
            sentence_vector = sentence_vector.bundle(self._get_word_vector(w))
            
        # 与概念中心进行相似度比对
        best_intent = "unknown"
        highest_sim = 0.0
        
        for intent_name, intent_vec in self.intents.items():
            sim = sentence_vector.similarity(intent_vec)
            if sim > highest_sim:
                highest_sim = sim
                best_intent = intent_name
                
        # VSA 相似度通常分布在 0.5 左右，我们取最高分
        # 如果没有明显的高分，才判定为未知
        if highest_sim < 0.5:
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