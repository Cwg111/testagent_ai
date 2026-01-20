# @FileName  :client.py
# @Time      :2026/1/19 10:11
# @Author    :ChenWenGang
from typing import Dict
from openai import OpenAI
import json
from src.config import CONFIG


class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=CONFIG["llm"]["api_key"],
                             base_url=CONFIG["llm"]["base_url"],
                             timeout=CONFIG["llm"]["timeout"])
        self.model = CONFIG["llm"]["model"]
        self.temperature = CONFIG["llm"]["temperature"]

    def _call_llm(self, prompt: str, force_json: bool = True) -> str:
        """
        调用大模型
        :param prompt: 提示词
        :param force_json: 是否强制返回JSON格式，默认为True（指定JSON格式），False则不指定
        :return: 大模型返回的内容
        """
        request_params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }
        if force_json:
            request_params["response_format"] = {"type": "json_object"}
        try:
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content
        except Exception as e:
            return f"生成失败，{str(e)}"

    # ----------------测试岗能力------------
    def parse_requirement_to_testcase(self, requirement_text: str) -> Dict:
        """
        解析需求->生成结构化功能测试用例（json格式）
        :param requirement_text: 需求文档
        :return: 生成的测试用例
        """
        prompt = f"""
        你是资深测试工程师，生成结构化功能测试用例，请勿返回其他内容：
        需求文档：{requirement_text}
        JSON结构：
        {{
            "feature": "功能模块名称",
            "cases": [
                {{
                    "case_id": "CASE_001",
                    "title": "用例标题",
                    "preconditions": "前置条件",
                    "steps":["步骤1","步骤2"],
                    "expected":"预期结果"
                }}
            ]
        }}
        """
        llm_response = self._call_llm(prompt)
        return json.loads(llm_response)

    def testcase_to_web_script(self, case_text: str) -> str:
        """
        测试用例->Selenium+pytest标准化脚本
        :param case_text: 测试用例
        :return: 生成的自动化测试脚本
        """
        prompt = f"""
        你是资深Web自动化测试工程师，将测试用例转为**Selenium+pytest标准化脚本**，严格遵循以下模板和规则：
        ### 核心规则：
        1. 必须完全匹配示例的代码结构、注释风格、命名规范；
        2. 导入包必须包含：pytest、selenium所有核心模块、webdriver_manager、Chrome Service；
        3. 全局配置用大写常量（如TAIGA_LOGIN_URL），根据用例自动替换为实际测试地址；
        4. Fixture命名为driver，scope=module，自动管理Chrome驱动（用ChromeDriverManager）；
        5. 测试用例函数命名格式：test_<CASE_ID>_<功能描述>（如test_LOG_001_login_success）；
        6. 所有元素操作必须用显式等待（WebDriverWait），超时时间10秒；
        7. 捕获TimeoutException，用pytest.fail抛出失败信息；
        8. 每个用例包含步骤注释、断言、成功/失败打印提示；
        9. 仅返回代码，无任何多余文字、解释；
        10. 元素定位优先用ID，其次CSS_SELECTOR，最后XPath。

        ### 示例模板（必须严格对齐）：
        import pytest
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        # --------------------------
        # 🔧 全局配置与 Fixture
        # --------------------------
        TAIGA_LOGIN_URL = "http://your-taiga-domain/login"  # 替换为你的测试地址
        TAIGA_HOME_URL = "http://your-taiga-domain/home"

        @pytest.fixture(scope="module")
        def driver():
            \"\"\"初始化 Chrome 浏览器，自动管理驱动\"\"\"
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.maximize_window()
            yield driver
            driver.quit()

        # --------------------------
        # 🧪 测试用例
        # --------------------------
        def test_LOG_001_login_success(driver):
            \"\"\"验证正确账号密码登录成功 (LOG-001)\"\"\"
            # 1. 访问登录页
            driver.get(TAIGA_LOGIN_URL)

            # 2. 输入正确用户名和密码
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "id_username"))
            )
            username_input.send_keys("admin")

            password_input = driver.find_element(By.ID, "id_password")
            password_input.send_keys("Admin@123456")

            # 3. 点击登录按钮
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # 验证预期结果
            try:
                WebDriverWait(driver, 10).until(EC.url_to_be(TAIGA_HOME_URL))
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info .avatar"))
                )
                assert "home" in driver.current_url, "登录后未跳转到首页"
                print("✅ LOG-001 测试通过：正确账号密码登录成功")
            except TimeoutException:
                pytest.fail("❌ LOG-001 测试失败：登录后未加载首页或未显示头像")

        ### 测试用例内容（根据此生成脚本）：
        {case_text}
        """
        script = self._call_llm(prompt, force_json=False)
        # # 清理markdown代码块标记
        # script=script.strip("```python").strip("```").strip()
        return script

    def parse_command_intent(self, command_text: str) -> Dict:
        """
        解析用户指令意图（兜底用，关键字匹配失败时调用）
        :param command_text: 指令
        :return: 解析结果
        """
        prompt = f"""
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
        llm_response = self._call_llm(prompt)
        return json.loads(llm_response)


if __name__ == "__main__":
    run_code = 0
