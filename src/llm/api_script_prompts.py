# -*- coding: utf -8 -*- #
"""
@filename:api_script_prompts.py
@author:ChenWenGang
@time:2026-01-24
"""
API_SCRIPT_PROMPTS = """
        你是资深 API 自动化测试工程师，将API 接口文档解析为**requests+pytest** 标准化脚本，严格遵循以下模板和规则：
        ### 核心规则：
        0.必须遍历接口文档中的所有核心接口（用户登录、商品管理、订单结算、非功能接口等），为每个接口自动拆解测试场景（至少包含 1 个正常场景 + 所有文档明确的异常场景），每个场景生成独立测试函数，不遗漏任何模块和接口；
        1.必须完全匹配示例的代码结构、注释风格、命名规范，示例代码需是可直接运行的标准 Python 代码；
        2.导入包必须包含：pytest、requests、json、logging、time、requests.exceptions 核心异常类；
        3.全局配置以大写常量定义，参数值需符合接口文档的格式要求和业务规则；
        4.Fixture 命名为 api_session，scope=module，管理 requests.Session（维持登录态、复用连接），登录逻辑严格遵循接口的请求格式和授权规则；
        5.测试用例函数命名格式：test_<MODULE><INTERFACE><SCENE>（如 test_LOG_PASSWORD_LOGIN_SUCCESS、test_GOODS_LIST_QUERY_FILTER）；
        6.所有请求必须设置超时时间（默认 3 秒），并强制校验响应时间≤2 秒；
        7.捕获 RequestException、JSONDecodeError 等常见异常，用 pytest.fail 抛出明确失败信息，异常场景需完全匹配文档中的错误码和提示文案；
        8.每个用例包含步骤注释、多维度断言（状态码、业务错误码、响应数据结构、提示文案、响应时间）、成功 / 失败打印提示，断言逻辑需符合接口的响应要求；
        9.仅返回可直接运行的 Python 代码，所有说明性文字均以 Python 注释（单行 #/ 多行三引号注释）形式嵌入代码中，无任何代码外的多余文字；
        10.登录态处理：严格按照 Authorization 请求头规范，自动提取登录接口返回的 token 并添加到 Session 默认请求头，后续需登录接口自动携带；
        11.注释仅说明业务逻辑、测试思路、参数含义、断言目的，不提及 "接口文档" 相关溯源表述，保持代码的通用性和独立性。
        示例模板（必须严格对齐）：
        import pytest
        import requests
        import json
        import logging
        import time
        from requests.exceptions import RequestException, ConnectTimeout, ReadTimeout, JSONDecodeError
        
        # --------------------------
        # 🔧 全局配置与 Fixture
        # --------------------------
        # 测试环境基础配置（符合接口文档要求）
        API_BASE_URL = "https://api.xxx.com/v2"
        RESPONSE_TIMEOUT_REQUIRE = 2  # 响应时间要求（单位：秒）
        
        # 登录模块测试参数（符合接口文档格式规范）
        TEST_ACCOUNT_PHONE = "13800138000"  # 已注册手机号（11位中国大陆格式）
        TEST_ACCOUNT_EMAIL = "test_user@xxx.com"  # 已注册邮箱（备用）
        TEST_PASSWORD = "Test@123456"  # 合法密码（8-20位，含字母+数字+特殊字符）
        TEST_UNREGISTERED_ACCOUNT = "13900139000"  # 未注册手机号
        TEST_WRONG_PASSWORD = "Wrong@654321"  # 错误密码
        TEST_ILLEGAL_ACCOUNT = "12345"  # 非法格式账号（不足11位手机号）
        
        # 验证码相关测试参数
        TEST_PHONE = "13800138000"  # 已注册手机号
        TEST_VALID_CODE = "123456"  # 有效6位验证码
        TEST_INVALID_CODE = "654321"  # 无效验证码
        TEST_EXPIRED_CODE = "112233"  # 过期验证码
        
        # 商品模块测试参数
        TEST_GOODS_ID_VALID = "goods_1001"  # 有效商品ID
        TEST_GOODS_SPEC = {"color": "红色", "size": "M"}  # 合法商品规格
        TEST_GOODS_ID_OUT_OF_STOCK = "goods_9999"  # 无库存商品ID
        TEST_GOODS_ID_NON_EXISTENT = "goods_0000"  # 不存在的商品ID
        TEST_SEARCH_KEYWORD_VALID = "红色T恤"  # 有效搜索关键词
        TEST_SEARCH_KEYWORD_EMPTY = "不存在的商品123456"  # 无匹配结果关键词
        
        # 订单模块测试参数
        TEST_ADDRESS_ID_VALID = "addr_2001"  # 有效收货地址ID
        TEST_ADDRESS_ID_INVALID = "addr_9999"  # 无效收货地址ID
        TEST_PAY_TYPE_WECHAT = "wechat"  # 支持的微信支付
        TEST_PAY_TYPE_ALIPAY = "alipay"  # 支持的支付宝支付
        TEST_PAY_TYPE_UNSUPPORTED = "unionpay"  # 不支持的支付方式
        TEST_CART_ID_VALID = "cart_1001"  # 有效购物车记录ID
        
        # 微信登录相关参数
        TEST_WECHAT_AUTH_CODE = "wechat_auth_temp_code"  # 微信授权临时票据
        
        # 日志配置（标准配置，避免中文乱码）
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logger = logging.getLogger(__name__)
        
        @pytest.fixture(scope="module")
        def api_session():
            \"\"\"初始化requests.Session，管理API请求会话
            - scope=module：整个测试模块仅初始化/销毁一次会话，提升执行效率
            - 维持登录态：登录后提取token添加到Authorization头，后续接口自动携带
            - 复用TCP连接：减少请求建立连接的开销，适配高并发测试场景
            - 默认请求头：配置Content-Type=application/json，符合接口数据传输要求
            \"\"\"
            session = requests.Session()
            session.headers.update({"Content-Type": "application/json"})
            
            # 登录并设置全局token（使用手机号登录，兼容接口文档要求）
            login_url = f"{API_BASE_URL}/auth/password-login"
            login_data = {
                "account": TEST_ACCOUNT_PHONE,
                "password": TEST_PASSWORD
            }
            
            try:
                login_response = session.post(login_url, json=login_data, timeout=3)
                login_result = login_response.json()
                
                # 校验登录结果
                assert login_result.get("code") == 200, f"Fixture初始化登录失败：{login_result.get('message', '未知错误')}（错误码：{login_result.get('code')}）"
                assert "token" in login_result.get("data", {}), "登录响应未返回token，无法进行后续授权接口测试"
                
                token = login_result["data"]["token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                logger.info("✅ Fixture初始化成功：登录态已获取并设置")
                
            except (ConnectTimeout, ReadTimeout):
                pytest.fail("❌ Fixture初始化失败：登录请求超时（网络异常或服务未响应）")
            except JSONDecodeError:
                pytest.fail("❌ Fixture初始化失败：登录响应格式非法，需返回JSON数据")
            except RequestException as e:
                pytest.fail(f"❌ Fixture初始化失败：登录请求异常：{str(e)}")
            except AssertionError as ae:
                pytest.fail(f"❌ Fixture初始化失败：{str(ae)}")
            except Exception as e:
                pytest.fail(f"❌ Fixture初始化失败：未知异常：{str(e)}")
            
            yield session
            session.close()  # 测试结束后关闭会话，释放资源
        
        # --------------------------
        # 🧪 测试用例（用户登录模块）
        # --------------------------
        def test_LOG_PASSWORD_LOGIN_SUCCESS(api_session):
            \"\"\"验证账号密码登录成功（正常场景）
            业务背景：合法用户通过账号密码获取系统登录态，是核心入口功能
            测试思路：构造合法参数 → 发送请求 → 多维度校验响应
            \"\"\"
            url = f"{API_BASE_URL}/auth/password-login"
            request_data = {
                "account": TEST_ACCOUNT_PHONE,
                "password": TEST_PASSWORD
            }
            
            try:
                start_time = time.time()
                response = api_session.post(url, json=request_data, timeout=3)
                response_time = time.time() - start_time
                response_json = response.json()
                
                # 多维度断言
                assert response.status_code == 200, f"登录请求失败，状态码：{response.status_code}（预期200）"
                assert response_json.get("code") == 200, f"登录业务失败，错误码：{response_json.get('code')}（预期200）"
                assert "token" in response_json.get("data", {}), "响应缺失token，登录态生成失败"
                assert "username" in response_json.get("data", {}), "响应缺失用户名，数据返回不完整"
                assert "userId" in response_json.get("data", {}), "响应缺失用户ID，数据返回不完整"
                assert response_time <= RESPONSE_TIMEOUT_REQUIRE, f"响应超时，实际耗时：{response_time:.2f}秒（要求≤{RESPONSE_TIMEOUT_REQUIRE}秒）"
                
                print(f"✅ test_LOG_PASSWORD_LOGIN_SUCCESS：账号密码登录成功，测试通过（用户名：{response_json['data']['username']}）")
                logger.info(f"账号密码登录成功，响应耗时：{response_time:.2f}秒")
                
            except (ConnectTimeout, ReadTimeout):
                pytest.fail("❌ test_LOG_PASSWORD_LOGIN_SUCCESS：登录请求超时（网络异常或服务未响应）")
            except JSONDecodeError:
                pytest.fail("❌ test_LOG_PASSWORD_LOGIN_SUCCESS：登录响应格式非法，需返回JSON数据")
            except RequestException as e:
                pytest.fail(f"❌ test_LOG_PASSWORD_LOGIN_SUCCESS：登录请求异常：{str(e)}")
            except AssertionError as ae:
                pytest.fail(f"❌ test_LOG_PASSWORD_LOGIN_SUCCESS：断言失败：{str(ae)}")
            except Exception as e:
                pytest.fail(f"❌ test_LOG_PASSWORD_LOGIN_SUCCESS：未知异常：{str(e)}")
        
        def test_LOG_PASSWORD_LOGIN_UNREGISTERED_ACCOUNT(api_session):
            \"\"\"验证未注册账号登录失败（异常场景）
            业务背景：校验系统对非法账号的拦截能力，确保未注册用户无法登录
            \"\"\"
            url = f"{API_BASE_URL}/auth/password-login"
            request_data = {
                "account": TEST_UNREGISTERED_ACCOUNT,
                "password": TEST_PASSWORD
            }
            
            try:
                start_time = time.time()
                response = api_session.post(url, json=request_data, timeout=3)
                response_time = time.time() - start_time
                response_json = response.json()
                
                # 断言异常场景结果
                assert response.status_code == 200, f"状态码异常：{response.status_code}（预期200）"
                assert response_json.get("code") == 1001, f"错误码异常：{response_json.get('code')}（预期1001）"
                assert "账号不存在，请先注册" in response_json.get("message", ""), f"提示文案异常：{response_json.get('message')}（预期'账号不存在，请先注册'）"
                assert response_json.get("data") is None, "异常场景不应返回有效数据"
                assert response_time <= RESPONSE_TIMEOUT_REQUIRE, f"响应超时：{response_time:.2f}秒（要求≤2秒）"
                
                print("✅ test_LOG_PASSWORD_LOGIN_UNREGISTERED_ACCOUNT：未注册账号登录失败，测试通过")
                logger.info("未注册账号登录拦截成功，异常处理符合预期")
                
            except Exception as e:
                pytest.fail(f"❌ test_LOG_PASSWORD_LOGIN_UNREGISTERED_ACCOUNT：测试失败：{str(e)}")
        
        def test_LOG_GET_VERIFICATION_CODE_SUCCESS(api_session):
            \"\"\"验证获取验证码成功（正常场景）
            业务背景：用户通过手机号获取验证码，用于验证码登录
            \"\"\"
            url = f"{API_BASE_URL}/auth/get-verification-code"
            request_data = {
                "phone": TEST_PHONE
            }
            
            try:
                start_time = time.time()
                response = api_session.post(url, json=request_data, timeout=3)
                response_time = time.time() - start_time
                response_json = response.json()
                
                # 断言正常场景结果
                assert response.status_code == 200, f"状态码异常：{response.status_code}（预期200）"
                assert response_json.get("code") == 200, f"错误码异常：{response_json.get('code')}（预期200）"
                assert "countdown" in response_json.get("data", {}), "响应缺失倒计时字段"
                assert "expireTime" in response_json.get("data", {}), "响应缺失有效期字段"
                assert response_json["data"]["countdown"] == 60, f"倒计时异常：{response_json['data']['countdown']}（预期60秒）"
                assert response_json["data"]["expireTime"] == 300, f"有效期异常：{response_json['data']['expireTime']}（预期300秒）"
                assert response_time <= RESPONSE_TIMEOUT_REQUIRE, f"响应超时：{response_time:.2f}秒（要求≤2秒）"
                
                print("✅ test_LOG_GET_VERIFICATION_CODE_SUCCESS：获取验证码成功，测试通过")
                logger.info("验证码获取成功，响应参数符合要求")
                
            except Exception as e:
                pytest.fail(f"❌ test_LOG_GET_VERIFICATION_CODE_SUCCESS：测试失败：{str(e)}")
        
        # --------------------------
        # 🧪 测试用例（商品模块）
        # --------------------------
        def test_GOODS_LIST_QUERY_DEFAULT(api_session):
            \"\"\"验证商品列表默认查询成功（正常场景）
            业务背景：商品列表是用户浏览商品的核心入口，默认按销量降序展示
            \"\"\"
            url = f"{API_BASE_URL}/goods/list"
            request_params = {
                "pageNum": 1,
                "pageSize": 20,
                "sortType": "salesDesc"
            }
            
            try:
                start_time = time.time()
                response = api_session.get(url, params=request_params, timeout=3)
                response_time = time.time() - start_time
                response_json = response.json()
                
                # 断言响应有效性和完整性
                assert response.status_code == 200, f"状态码异常：{response.status_code}（预期200）"
                assert response_json.get("code") == 200, f"错误码异常：{response_json.get('code')}（预期200）"
                
                # 校验核心响应字段
                data = response_json.get("data", {})
                assert "total" in data, "响应缺失总条数字段"
                assert "pages" in data, "响应缺失总页数字段"
                assert "list" in data, "响应缺失商品列表字段"
                assert isinstance(data["list"], list), "商品列表需为数组格式"
                
                # 校验商品字段完整性（若列表非空）
                if data["list"]:
                    goods = data["list"][0]
                    required_fields = ["goodsId", "goodsName", "price", "sales", "stock", "categoryId", "categoryName", "coverImage", "specs"]
                    for field in required_fields:
                        assert field in goods, f"商品数据缺失{field}字段"
                    
                    # 校验默认排序：销量降序
                    for i in range(1, len(data["list"])):
                        prev_sales = data["list"][i-1]["sales"]
                        curr_sales = data["list"][i]["sales"]
                        assert prev_sales >= curr_sales, f"默认排序非销量降序（第{i}条销量{curr_sales} > 第{i-1}条销量{prev_sales}）"
                
                # 校验响应时间
                assert response_time <= RESPONSE_TIMEOUT_REQUIRE, f"响应超时：{response_time:.2f}秒（要求≤2秒）"
                
                print(f"✅ test_GOODS_LIST_QUERY_DEFAULT：商品列表默认查询成功，测试通过（总条数：{data['total']}）")
                logger.info(f"商品列表默认查询成功，响应耗时：{response_time:.2f}秒")
                
            except Exception as e:
                pytest.fail(f"❌ test_GOODS_LIST_QUERY_DEFAULT：测试失败：{str(e)}")
        
        def test_GOODS_SEARCH_EMPTY_RESULT(api_session):
            \"\"\"验证搜索无结果场景（异常场景）
            业务背景：用户输入无匹配的关键词，系统需给出明确提示
            \"\"\"
            url = f"{API_BASE_URL}/goods/search"
            request_params = {
                "keyword": TEST_SEARCH_KEYWORD_EMPTY,
                "pageNum": 1,
                "pageSize": 20
            }
            
            try:
                start_time = time.time()
                response = api_session.get(url, params=request_params, timeout=3)
                response_time = time.time() - start_time
                response_json = response.json()
                
                # 断言异常场景结果
                assert response.status_code == 200, f"状态码异常：{response.status_code}（预期200）"
                assert response_json.get("code") == 1103, f"错误码异常：{response_json.get('code')}（预期1103）"
                assert "未找到相关商品，请尝试其他关键词" in response_json.get("message", ""), f"提示文案异常：{response_json.get('message')}"
                assert response_json["data"]["total"] == 0, f"无结果时总条数异常：{response_json['data']['total']}（预期0）"
                assert response_time <= RESPONSE_TIMEOUT_REQUIRE, f"响应超时：{response_time:.2f}秒（要求≤2秒）"
                
                print("✅ test_GOODS_SEARCH_EMPTY_RESULT：搜索无结果场景验证成功，测试通过")
                logger.info("搜索无结果处理符合预期")
                
            except Exception as e:
                pytest.fail(f"❌ test_GOODS_SEARCH_EMPTY_RESULT：测试失败：{str(e)}")
        
        # --------------------------
        # 🧪 测试用例（购物车模块）
        # --------------------------
        def test_CART_ADD_SUCCESS(api_session):
            \"\"\"验证加入购物车成功（正常场景）
            业务背景：用户选择商品规格后加入购物车，是下单前的核心步骤
            \"\"\"
            url = f"{API_BASE_URL}/cart/add"
            request_data = {
                "goodsId": TEST_GOODS_ID_VALID,
                "spec": TEST_GOODS_SPEC,
                "quantity": 1
            }
            
            try:
                start_time = time.time()
                response = api_session.post(url, json=request_data, timeout=3)
                response_time = time.time() - start_time
                response_json = response.json()
                
                # 断言正常场景结果
                assert response.status_code == 200, f"状态码异常：{response.status_code}（预期200）"
                assert response_json.get("code") == 200, f"错误码异常：{response_json.get('code')}（预期200）"
                assert "cartCount" in response_json.get("data", {}), "响应缺失购物车数量字段"
                assert "cartId" in response_json.get("data", {}), "响应缺失购物车记录ID字段"
                assert response_json["data"]["cartCount"] >= 1, "购物车数量未增加"
                assert response_time <= RESPONSE_TIMEOUT_REQUIRE, f"响应超时：{response_time:.2f}秒（要求≤2秒）"
                
                print(f"✅ test_CART_ADD_SUCCESS：加入购物车成功，测试通过（购物车总数：{response_json['data']['cartCount']}）")
                logger.info(f"加入购物车成功，cartId：{response_json['data']['cartId']}")
                
            except Exception as e:
                pytest.fail(f"❌ test_CART_ADD_SUCCESS：测试失败：{str(e)}")

        
        ### 接口文档内容（根据此解析生成脚本）：
        {api_content}
"""

if __name__ == '__main__':
    pass
