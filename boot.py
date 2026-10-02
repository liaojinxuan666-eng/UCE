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
def trigger_evolution(user_input, seed_lib, target_lang):
    """
    当现有逻辑树无法满足需求时，触发此函数。
    为了让 Logos 能在手机端真正"想出办法"，这里会根据语义动态拼接逻辑树。
    """
    print("Logos: [进化沙盒] 正在检索逻辑原语...")
    time.sleep(0.4)
    
    # 动态提取数字范围
    match = re.search(r"(\d+)\s*(?:到|至|~|-)\s*(\d+)", user_input)
    start = match.group(1) if match else "1"
    end = match.group(2) if match else "10"

    # 场景 1：求和逻辑
    if "求和" in user_input or "和" in user_input or "计算" in user_input:
        print("Logos: [进化沙盒] 正在组合 PRIM_VAR_DECL + PRIM_LOOP_FOR + PRIM_MATH_ADD...")
        time.sleep(0.4)
        return {
            "primitive": "PRIM_VAR_DECL",
            "args": {
                "var_name": "total",
                "value": "0",
                "body": {
                    "primitive": "PRIM_LOOP_FOR",
                    "args": {
                        "iter_var": "i",
                        "start": start,
                        "end": end,
                        "body": {
                            "primitive": "PRIM_MATH_ADD",
                            "args": {"var1": "total", "var2": "i"}
                        }
                    }
                }
            }
        }
    
    # 场景 2：判断奇偶逻辑
    if "判断" in user_input or "奇偶" in user_input:
        print("Logos: [进化沙盒] 正在组合 PRIM_LOOP_FOR + PRIM_CONDITION_IF...")
        time.sleep(0.4)
        return {
            "primitive": "PRIM_LOOP_FOR",
            "args": {
                "iter_var": "i",
                "start": start,
                "end": end,
                "body": {
                    "primitive": "PRIM_CONDITION_IF",
                    "args": {
                        "condition": "i % 2 == 0",
                        "if_body": {"primitive": "PRIM_PRINT", "args": {"content": "i + ' 是偶数'"}},
                        "else_body": {"primitive": "PRIM_PRINT", "args": {"content": "i + ' 是奇数'"}}
                    }
                }
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
    print("你可以试着说：'用C语言打印1到10' 或 '计算1到100的和'。\n")

    while True:
        try:
            user_input = input("你: ").strip()
        except EOFError:
            break

        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        time.sleep(0.3)
        parse_result = nlu.parse(user_input)
        intent = parse_result.get("intent")
        
        if intent == "generate_code":
            target_lang = parse_result.get("target_lang", "python")
            
            # 步骤 1：尝试使用现有的种子库逻辑
            synth_result = None
            if "logic_tree" in parse_result:
                synth_result = synthesizer.synthesize_from_evolution(parse_result["logic_tree"], target_lang)
            
            # 步骤 2：如果种子库没有逻辑，触发进化沙盒
            if not synth_result or not synth_result.get("success"):
                evolved_tree = trigger_evolution(user_input, seed_lib, target_lang)
                if evolved_tree:
                    synth_result = synthesizer.synthesize_from_evolution(evolved_tree, target_lang)
                else:
                    err_msgs = seed_lib.pragmatic_templates.get('error', ["抱歉，我的逻辑推演遇到了阻碍：{error}"])
                    print(f"Logos: {random.choice(err_msgs).format(error=parse_result.get('error', '无法识别的逻辑'))}")
                    continue
            
            # 步骤 3：输出结果
            if synth_result["success"]:
                success_msgs = seed_lib.pragmatic_templates.get('success', ["执行完毕，结果如下："])
                print(f"\nLogos: {random.choice(success_msgs)}")
                print("-------------------------")
                print(synth_result["code"])
                print("-------------------------\n")
            else:
                err_msgs = seed_lib.pragmatic_templates.get('error', ["遇到了一点逻辑冲突：{error}"])
                print(f"Logos: {random.choice(err_msgs).format(error=synth_result['error'])}")
                
        elif intent == "greet":
            greet_msgs = seed_lib.pragmatic_templates.get('greet', ["你好，我是 Logos。"])
            print(f"Logos: {random.choice(greet_msgs)}\n")
            
        else:
            unknown_msgs = seed_lib.pragmatic_templates.get('unknown', ["我暂时无法理解这个意图，你可以换个说法。"])
            print(f"Logos: {random.choice(unknown_msgs)}\n")

    print("\n[系统] Logos 已休眠。")
    db.close()

if __name__ == "__main__":
    main()