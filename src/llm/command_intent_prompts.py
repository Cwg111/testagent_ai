# @FileName  :command_intent_prompts.py
# @Time      :2026/1/21 16:18
# @Author    :ChenWenGang
COMMAND_INTENT_PROMPTS = """
        分析用户指令意图，仅返回JSON格式结果，无多余文字
        指令：{command_text}
        JSON结构：
        {{
            "intent": "generate_case"|"generate_script", # 仅这两个值
            "use_context": true|false# 是否使用上下文
        }}
        规则：
        1. generate_case：生成测试用例（如指令含“生成测试用例”“创建用例”“编写测试用例”）
        2. generate_script：生成自动化测试脚本（如指令含“生成脚本”“创建测试脚本”）
        3. use_context：指令含“上面的”“之前的“”已生成的”则为true，否则为false
        """

if __name__ == "__main__":
    run_code = 0
