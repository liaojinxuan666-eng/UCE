class CAEvolver:
    def __init__(self, goal_func, max_generations=1000)
    def generate_ast(self)    # 基于 CA 状态生成 AST
    def mutate(self, ast_node) # 代码变异
    def evaluate(self, code)   # 沙盒中执行并打分
    def evolve(self)           # 进化主循环