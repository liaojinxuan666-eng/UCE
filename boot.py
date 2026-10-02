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
    from core.ca_evolver import CAEvolver
except ImportError as e:
    print(f"导入模块失败，请检查文件夹结构。错误: {e}")
    sys.exit(1)

def calculate_target_output(start, end, math_op):
    """计算进化沙盒需要匹配的目标值"""
    try:
        s, e = int(start), int(end)
        if math_op == "PRIM_MATH_MUL":
            result = 1
            for i in range(s, e + 1): result *= i
            return result
        else:
            return sum(range(s, e + 1))
    except Exception:
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
    print("你可以试着说：'计算1到5的乘积' 或 '今天天气真好'。\n")

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
            
            loop_range = params.get("loop_range", ("1", "10"))
            start, end = loop_range[0], loop_range[1]
            
            math_op_hint = params.get("math_op", "NONE")
            signature = f"{target_lang}_{math_op_hint}_{start}_{end}"
            
            cached_tree, cached_lang = db.get_experience_by_signature(signature)
            synth_result = None
            
            if cached_tree:
                print(f"Logos: [记忆检索] 发现匹配的历史经验！(签名: {signature})")
                synth_result = synthesizer.synthesize_from_evolution(cached_tree, cached_lang)
            else:
                print(f"Logos: [记忆检索] 未找到匹配经验 (签名: {signature})")
                target_output = calculate_target_output(start, end, math_op_hint)
                
                if target_output is not None:
                    print(f"Logos: [真·进化沙盒] 目标输出已知为 {target_output}，启动随机变异与试错...")
                    evolver = CAEvolver(target_output, start, end, synthesizer, max_generations=20, population_size=10)
                    evolved_tree, discovered_op, discovered_init = evolver.evolve()
                    
                    if evolved_tree:
                        synth_result = synthesizer.synthesize_from_evolution(evolved_tree, target_lang)
                        if synth_result and synth_result.get("success"):
                            real_math_op = "PRIM_MATH_MUL" if discovered_op == "*" else "PRIM_MATH_ADD"
                            real_signature = f"{target_lang}_{real_math_op}_{start}_{end}"
                            db.add_code_experience(real_signature, evolved_tree, target_lang)
                            print(f"Logos: [记忆固化] 已将新的逻辑存入长期记忆 (签名: {real_signature})。")
                    else:
                        print("Logos: [进化沙盒] 达到最大代数，未能找到正确逻辑。")
                else:
                    print("Logos: [进化沙盒] 无法解析参数，尝试失败。")
                    
            if synth_result and synth_result.get("success"):
                success_msgs = seed_lib.pragmatic_templates.get('success', ["执行完毕，结果如下："])
                print(f"\nLogos: {random.choice(success_msgs)}")
                print("-------------------------")
                print(synth_result["code"])
                print("-------------------------\n")
            else:
                err_msgs = seed_lib.pragmatic_templates.get('error', ["遇到逻辑冲突：{error}"])
                print(f"Logos: {random.choice(err_msgs).format(error='进化未能产生可行代码')}")
                
        elif intent == "greet":
            greet_msgs = seed_lib.pragmatic_templates.get('greet', ["你好，我是 Logos。"])
            print(f"Logos: {random.choice(greet_msgs)}\n")
            
        elif intent == "chat":
            chat_msgs = seed_lib.pragmatic_templates.get('chat', ["我在听。"])
            print(f"Logos: {random.choice(chat_msgs)}\n")
            
        else:
            unknown_msgs = seed_lib.pragmatic_templates.get('unknown', ["我暂时无法理解这个意图。"])
            print(f"Logos: {random.choice(unknown_msgs)}\n")

    print("\n[系统] Logos 已休眠。")
    db.close()

if __name__ == "__main__":
    main()