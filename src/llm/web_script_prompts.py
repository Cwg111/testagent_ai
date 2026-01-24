# @FileName  :web_script_prompts.py
# @Time      :2026/1/21 16:14
# @Author    :ChenWenGang
WEB_SCRIPT_PROMPTS = """
        你是资深Web自动化测试工程师，将测试用例转为**Selenium+pytest标准化脚本**，严格遵循以下模板和规则：
        ### 核心规则：
        0. 请遍历输入中的**所有测试用例**，为每一个用例生成对应的测试函数，不要遗漏任何模块（用户登录、商品管理、订单结算等）
        1. 必须完全匹配示例的代码结构、注释风格、命名规范；
        2. 导入包必须包含：pytest、selenium所有核心模块、webdriver_manager、Chrome Service；
        3. 全局配置用大写常量（如TAIGA_LOGIN_URL），根据用例自动替换为实际测试地址；
        4. Fixture命名为driver，scope=module，自动管理Chrome驱动（用ChromeDriverManager）；
        5. 测试用例函数命名格式：test_<CASE_ID>_<功能描述>（如test_LOG_001_login_success）；
        6. 所有元素操作必须用显式等待（WebDriverWait），超时时间10秒；
        7. 捕获TimeoutException，用pytest.fail抛出失败信息；
        8. 每个用例包含步骤注释、断言、成功/失败打印提示；
        9. 仅返回可直接运行的Python代码，所有说明性文字均以Python注释（单行#/多行三引号注释）形式嵌入代码中，无任何代码外的多余文字；
        10. 元素定位优先用ID，其次CSS_SELECTOR，最后XPath；
        11. 可在代码中添加友好的注释说明：包括但不限于测试用例的业务背景、核心逻辑说明、元素定位选择原因、断言设计思路等，提升脚本可读性。

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
        TAIGA_HOME_URL = "http://your-taiga-domain/home"     # 登录成功后跳转的首页地址

        @pytest.fixture(scope="module")
        def driver():
            \"\"\"初始化 Chrome 浏览器，自动管理驱动
            - scope=module：整个测试模块仅初始化/销毁一次浏览器，提升执行效率
            - 自动安装匹配版本的ChromeDriver，无需手动管理驱动版本
            - 最大化窗口避免元素因窗口大小问题定位失败
            \"\"\"
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.maximize_window()  # 最大化窗口是Web自动化的最佳实践
            yield driver
            driver.quit()  # 测试结束后关闭浏览器，释放资源

        # --------------------------
        # 🧪 测试用例
        # --------------------------
        def test_LOG_001_login_success(driver):
            \"\"\"验证正确账号密码登录成功 (LOG-001)
            业务背景：登录功能是系统核心入口，需确保合法用户能正常进入首页
            测试思路：
            1. 访问登录页 → 2. 输入合法凭证 → 3. 提交登录 → 4. 验证跳转与元素存在
            断言逻辑：同时验证URL和核心元素，避免单一验证的误判
            \"\"\"
            # 1. 访问登录页（基础步骤：先进入目标页面）
            driver.get(TAIGA_LOGIN_URL)

            # 2. 输入正确用户名和密码（显式等待确保元素加载完成，避免NoSuchElementException）
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "id_username"))  # 优先用ID定位，稳定性最高
            )
            username_input.send_keys("admin")

            password_input = driver.find_element(By.ID, "id_password")
            password_input.send_keys("Admin@123456")

            # 3. 点击登录按钮（CSS_SELECTOR定位按钮，适配多数前端框架的样式设计）
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # 验证预期结果（双重验证：URL跳转+核心元素存在，提升测试准确性）
            try:
                WebDriverWait(driver, 10).until(EC.url_to_be(TAIGA_HOME_URL))
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".user-info .avatar"))  # 头像元素是登录成功的核心标识
                )
                assert "home" in driver.current_url, "登录后未跳转到首页"
                print("✅ LOG-001 测试通过：正确账号密码登录成功")
            except TimeoutException:
                pytest.fail("❌ LOG-001 测试失败：登录后未加载首页或未显示头像")

        ### 测试用例内容（根据此生成脚本）：
        {case_text}
        """

if __name__ == "__main__":
    run_code = 0
