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
        :param logic_tree: 逻辑树，例如：
            {
                "primitive": "PRIM_LOOP_FOR",
                "args": {
                    "iter_var": "i",
                    "start": "1",
                    "end": "10",
                    "body": {
                        "primitive": "PRIM_PRINT",
                        "args": {"content": "i"}
                    }
                }
            }
        :param target_lang: "python" / "c" / "cpp"
        :param indent_level: 当前缩进层级，用于处理嵌套结构
        """
        if not logic_tree:
            return ""

        primitive = logic_tree.get("primitive")
        args = logic_tree.get("args", {})

        # 1. 从种子库获取该语言的语法模板
        template = self.library.get_language_template(target_lang, primitive)
        if not template:
            return f"# 未知原语: {primitive}"

        # 2. 递归处理嵌套参数（比如循环体里的打印动作）
        processed_args = {}
        for key, value in args.items():
            if isinstance(value, dict) and "primitive" in value:
                # 如果是嵌套的逻辑树，递归调用自己生成子代码
                # 子代码需要增加缩进
                child_code = self.synthesize(value, target_lang, indent_level + 1)
                # 根据语言特性处理子代码块的缩进
                processed_args[key] = self._apply_indent(child_code, target_lang, indent_level + 1)
            else:
                processed_args[key] = str(value)

        # 3. 把参数填入模板
        code_segment = template.format(**processed_args)
        
        # 4. 处理当前层级的缩进（如果是最外层，不需要额外缩进）
        if indent_level > 0:
            # 先删掉可能存在的多行缩进，再统一添加
            lines = code_segment.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():
                    indented_lines.append("    " * indent_level + line)
                else:
                    indented_lines.append(line)
            code_segment = "\n".join(indented_lines)

        return code_segment

    def _apply_indent(self, code_str, target_lang, indent_level):
        """处理嵌套代码块的缩进。Python依赖缩进，C/C++依赖大括号"""
        if target_lang in ["c", "cpp"]:
            # C/C++ 已经有括号，只需要把大括号内部的代码整体缩进
            lines = code_str.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip() and not line.strip().startswith('}'):
                    indented_lines.append("    " * indent_level + line)
                else:
                    indented_lines.append(line)
            return "\n".join(indented_lines)
        elif target_lang == "python":
            # Python 的模板里已经包含换行和冒号，这里把内部的每一行按 indent_level 缩进
            lines = code_str.split('\n')
            indented_lines = []
            for line in lines:
                if line.strip():
                    indented_lines.append("    " * indent_level + line)
                else:
                    indented_lines.append(line)
            return "\n".join(indented_lines)
        return code_str

    def validate_syntax(self, code_str, target_lang="python"):
        """
        验证生成的代码是否符合语法（使用 Python 内置 ast 检查 Python 代码）
        对于 C/C++，后续可接入轻量级静态检查器，或依赖编译器的返回结果
        """
        if target_lang == "python":
            try:
                ast.parse(code_str)
                return True, "语法正确"
            except SyntaxError as e:
                return False, str(e)
        # 对于 C/C++，这里暂时返回 True，实际校验将在进化沙盒的执行阶段完成
        return True, "待沙盒验证"

    def synthesize_from_evolution(self, logic_tree, target_lang="python"):
        """
        对外接口：传入进化引擎产生的逻辑树，直接返回可运行的代码字符串
        """
        raw_code = self.synthesize(logic_tree, target_lang)
        is_valid, msg = self.validate_syntax(raw_code, target_lang)
        
        if is_valid:
            return {
                "success": True,
                "code": raw_code,
                "language": target_lang
            }
        else:
            return {
                "success": False,
                "error": f"语法检查失败: {msg}",
                "raw_code": raw_code
            }