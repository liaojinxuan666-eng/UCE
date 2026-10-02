# Logos 核心组件 8：种子标准库 (Seed Standard Library)

class LogosSeedLibrary:
    def __init__(self):
        # ================= 第一层：逻辑原语库 =================
        self.logic_primitives = {
            "PRIM_SEQUENCE": {"desc": "顺序执行多个动作", "args": ["body"]},
            "PRIM_VAR_DECL": {"desc": "声明变量", "args": ["var_name", "value"]},
            "PRIM_MATH_ADD": {"desc": "加法运算", "args": ["var1", "var2"]},
            "PRIM_MATH_SUB": {"desc": "减法运算", "args": ["var1", "var2"]},
            "PRIM_MATH_MUL": {"desc": "乘法运算", "args": ["var1", "var2"]},
            "PRIM_MATH_DIV": {"desc": "除法运算", "args": ["var1", "var2"]},
            "PRIM_PRINT": {"desc": "输出内容", "args": ["content"]},
            "PRIM_LOOP_FOR": {"desc": "for循环", "args": ["iter_var", "start", "end", "body"]},
            "PRIM_CONDITION_IF": {"desc": "if条件判断", "args": ["condition", "if_body", "else_body"]},
        }

        # ================= 第二层：多语言语法映射库 =================
        self.syntax_mappings = {
            "python": {
                "PRIM_SEQUENCE": "{body}",
                "PRIM_VAR_DECL": "{var_name} = {value}",
                "PRIM_MATH_ADD": "{var1} + {var2}",
                "PRIM_MATH_SUB": "{var1} - {var2}",
                "PRIM_MATH_MUL": "{var1} * {var2}",
                "PRIM_MATH_DIV": "{var1} / {var2}",
                "PRIM_PRINT": "print({content})",
                # 去掉模板里的硬编码缩进，完全交由生成器控制
                "PRIM_LOOP_FOR": "for {iter_var} in range({start}, {end} + 1):\n{body}",
                "PRIM_CONDITION_IF": "if {condition}:\n{if_body}\nelse:\n{else_body}",
            },
            "c": {
                "PRIM_SEQUENCE": "{body}",
                "PRIM_VAR_DECL": "int {var_name} = {value};",
                "PRIM_MATH_ADD": "{var1} + {var2}",
                "PRIM_MATH_SUB": "{var1} - {var2}",
                "PRIM_MATH_MUL": "{var1} * {var2}",
                "PRIM_MATH_DIV": "{var1} / {var2}",
                "PRIM_PRINT": 'printf("%d", {content});',
                "PRIM_LOOP_FOR": "for(int {iter_var}={start}; {iter_var}<={end}; {iter_var}++) {{\n{body}\n}}",
                "PRIM_CONDITION_IF": "if ({condition}) {{\n{if_body}\n}} else {{\n{else_body}\n}}",
            },
            "cpp": {
                "PRIM_SEQUENCE": "{body}",
                "PRIM_VAR_DECL": "int {var_name} = {value};",
                "PRIM_MATH_ADD": "{var1} + {var2}",
                "PRIM_MATH_SUB": "{var1} - {var2}",
                "PRIM_MATH_MUL": "{var1} * {var2}",
                "PRIM_MATH_DIV": "{var1} / {var2}",
                "PRIM_PRINT": 'std::cout << {content} << std::endl;',
                "PRIM_LOOP_FOR": "for(int {iter_var}={start}; {iter_var}<={end}; {iter_var}++) {{\n{body}\n}}",
                "PRIM_CONDITION_IF": "if ({condition}) {{\n{if_body}\n}} else {{\n{else_body}\n}}",
            }
        }

        # ================= 第三层：初始语用模板库 =================
        self.pragmatic_templates = {
            "greet": ["你好，我是 Logos。有什么我可以帮你的？", "我在。有什么需要思考或计算的？"],
            "success": ["执行完毕，结果如下：", "推演成功，得出的结论是：", "代码已跑通，输出如下："],
            "error": ["遇到了一点逻辑冲突，错误信息：{error}。", "运行失败了，报错如下：{error}。"],
            "unknown": ["这个我目前没有足够的逻辑原语来推演，但我们可尝试进化它。", "我暂时无法理解这个意图，你可以换个说法。"],
            "think": ["正在检索记忆图并组合逻辑原语...", "正在启动元胞自动机进化沙盒..."]
        }

    def add_composite_primitive(self, name, desc, args, syntax_map_dict):
        self.logic_primitives[name] = {"desc": desc, "args": args}
        for lang, template in syntax_map_dict.items():
            if lang in self.syntax_mappings:
                self.syntax_mappings[lang][name] = template
                
    def get_language_template(self, lang, primitive):
        if lang in self.syntax_mappings:
            return self.syntax_mappings[lang].get(primitive)
        return None