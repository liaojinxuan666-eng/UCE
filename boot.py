# Logos 启动引导程序 (Boot)
import sys
import pathlib
import random
import time
import re

# ================= 路径兼容处理 =================
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
def trigger_evolution(user_input, target_lang):
    print("Logos: [进化沙盒] 正在检索逻辑原语...")
    time.sleep(0.3)
    
    match = re.search(r"(\d+)\s*(?:到|至|~|-)\s*(\d+)", user_input)
    start = match.group(1) if match else "1"
    end = match.group(2) if match else "10"
    
    if "求和" in user_input or "和" in user_input or "计算" in user_input:
        print("Logos: [进化沙盒] 正在组合 PRIM_VAR_DECL + PRIM_LOOP_FOR + PRIM_MATH_ADD...")
        time.sleep(0.3)
        return {
            "primitive": "PRIM_SEQUENCE",
            "args": {
                "body": [
                    {"primitive": "PRIM_VAR_DECL", "args": {"var_name": "total", "value": "0"}},
                    {"primitive": "PRIM_LOOP_FOR", "args": {
                        "iter_var": "i", "start": start, "end": end,
                        "body": {"primitive": "PRIM_VAR_DECL", "args": {"var_name": "total", "value": "total + i"}}
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
        # 这里就是刚才出错的地方，修正为正确的点号
        db.cursor.execute("SELECT COUNT(*) FROM concepts")
        concept_count = db.cursor.fetchone()[0]
        print(f"[系统] 数据库已就绪，当前掌握 {concept_count} 个概念。")
    except Exception as e:
        print(f"[错误] 数据库加载失败: {e}")
        sys.exit(1)

    seed_lib = LogosSeedLibrary()
    nlu = LogosNLU(seed_lib)
    synthesizer = CodeSynthesizer(seed_lib)

    print("\n[系统] Logos 启动完毕！输入 'exit' 退出。")
    print("你可以试着说：'计算1到100的和' 或 '用Python写个判断奇偶数的代码'。\n")

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
            synth_result = None
            
            if "logic_tree" in parse_result:
                synth_result = synthesizer.synthesize_from_evolution(parse_result["logic_tree"], target_lang)
            
            if not synth_result or not synth_result.get("success"):
                evolved_tree = trigger_evolution(user_input, target_lang)
                if evolved_tree:
                    synth_result = synthesizer.synthesize_from_evolution(evolved_tree, target_lang)
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
                if "到" not in user_input and "至" not in user_input:
                    print("Logos: 提示：未指定范围，默认使用 1 到 10。\n")
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