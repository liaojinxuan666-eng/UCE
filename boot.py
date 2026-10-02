# Logos 启动引导程序 (Boot)
import sys
import pathlib
import random
import time
import re

BASE_DIR = pathlib.Path(__file__).parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "core"))
sys.path.append(str(BASE_DIR / "db"))
sys.path.append(str(BASE_DIR / "nlu"))
sys.path.append(str(BASE_DIR / "trainer"))

try:
    from db.logos_db import LogosDB
    from nlu.logos_nlu import LogosNLU
    from core.uce_seed_library import LogosSeedLibrary
    from core.code_synthesizer import CodeSynthesizer
except ImportError as e:
    try:
        from logos_db import LogosDB
        from logos_nlu import LogosNLU
        from uce_seed_library import LogosSeedLibrary
        from code_synthesizer import CodeSynthesizer
    except ImportError as e2:
        print(f"导入模块失败，请检查文件夹结构。错误: {e2}")
        sys.exit(1)

# ================= 进化引擎的快速触发模块 =================
def trigger_evolution(user_input, params, target_lang):
    print("Logos: [进化沙盒] 正在检索逻辑原语...")
    time.sleep(0.3)
    
    loop_range = params.get("loop_range", ("1", "10"))
    start, end = loop_range[0], loop_range[1]
    math_op = params.get("math_op")

    if math_op:
        print(f"Logos: [进化沙盒] 正在组合 PRIM_VAR_DECL + PRIM_LOOP_FOR + {math_op}...")
        time.sleep(0.3)
        
        init_value = "1" if math_op == "PRIM_MATH_MUL" else "0"
        
        return {
            "primitive": "PRIM_SEQUENCE",
            "args": {
                "body": [
                    {"primitive": "PRIM_VAR_DECL", "args": {"var_name": "total", "value": init_value}},
                    {"primitive": "PRIM_LOOP_FOR", "args": {
                        "iter_var": "i", "start": start, "end": end,
                        "body": {"primitive": "PRIM_VAR_DECL", "args": {"var_name": "total", "value": f"total { '+' if math_op == 'PRIM_MATH_ADD' else '*' } i"}}
                    }},
                    {"primitive": "PRIM_PRINT", "args": {"content": "total"}}
                ]
            }
        }

    if "判断" in user_input or "奇偶" in user_input:
        print("Logos: [进化沙盒] 正在组合 PRIM_LOOP_FOR + PRIM_CONDITION_IF...")
        time.sleep(0.3)
        return {
            "primitive": "PRIM_SEQUENCE",
            "args": {
                "body": [
                    {"primitive": "PRIM_LOOP_FOR", "args": {
                        "iter_var": "i", "start": start, "end": end,
                        "body": {
                            "primitive": "PRIM_CONDITION_IF",
                            "args": {
                                "condition": "i % 2 == 0",
                                "if_body": {"primitive": "PRIM_PRINT", "args": {"content": "str(i) + ' 是偶数'"}},
                                "else_body": {"primitive": "PRIM_PRINT", "args": {"content": "str(i) + ' 是奇数'"}}
                            }
                        }
                    }}
                ]
            }
        }
    return None

def main():
    print("=======================================")
    print("          Logos (逻各斯) 认知引擎         ")
    print("   纯本地逻辑 · 超维进化 · 无需GPU       ")
    print("=======================================\n")
    
    try:
        db = LogosDB()
        db.cursor.execute("SELECT COUNT(*) FROM code_experience")
        exp_count = db.cursor.fetchone()[0]
        print(f"[系统] 数据库已就绪，当前掌握 {exp_count} 条逻辑经验。")
    except Exception as e:
        print(f"[错误] 数据库加载失败: {e}")
        sys.exit(1)

    seed_lib = LogosSeedLibrary()
    nlu = LogosNLU(seed_lib)
    synthesizer = CodeSynthesizer(seed_lib)

    print("\n[系统] Logos 启动完毕！输入 'exit' 退出。")
    print("你可以试着说：'计算1到100的和' 或 '计算1到5的乘积'。\n")

    while True:
        try:
            user_input = input("你: ").strip()
        except EOFError:
            break

        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        time.sleep(0.2)
        parse_result = nlu.parse(user_input)
        intent = parse_result.get("intent")
        
        if intent == "generate_code":
            target_lang = parse_result.get("target_lang", "python")
            params = parse_result.get("params", {})
            synth_result = None
            
            # ================= 核心：构建记忆签名 =================
            math_op = params.get("math_op", "NONE")
            loop_range = params.get("loop_range", ("1", "10"))
            # 签名格式：语言_操作_起始_结束 (例如: python_MUL_1_5)
            signature = f"{target_lang}_{math_op}_{loop_range[0]}_{loop_range[1]}"
            
            # 步骤 1：从数据库检索是否有现成的经验
            cached_tree, cached_lang = db.get_experience_by_signature(signature)
            
            if cached_tree:
                print(f"Logos: [记忆检索] 发现匹配的历史经验！(签名: {signature})")
                synth_result = synthesizer.synthesize_from_evolution(cached_tree, cached_lang)
            else:
                # 步骤 2：如果没有经验，则触发进化沙盒
                print(f"Logos: [记忆检索] 未找到匹配经验 (签名: {signature})，启动进化沙盒...")
                evolved_tree = trigger_evolution(user_input, params, target_lang)
                if evolved_tree:
                    synth_result = synthesizer.synthesize_from_evolution(evolved_tree, target_lang)
                    # 成功生成代码后，存入数据库！
                    if synth_result and synth_result.get("success"):
                        db.add_code_experience(signature, evolved_tree, target_lang)
                        print(f"Logos: [记忆固化] 已将新逻辑存入长期记忆。")
                else:
                    err_msgs = seed_lib.pragmatic_templates.get('error', ["抱歉，逻辑推演遇到阻碍：{error}"])
                    print(f"Logos: {random.choice(err_msgs).format(error=parse_result.get('error', '无法识别'))}")
                    continue
            
            if synth_result and synth_result.get("success"):
                success_msgs = seed_lib.pragmatic_templates.get('success', ["执行完毕，结果如下："])
                print(f"\nLogos: {random.choice(success_msgs)}")
                print("-------------------------")
                print(synth_result["code"])
                print("-------------------------\n")
            else:
                err_msgs = seed_lib.pragmatic_templates.get('error', ["遇到逻辑冲突：{error}"])
                print(f"Logos: {random.choice(err_msgs).format(error=synth_result.get('error', '合成失败'))}")
                
        elif intent == "greet":
            greet_msgs = seed_lib.pragmatic_templates.get('greet', ["你好，我是 Logos。"])
            print(f"Logos: {random.choice(greet_msgs)}\n")
        else:
            unknown_msgs = seed_lib.pragmatic_templates.get('unknown', ["我暂时无法理解这个意图。"])
            print(f"Logos: {random.choice(unknown_msgs)}\n")

    print("\n[系统] Logos 已休眠。")
    db.close()

if __name__ == "__main__":
    main()