class LogosSeedLibrary:
    def __init__(self):
        self.logic_primitives = { ... } # 保持原样
        self.syntax_mappings = { ... } # 保持原样
        
        # 扩充语用模板
        self.pragmatic_templates = {
            "greet": ["你好，我是 Logos。", "我在。有什么想聊的吗？"],
            "success": ["执行完毕，结果如下：", "推演成功，得出的结论是：", "代码已跑通，输出如下："],
            "error": ["遇到了一点逻辑冲突：{error}。", "运行失败了：{error}。"],
            "unknown": ["我没太听懂，你可以换个说法。", "我的逻辑库还没覆盖这个领域，但我可以学。"],
            "think": ["正在检索记忆图...", "正在启动元胞自动机进化沙盒..."],
            # 新增闲聊模板
            "chat": [
                "听起来不错。",
                "嗯，我明白你的感受。",
                "这是个有趣的话题。",
                "你可以多跟我说说。",
                "我只是个逻辑引擎，但我愿意听你说。"
            ]
        }