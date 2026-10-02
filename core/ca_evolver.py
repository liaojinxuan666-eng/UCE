# Logos 核心组件 3：元胞自动机进化沙盒 (True Cellular Automata Evolver)
# 纯 Python 标准库
# 作用：基于逻辑原语（而非纯Python代码）进行随机变异与试错

import random
import io
import contextlib

class CAEvolver:
    def __init__(self, target_output, start, end, synthesizer, max_generations=20, population_size=10):
        self.target_output = str(target_output)
        self.start = start
        self.end = end
        self.synthesizer = synthesizer
        self.max_generations = max_generations
        self.population_size = population_size

    def _generate_random_tree(self):
        """
        生成一个随机的逻辑树（这是它独立思考的核心）。
        随机选择初始值（0或1），随机选择运算符（+或*）。
        """
        init_val = random.choice(["0", "1"])
        op = random.choice(["+", "*"])
        return {
            "primitive": "PRIM_SEQUENCE",
            "args": {
                "body": [
                    {"primitive": "PRIM_VAR_DECL", "args": {"var_name": "total", "value": init_val}},
                    {"primitive": "PRIM_LOOP_FOR", "args": {
                        "iter_var": "i", "start": self.start, "end": self.end,
                        "body": {"primitive": "PRIM_VAR_DECL", "args": {"var_name": "total", "value": f"total {op} i"}}
                    }},
                    {"primitive": "PRIM_PRINT", "args": {"content": "total"}}
                ]
            }
        }

    def _evaluate(self, tree):
        """
        在隔离沙盒中运行逻辑树生成的代码，检查输出是否匹配目标。
        返回：(是否成功, 运算符, 初始值)
        """
        # 1. 用代码合成器把逻辑树翻译成 Python 代码
        synth_result = self.synthesizer.synthesize_from_evolution(tree, "python")
        if not synth_result.get("success"):
            return False, None, None
            
        code = synth_result["code"]
        
        # 2. 提取操作符和初始值，以便后续固化记忆
        op = "+" if "*" not in code else "*"
        init_val = "1" if "total = 1" in code else "0"
        
        # 3. 沙盒执行
        try:
            f = io.StringIO()
            # 隔离执行环境，只允许 range 和 print
            with contextlib.redirect_stdout(f):
                exec(code, {"__builtins__": {"range": range, "print": print}}, {})
            output = f.getvalue().strip()
            
            # 4. 匹配目标
            if output == self.target_output:
                return True, op, init_val
        except Exception:
            pass
            
        return False, None, None

    def evolve(self):
        """启动进化循环"""
        for gen in range(self.max_generations):
            # 生成随机种群
            population = [self._generate_random_tree() for _ in range(self.population_size)]
            
            # 遍历种群，寻找成功者
            for tree in population:
                success, op, init_val = self._evaluate(tree)
                if success:
                    print(f"Logos: [进化沙盒] 第 {gen+1} 代产生正确逻辑！（运算符: {op}，初始值: {init_val}）")
                    return tree, op, init_val
                    
        return None, None, None