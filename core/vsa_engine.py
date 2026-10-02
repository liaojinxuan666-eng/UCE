# UCE 核心组件 1：超维向量符号引擎 (Hyperdimensional Vector Symbolic Engine)
# 纯 Python 标准库，不使用 NumPy，不使用 GPU
# 特性：用 10000 维二进制向量进行概念绑定、捆绑、解绑与相似度计算

import array
import random

class HyperVector:
    DIM = 10000  # 默认维度，可调

    def __init__(self, bits=None):
        # 使用 array 存储二进制位，每个元素是 0 或 1
        # 内存占用约为 10KB，极其轻量
        self.bits = bits if bits is not None else array.array('B', [0] * self.DIM)

    @classmethod
    def random(cls):
        """生成一个随机的超维向量，代表一个全新的原子概念"""
        bits = array.array('B', (random.getrandbits(1) for _ in range(cls.DIM)))
        return cls(bits)

    def bind(self, other):
        """
        绑定（乘法）：用来关联两个概念（例如：苹果 + 红色 = 红苹果）
        在二进制超维计算中，绑定操作定义为逐位异或 (XOR)
        """
        new_bits = array.array('B', (self.bits[i] ^ other.bits[i] for i in range(self.DIM)))
        return HyperVector(new_bits)

    def bundle(self, other):
        """
        捆绑（加法）：用来将多个概念合并成同类（例如：苹果 + 香蕉 = 水果）
        采用"多数表决"原则：如果两向量在某一位相同，则保留；不同则随机
        为保证数学性质，这里使用经典的"多数加法"近似算法
        """
        new_bits = array.array('B')
        for i in range(self.DIM):
            a, b = self.bits[i], other.bits[i]
            if a == b:
                new_bits.append(a)
            else:
                # 在严格 VSA 中，这里应记录权重或做随机选择
                new_bits.append(random.getrandbits(1))
        return HyperVector(new_bits)

    def permute(self, shift=1):
        """
        置换：改变序列顺序，用来表达"顺序"、"先后"或"关系"
        即循环移位操作
        """
        new_bits = array.array('B')
        for i in range(self.DIM):
            new_bits.append(self.bits[(i - shift) % self.DIM])
        return HyperVector(new_bits)

    def similarity(self, other):
        """
        计算相似度：1 - 汉明距离 / 维度
        返回一个 0.0 到 1.0 之间的浮点数
        """
        dist = sum(1 for i in range(self.DIM) if self.bits[i] != other.bits[i])
        return 1.0 - (dist / self.DIM)

    def to_binary_string(self):
        """用于可视化调试：将向量转为 10000 位字符串（慎用，太长）"""
        return ''.join(str(b) for b in self.bits)