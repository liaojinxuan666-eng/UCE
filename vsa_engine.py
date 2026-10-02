# UCE - 超维向量符号引擎 (Hyperdimensional Vector Symbolic Engine)
# 纯 Python 标准库，不依赖 numpy，不使用 GPU
import random

class HyperVector:
    def __init__(self, dim=10000):
        # 我们用 Python 的大整数来模拟 10000 维的二进制向量
        # 内存占用仅 1.25KB 左右，极其轻量
        self.dim = dim
        self.bits = 0
    
    @classmethod
    def random(cls, dim=10000):
        """生成一个随机的超维向量（代表一个新的概念）"""
        v = cls(dim)
        # 随机生成 10000 个 0 或 1
        v.bits = random.getrandbits(dim)
        return v
    
    def bind(self, other):
        """绑定（乘法）：把两个概念关联起来。在二进制里，等价于 XOR。"""
        v = HyperVector(self.dim)
        v.bits = self.bits ^ other.bits
        return v
    
    def bundle(self, other):
        """捆绑（加法）：把两个概念叠加成一类。用多数投票法。"""
        v = HyperVector(self.dim)
        # 按位计算两边的 1 是否占多数
        # 这里为了代码极简，用位运算实现快速多数表决
        # (a & b) 两边都是1的保留；(a & ~b) 和 (~a & b) 随机选一边补齐
        both_1 = self.bits & other.bits
        both_0 = ~self.bits & ~other.bits
        diff = self.bits ^ other.bits
        
        # 随机决定不同的位是归 0 还是 1
        mask = random.getrandbits(self.dim)
        # 优化：在实际运行中，这种随机掩码可以在 10000 维下瞬间完成
        new_bits = both_1 | (diff & mask) 
        v.bits = new_bits & ((1 << self.dim) - 1)
        return v
    
    def permute(self, shift=1):
        """置换：改变序列顺序，用来表达“顺序”或“先后”关系。"""
        v = HyperVector(self.dim)
        v.bits = ((self.bits << shift) | (self.bits >> (self.dim - shift))) & ((1 << self.dim) - 1)
        return v
    
    def similarity(self, other):
        """计算相似度（汉明距离的归一化），用来判断两个概念像不像。"""
        dist = (self.bits ^ other.bits).bit_count()
        return 1.0 - (dist / self.dim)

# ================== 测试引擎是否能工作 ==================
if __name__ == "__main__":
    print(">>> UCE 超维引擎启动...")
    
    # 1. 生成随机概念
    apple = HyperVector.random()
    red = HyperVector.random()
    fruit = HyperVector.random()
    
    # 2. 绑定：红苹果 (苹果 绑定 红色)
    red_apple = apple.bind(red)
    
    # 3. 捆绑：水果大类 (苹果 捆绑 香蕉 捆绑 橘子)
    fruit_category = apple.bundle(red).bundle(fruit) # 叠加概念
    
    # 4. 解绑：从“红苹果”里提取“苹果” (XOR 是可逆的)
    recovered_apple = red_apple.bind(red)
    
    print(f"超维向量维度: {apple.dim}")
    print(f"苹果与红苹果的相似度: {red_apple.similarity(apple):.4f} (应该很低)")
    print(f"从红苹果解绑红之后的苹果，与原本苹果的相似度: {recovered_apple.similarity(apple):.4f} (应该极高)")
    
    # 5. 类比推理测试：这是“像人思考”的基石
    # 如果 苹果 绑 红色 = 红苹果；那么 香蕉 绑 黄色 = 黄香蕉
    yellow = HyperVector.random()
    yellow_banana = fruit.bind(yellow)
    recovered_banana = yellow_banana.bind(yellow)
    print(f"类比推理：黄香蕉 解绑 黄色，与原本香蕉的相似度: {recovered_banana.similarity(fruit):.4f} (应该极高)")