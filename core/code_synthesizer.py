# Logos 核心组件 9：代码合成器 (Code Synthesizer)
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

        # 特殊处理：如果是列表（通常出现在 PRIM_SEQUENCE 的 body 里）
        if isinstance(logic_tree, list):
            codes = []
            for item in logic_tree:
                codes.append(self.synthesize(item, target_lang, indent_level))
            return "\n".join(codes)

        primitive = logic_tree.get("primitive")
        args = logic_tree.get("args", {})

        # PRIM_SEQUENCE 是透明容器，内部的 body 列表元素各自负责自己的缩进
        if primitive == "PRIM_SEQUENCE":
            sub_codes = []
            for item in args.get("body", []):
                sub_codes.append(self.synthesize(item, target_lang, indent_level))
            return "\n".join(sub_codes)

        # 1. 获取语法模板
        template = self.library.get_language_template(target_lang, primitive)
        if not template:
            return f"# 未知原语: {primitive}"

        # 2. 递归处理嵌套参数
        processed_args = {}
        for key, value in args.items():
            if isinstance(value, dict) and "primitive" in value:
                processed_args[key] = self.synthesize(value, target_lang, indent_level + 1)
            elif isinstance(value, list):
                sub_codes = []
                for item in value:
                    sub_codes.append(self.synthesize(item, target_lang, indent_level + 1))
                processed_args[key] = "\n".join(sub_codes)
            else:
                processed_args[key] = str(value)

        # 3. 填充模板
        try:
            code_segment = template.format(**processed_args)
        except KeyError as e:
            return f"# 模板填充失败，缺少参数: {e}"

        # 4. 对当前生成的代码块整体进行缩进
        if indent_level > 0:
            code_segment = self._indent_code(code_segment, indent_level)
            
        return code_segment

    def _indent_code(self, code_str, level):
        """对代码块的每一行添加统一的缩进"""
        lines = code_str.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append("    " * level + line)
            else:
                indented_lines.append("")
        return "\n".join(indented_lines)

    def validate_syntax(self, code_str, target_lang="python"):
        if target_lang == "python":
            try:
                ast.parse(code_str)
                return True, "语法正确"
            except SyntaxError as e:
                return False, str(e)
        return True, "待沙盒验证"

    def synthesize_from_evolution(self, logic_tree, target_lang="python"):
        raw_code = self.synthesize(logic_tree, target_lang)
        is_valid, msg = self.validate_syntax(raw_code, target_lang)
        
        if is_valid:
            return {"success": True, "code": raw_code, "language": target_lang}
        else:
            return {"success": False, "error": f"语法检查失败: {msg}", "raw_code": raw_code}