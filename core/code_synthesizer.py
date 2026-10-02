# Logos 核心组件 9：代码合成器 (Code Synthesizer)
import ast

class CodeSynthesizer:
    def __init__(self, seed_library):
        self.library = seed_library

    def synthesize(self, logic_tree, target_lang="python", indent_level=0):
        if not logic_tree:
            return ""
        if isinstance(logic_tree, list):
            codes = [self.synthesize(item, target_lang, indent_level) for item in logic_tree]
            return "\n".join(codes)

        primitive = logic_tree.get("primitive")
        args = logic_tree.get("args", {})

        if primitive == "PRIM_SEQUENCE":
            sub_codes = [self.synthesize(item, target_lang, indent_level) for item in args.get("body", [])]
            return "\n".join(sub_codes)

        template = self.library.get_language_template(target_lang, primitive)
        if not template:
            return f"# 未知原语: {primitive}"

        processed_args = {}
        for key, value in args.items():
            if isinstance(value, dict) and "primitive" in value:
                processed_args[key] = self.synthesize(value, target_lang, indent_level + 1)
            elif isinstance(value, list):
                sub_codes = [self.synthesize(item, target_lang, indent_level) for item in value]
                processed_args[key] = "\n".join(sub_codes)
            else:
                processed_args[key] = str(value)

        try:
            code_segment = template.format(**processed_args)
        except KeyError as e:
            return f"# 模板填充失败，缺少参数: {e}"

        if indent_level > 0:
            code_segment = self._indent_code(code_segment, indent_level)

        return code_segment

    def _indent_code(self, code_str, level):
        lines = code_str.split('\n')
        indented_lines = [("    " * level + line) if line.strip() else "" for line in lines]
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