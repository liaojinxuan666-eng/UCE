# Logos 核心组件 9：代码合成器 (Code Synthesizer)
# 纯 Python 标准库
# 作用：将进化出的"逻辑树"与种子库的"语法映射"结合，动态拼装出多语言代码

import ast

class CodeSynthesizer:
    def __init__(self, seed_library):
        self.library = seed_library

    def synthesize(self, logic_tree, target_lang="python", indent_level=0):
        """
        递归解析逻辑树，生成目标语言的代码字符串。
        """
        if not logic_tree:
            return ""

        primitive = logic_tree.get("primitive")
        args = logic_tree.get("args", {})

        # 1. 获取语法模板
        template = self.library.get_language_template(target_lang, primitive)
        if not template:
            return f"# 未知原语: {primitive}"

        # 2. 递归处理嵌套参数
        processed_args = {}
        for key, value in args.items():
            if isinstance(value, dict) and "primitive" in value:
                # 递归生成子代码
                child_code = self.synthesize(value, target_lang, indent_level + 1)
                # 修正缩进：确保子代码块内部的缩进是相对于当前层级的
                processed_args[key] = self._indent_code(child_code, indent_level + 1)
            else:
                processed_args[key] = str(value)

        # 3. 填充模板
        try:
            code_segment = template.format(**processed_args)
        except KeyError as e:
            return f"# 模板填充失败，缺少参数: {e}"

        # 4. 处理当前层级缩进
        if indent_level > 0:
            code_segment = self._indent_code(code_segment, indent_level)

        return code_segment

    def _indent_code(self, code_str, level):
        """对代码块的每一行添加统一的缩进"""
        if not code_str:
            return ""
        lines = code_str.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():  # 非空行才加缩进
                indented_lines.append("    " * level + line)
            else:
                indented_lines.append("")
        return "\n".join(indented_lines)

    def validate_syntax(self, code_str, target_lang="python"):
        """验证生成的代码是否符合语法"""
        if target_lang == "python":
            try:
                ast.parse(code_str)
                return True, "语法正确"
            except SyntaxError as e:
                return False, str(e)
        return True, "待沙盒验证"

    def synthesize_from_evolution(self, logic_tree, target_lang="python"):
        """对外接口：传入进化引擎产生的逻辑树，返回可运行的代码字符串"""
        raw_code = self.synthesize(logic_tree, target_lang)
        is_valid, msg = self.validate_syntax(raw_code, target_lang)
        
        if is_valid:
            return {"success": True, "code": raw_code, "language": target_lang}
        else:
            return {"success": False, "error": f"语法检查失败: {msg}", "raw_code": raw_code}