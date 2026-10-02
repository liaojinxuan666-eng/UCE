# Logos 启动引导程序 (Boot)
# 这是 Logos 的大脑中枢，串联 NLU (耳朵)、DB (记忆)、Core (大脑)、Synthesizer (手) 和 Templates (嘴巴)
# 运行方式：python boot.py

import sys
import pathlib
import random
import time

# ================= 路径兼容处理 =================
BASE_DIR = pathlib.Path(__file__).parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "core"))
sys.path.append(str(BASE_DIR / "db"))
sys.path.append(str(BASE_DIR / "nlu"))
sys.path.append(str(BASE_DIR / "trainer"))

# 尝试导入核心模块
try:
    from db.logos_db import LogosDB
    from nlu.logos_nlu import LogosNLU
    from core.uce_seed_library import LogosSeedLibrary
    from core.code_synthesizer import CodeSynthesizer
except ImportError as e:
    # 兼容平铺目录的情况
    try:
        from logos_db import LogosDB
        from logos_nlu import LogosNLU
        from uce_seed_library import LogosSeedLibrary
        from code_synthesizer import CodeSynthesizer
    except ImportError as e2:
        print(f"导入模块失败，请检查文件夹结构。错误: {e2}")
        sys.exit(1)

def main():
    print("=======================================")
    print("          Logos (逻各斯) 认知引擎         ")
    print("   纯本地逻辑 · 超维进化 · 无需GPU       ")
    print("=======================================\n")
    
    # 1. 初始化数据库和记忆
    print("[系统] 正在加载长期记忆数据库...")
    try:
        db = LogosDB()
        db.cursor.execute("SELECT COUNT(*) FROM concepts")
        concept_count = db.cursor.fetchone()[0]
        if concept_count == 0:
            print(">>> 警告：数据库是空的！请先运行 python trainer/data_feeder.py 喂食初始知识。")
        else:
            print(f"[系统] 数据库已就绪，当前掌握 {concept_count} 个概念。")
    except Exception as e:
        print(f"[错误] 数据库加载失败: {e}")
        sys.exit(1)

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
            # 检查 NLU 解析时是不是已经报错了（比如逻辑冲突）
            if "error" in parse_result:
                err_msgs = seed_lib.pragmatic_templates.get('error', ["抱歉，我的逻辑推演遇到了阻碍：{error}"])
                print(f"Logos: {random.choice(err_msgs).format(error=parse_result['error'])}")
                continue
                
            target_lang = parse_result.get("target_lang")
            logic_tree = parse_result.get("logic_tree")
            
            if logic_tree is None:
                print("Logos: 我没能理解这个逻辑组合，请换个说法。")
                continue

            # 阶段 3: 行动 (手 - 合成代码)
            synth_result = synthesizer.synthesize_from_evolution(logic_tree, target_lang)
            
            # 阶段 4: 表达 (嘴)
            if synth_result["success"]:
                success_msgs = seed_lib.pragmatic_templates.get('success', ["执行完毕，结果如下："])
                print(f"\nLogos: {random.choice(success_msgs)}")
                print("-------------------------")
                print(synth_result["code"])
                print("-------------------------\n")
                
                # ======== 预留接口：真正的进化引擎接入点 ========
                # 当用户要求更复杂的逻辑（如"计算1到100的和"）时，
                # 我们让系统提示准备进化，但这部分逻辑需要 ca_evolver 的实际参与。
                # 目前我们只检测关键词，并提示用户"正在准备进化"。
                if any(kw in user_input for kw in ["和", "累加", "求和"]):
                    print("Logos: 这属于未知的复合逻辑。正在唤醒元胞自动机进化沙盒...")
                    print("Logos: [进化引擎待接入，当前只返回基础模板结果]\n")
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