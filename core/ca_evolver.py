# UCE 核心组件 3：元胞自动机进化沙盒 (Cellular Automata Evolutionary Sandbox)
# 纯 Python 标准库，依赖 ast、subprocess、sys、random
# 特性：用 AST 构造代码，用元胞自动机驱动变异，在隔离沙盒中进化出符合目标的代码

import ast
import subprocess
import sys
import random
import time
import copy

class CAEvolver:
    def __init__(self, target_output, max_generations=1000, population_size=100):
        self.target_output = str(target_output)  # 期望的程序输出
        self.max_generations = max_generations
        self.population_size = population_size
        
        # 基础代码模板：我们要让种群进化的起点
        # 例如，围绕 print(...) 表达式进行进化
        self.seed_code = "print(0)"
        
        # 记录进化历史
        self.history = []

    # ================= 1. 初始种群生成 =================
    def generate_initial_population(self):
        """生成第一代种群（基于种子代码进行初步变异）"""
        population = []
        for _ in range(self.population_size):
            # 解析种子代码为 AST
            tree = ast.parse(self.seed_code)
            # 变异
            mutated_tree = self.mutate_ast(tree)
            # 编译回代码字符串
            code_str = ast.unparse(mutated_tree)
            population.append(code_str)
        return population

    # ================= 2. 元胞自动机驱动的 AST 变异 =================
    def mutate_ast(self, tree):
        """
        将 AST 展平为一维数组（元胞状态），根据局部规则变异，再组装回 AST。
        这里以修改数学常量或运算符为例演示 CA 规则。
        """
        tree = copy.deepcopy(tree)
        
        # 收集所有的常数节点（CA中的状态单元）
        constants = [node for node in ast.walk(tree) if isinstance(node, ast.Constant)]
        
        if not constants:
            return tree
            
        # 元胞自动机的核心：每个细胞（常数）根据邻居决定自己的变化
        # 简化版：如果前后细胞是相似状态（比如都是偶数），则保持，否则随机突变
        for i, const_node in enumerate(constants):
            if isinstance(const_node.value, int):
                # 邻居状态
                left_val = constants[i-1].value if i > 0 else const_node.value
                right_val = constants[i+1].value if i < len(constants) - 1 else const_node.value
                
                # CA 规则：如果左右邻居都是偶数，则当前格 +1；否则 -1 或 随机
                if left_val % 2 == 0 and right_val % 2 == 0:
                    const_node.value += 1
                else:
                    const_node.value = random.randint(-10, 10)
                    
        # 也可以随机改变运算符（这也是 CA 状态的一部分）
        binops = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp)]
        for binop in binops:
            if random.random() < 0.3:  # 30% 概率变异运算符
                binop.op = random.choice([ast.Add(), ast.Sub(), ast.Mult(), ast.Div()])
                
        return tree

    # ================= 3. 沙盒执行与评估 =================
    def run_in_sandbox(self, code_str):
        """
        在隔离的子进程中运行代码，设置 1 秒超时。
        返回 (stdout, stderr)
        """
        try:
            # 使用子进程运行代码，超时1秒强制终止
            result = subprocess.run(
                [sys.executable, "-c", code_str],
                capture_output=True,
                text=True,
                timeout=1.0
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return None, "Timeout"
        except Exception as e:
            return None, str(e)

    def evaluate_fitness(self, code_str):
        """
        根据输出与目标匹配的程度打分。
        分数范围 0.0 ~ 1.0
        """
        stdout, stderr = self.run_in_sandbox(code_str)
        
        # 运行报错或超时，直接给 0 分淘汰
        if stderr or stdout is None:
            return 0.0
            
        # 精确命中目标
        if stdout == self.target_output:
            return 1.0
            
        # 模糊匹配（字符串部分匹配，鼓励向目标收敛）
        matches = sum(1 for a, b in zip(stdout, self.target_output) if a == b)
        return matches / max(len(stdout), len(self.target_output)) * 0.9  # 最高给0.9，避免蒙对

    # ================= 4. 进化主循环 =================
    def evolve(self):
        """运行进化算法，返回最优代码"""
        population = self.generate_initial_population()
        
        for generation in range(self.max_generations):
            # 1. 评估适应度
            scored_population = []
            for code in population:
                score = self.evaluate_fitness(code)
                scored_population.append((score, code))
                
                # 如果找到满分代码，直接结束进化
                if score == 1.0:
                    self.history.append({"generation": generation, "score": 1.0, "code": code})
                    return code, generation
            
            # 2. 按分数排序，淘汰后 50%
            scored_population.sort(reverse=True, key=lambda x: x[0])
            survivors = [item[1] for item in scored_population[:self.population_size // 2]]
            
            # 3. 繁殖下一代（交叉 + 变异）
            next_generation = survivors[:]
            while len(next_generation) < self.population_size:
                parent = random.choice(survivors)
                parent_tree = ast.parse(parent)
                child_tree = self.mutate_ast(parent_tree)
                child_code = ast.unparse(child_tree)
                next_generation.append(child_code)
            
            population = next_generation
            
            # 记录最佳分数（用于后续元进化调整参数）
            self.history.append({"generation": generation, "score": scored_population[0][0], "code": scored_population[0][1]})
            
        # 如果达到最大代数还没找到满分解，返回最好的
        return scored_population[0][1], self.max_generations

    # ================= 5. 外部调用接口 =================
    def solve(self):
        """对外接口：传入目标，返回进化出的代码"""
        best_code, generations_used = self.evolve()
        return {
            "success": self.evaluate_fitness(best_code) == 1.0,
            "code": best_code,
            "generations": generations_used,
            "history": self.history
        }