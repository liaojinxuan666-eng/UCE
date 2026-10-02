# Logos 启动引导程序 (Boot)
# 这是 Logos 的大脑中枢，串联 NLU (耳朵)、DB (记忆)、Core (大脑)、Synthesizer (手) 和 Templates (嘴巴)
# 运行方式：python boot.py

import sys
import pathlib
import random
import time

# 确保能导入各个模块（根据你的实际文件夹结构，可能需微调）
sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent / "core"))
sys.path.append(str(pathlib.Path(__file__).parent / "db"))
sys.path.append(str(pathlib.Path(__file__).parent / "nlu"))
sys.path.append(str(pathlib.Path(__file__).parent / "trainer"))

try:
    from db.logos_db import LogosDB
    from nlu.logos_nlu import LogosNLU
    from uce_seed_library import LogosSeedLibrary
    from code_synthesizer import CodeSynthesizer
except ImportError as e:
    print(f"导入模块失败，请检查文件夹结构。错误: {e}")
    print("确保 core/ db/ nlu/ trainer/ 文件夹里有对应的 .py 文件，且项目根目录下有 boot.py")
    sys.exit(1)

def main():
    print("=======================================")
    print("          Logos (逻各斯) 认知引擎         ")
    print("   纯本地逻辑 · 超维进化 · 无需GPU       ")
    print("=======================================\n")
    
    # 1. 初始化数据库和记忆
    print("[系统] 正在加载长期记忆数据库...")
    db = LogosDB()
    # 检查数据库是否有基础数据
    db.cursor.execute("SELECT COUNT(*) FROM concepts")
    concept_count = db.cursor.fetchone()[0]
    if concept_count == 0:
        print(">>> 警告：数据库是空的！请先运行 python trainer/data_feeder.py 喂食初始知识。")
    else:
        print(f"[系统] 数据库已就绪，当前掌握 {concept_count} 个概念。")

    # 2. 初始化种子库 (包含逻辑原语和语用模板)
    print("[系统] 加载种子标准库...")
    seed_lib = LogosSeedLibrary()

    # 3. 初始化耳朵和手
    nlu = LogosNLU(seed_lib)
    synthesizer = CodeSynthesizer(seed_lib)

    print("\n[系统] Logos 启动完毕！输入 'exit' 退出。")
    print("你可以试着说：'用C语言打印1到10' 或 '用Python写个循环打印1到5'。\n")

    # 4. 主循环 (Loop)
    while True:
        try:
            user_input = input("你: ").strip()
        except EOFError:
            break

        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        # 阶段 1: 感知 (听)
        time.sleep(0.3) # 模拟思考延迟
        parse_result = nlu.parse(user_input)
        
        # 阶段 2: 处理意图
        intent = parse_result.get("intent")
        
        if intent == "generate_code":
            # 提取到参数，开始合成代码
            target_lang = parse_result.get("target_lang")
            logic_tree = parse_result.get("logic_tree")
            
            if "error" in logic_tree:
                print(f"Logos: 抱歉，我的逻辑推演遇到了阻碍：{logic_tree['error']}")
                continue

            # 尝试从数据库里查询历史经验 (自我进化记忆)
            # (目前我们直接传给合成器，后续可在数据库里做缓存查询)
            
            # 阶段 3: 行动 (手 - 合成代码)
            synth_result = synthesizer.synthesize_from_evolution(logic_tree, target_lang)
            
            # 阶段 4: 表达 (嘴)
            if synth_result["success"]:
                print(f"\nLogos: {random.choice(seed_lib.pragmatic_templates['success'])}")
                print("-------------------------")
                print(synth_result["code"])
                print("-------------------------\n")
            else:
                print(f"Logos: {random.choice(seed_lib.pragmatic_templates['error'])}")
                print(f"错误详情: {synth_result['error']}\n")
                
        elif intent == "greet":
            print(f"Logos: {random.choice(seed_lib.pragmatic_templates['greet'])}\n")
            
        else:
            print(f"Logos: {random.choice(seed_lib.pragmatic_templates['unknown'])}\n")

    print("\n[系统] Logos 已休眠。")
    db.close()

if __name__ == "__main__":
    main()