# UCE 核心组件 4：量子启发式搜索 (Quantum-Inspired Search)
# 纯 Python 标准库，不依赖任何量子计算库
# 特性：用概率幅并行评估多个逻辑路径，模拟量子隧穿跳出局部最优

import random
import math

class QuantumSearch:
    def __init__(self, paths):
        # paths: 列表，每个元素是一个字典，包含 "path" 和 "weight"
        self.paths = paths
        self.num_paths = len(paths)
        
        # 初始化概率幅，给每条路径赋一个均等的权重
        for p in self.paths:
            p["amplitude"] = 1.0 / math.sqrt(self.num_paths) if self.num_paths > 0 else 0.0

    def superposition(self, iterations=100):
        """
        叠加态演化：通过概率幅的干涉和调整，让最优路径的概率放大
        """
        for _ in range(iterations):
            # 计算总概率（归一化常数）
            total_prob = sum(p["amplitude"] ** 2 for p in self.paths)
            if total_prob == 0:
                break
            
            # 模拟量子干涉：根据当前概率，调整概率幅
            for p in self.paths:
                prob = (p["amplitude"] ** 2) / total_prob
                # 概率越大的路径，概率幅越增加（正反馈，放大优势）
                # 同时加入扰动，防止过早收敛
                noise = random.uniform(-0.05, 0.05)
                p["amplitude"] = math.sqrt(prob) + noise

    def quantum_tunneling(self):
        """
        量子隧穿：当搜索陷入局部最优时，强制给某些路径"穿墙"的机会，
        逃逸出当前的最优解，去探索更广的空间。
        """
        # 随机选择一条路径，给它一个大幅度的概率幅提升
        if not self.paths:
            return
        
        idx = random.randint(0, self.num_paths - 1)
        self.paths[idx]["amplitude"] += random.uniform(0.2, 0.5)

    def collapse(self):
        """
        坍缩：观察者效应，根据概率幅最终选择一个最优路径
        """
        # 计算所有路径的最终概率
        total_prob = sum(p["amplitude"] ** 2 for p in self.paths)
        if total_prob == 0:
            return random.choice(self.paths) if self.paths else None
        
        # 按照概率分布进行轮盘赌选择
        r = random.uniform(0, total_prob)
        cumulative = 0.0
        for p in self.paths:
            cumulative += p["amplitude"] ** 2
            if r <= cumulative:
                return p
                
        return self.paths[-1]