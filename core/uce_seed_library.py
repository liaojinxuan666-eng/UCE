# Logos 核心组件 8：种子标准库 (Seed Standard Library)
# 纯 Python 标准库，内存占用极低（< 100KB）
# 作用：提供开箱即用的逻辑原语、多语言语法映射、以及基础语用模板

class LogosSeedLibrary:
    def __init__(self):
        # ================= 第一层：逻辑原语库 (Logic Primitives) =================
        # 与语言无关的抽象逻辑积木，供进化引擎拼装使用
        self.logic_primitives = {
            "PRIM_VAR_DECL": {"desc": "声明变量", "args": ["var_name", "value"]},
            "PRIM_MATH_ADD": {"desc": "加法运算", "args": ["var1", "var2"]},
            "PRIM_MATH_SUB": {"desc": "减法运算", "args": ["var1", "var2"]},
            "PRIM_MATH_MUL": {"desc": "乘法运算", "args": ["var1", "var2"]},
            "PRIM_MATH_DIV": {"desc": "除法运算", "args": ["var1", "var2"]},
            "PRIM_PRINT": {"desc": "输出内容", "args": ["content"]},
            "PRIM_LOOP_FOR": {"desc": "for循环", "args": ["iter_var", "start", "end", "body"]},
            "PRIM_CONDITION_IF": {"desc": "if条件判断", "args": ["condition", "if_body", "else_body"]},
        }

        # ================= 第二层：多语言语法映射库 (Syntax Mappings) =================
        # 定义逻辑原语如何翻译成具体语言的模板字符串
        # 后续如果加 Go, Rust，只需在此字典添加键值对
        self.syntax_mappings = {
            "python": {
                "PRIM_VAR_DECL": "{var_name} = {value}",
                "PRIM_MATH_ADD": "{var1} + {var2}",
                "PRIM_MATH_SUB": "{var1} - {var2}",
                "PRIM_MATH_MUL": "{var1} * {var2}",
                "PRIM_MATH_DIV": "{var1} / {var2}",
                "PRIM_PRINT": "print({content})",
                # 修复边界 Bug：Python 范围要加 1
                "PRIM_LOOP_FOR": "for {iter_var} in range({start}, {end} + 1):\n    {body}",
                "PRIM_CONDITION_IF": "if {condition}:\n    {if_body}\nelse:\n    {else_body}",
            },
            "c": {
                "PRIM_VAR_DECL": "int {var_name} = {value};",
                "PRIM_MATH_ADD": "{var1} + {var2}",
                "PRIM_MATH_SUB": "{var1} - {var2}",
                "PRIM_MATH_MUL": "{var1} * {var2}",
                "PRIM_MATH_DIV": "{var1} / {var2}",
                "PRIM_PRINT": 'printf("%d", {content});',
                # 修复边界 Bug：改成 <=
                "PRIM_LOOP_FOR": "for(int {iter_var}={start}; {iter_var}<={end}; {iter_var}++) {{\n    {body}\n}}",
                "PRIM_CONDITION_IF": "if ({condition}) {{\n    {if_body}\n}} else {{\n    {else_body}\n}}",
            },
            "cpp": {
                "PRIM_VAR_DECL": "int {var_name} = {value};",
                "PRIM_MATH_ADD": "{var1} + {var2}",
                "PRIM_MATH_SUB": "{var1} - {var2}",
                "PRIM_MATH_MUL": "{var1} * {var2}",
                "PRIM_MATH_DIV": "{var1} / {var2}",
                "PRIM_PRINT": 'std::cout << {content} << std::endl;',
                # 修复边界 Bug：改成 <=
                "PRIM_LOOP_FOR": "for(int {iter_var}={start}; {iter_var}<={end}; {iter_var}++) {{\n    {body}\n}}",
                "PRIM_CONDITION_IF": "if ({condition}) {{\n    {if_body}\n}} else {{\n    {else_body}\n}}",
            }
        }

        # ================= 第三层：初始语用模板库 (Pragmatic Templates) =================
        # 让 Logos 一启动就能像人一样说话，包含多种随机回复
        self.pragmatic_templates = {
            "greet": [
                "你好，我是 Logos。有什么我可以帮你的？",
                "我在。有什么需要思考或计算的？",
                "你好，Logos 在线。随时准备开始推演。"
            ],
            # 修复 Key 名错误，并移除可能导致崩溃的占位符
            "success": [
                "执行完毕，结果如下：",
                "推演成功，得出的结论是：",
                "代码已跑通，输出如下："
            ],
            "error": [
                "遇到了一点逻辑冲突，错误信息：{error}。",
                "运行失败了，报错如下：{error}。",
                "推演中断，需要解决这个错误：{error}。"
            ],
            "unknown": [
                "这个我目前没有足够的逻辑原语来推演，但我们可尝试进化它。",
                "我暂时无法理解这个意图，你可以换个说法，或者让我重新进化学习。",
                "我的种子库没找到对应的逻辑，你可以教我怎么处理。"
            ],
            "think": [
                "正在检索记忆图并组合逻辑原语...",
                "正在启动元胞自动机进化沙盒...",
                "量子搜索层正在坍缩最优路径..."
            ]
        }

    # ================= 自我繁衍接口 =================
    def add_composite_primitive(self, name, desc, args, syntax_map_dict):
        """
        高级接口：当进化引擎（ca_evolver）跑通了一个复杂算法（如快速排序），
        将其转化为"复合逻辑原语"存入种子库。
        """
        self.logic_primitives[name] = {"desc": desc, "args": args}
        for lang, template in syntax_map_dict.items():
            if lang in self.syntax_mappings:
                self.syntax_mappings[lang][name] = template
                
    def get_language_template(self, lang, primitive):
        """提供给代码合成器的查询接口"""
        if lang in self.syntax_mappings:
            return self.syntax_mappings[lang].get(primitive)
        return None