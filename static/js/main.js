// 元素绑定
const reqFile = document.getElementById('reqFile');
const uploadedFileContainer = document.querySelector('.uploaded-file-container');
const chatContainer = document.querySelector('.chat-container');
const resultContainer = document.getElementById('resultContainer');
const sendBtn = document.getElementById('sendBtn');
const chatInput = document.getElementById('chatInput');
const functionType = document.getElementById('functionType');

// 会话ID：页面刷新/新打开时重置为null
let currentSessionId = null;

function scrollToBottom() {
    requestAnimationFrame(
        () => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    )
}

// 显示用户上传的文件名称到右侧聊天区
function showUploadedFileInChat(fileName) {
    const fileMsg = document.createElement('div');
    fileMsg.className = 'message user-message';
    fileMsg.innerHTML = `
        <div class="message-content">
            <span style="margin-right: 8px;">👤</span>
            上传文件：<strong>${fileName}</strong>
        </div>
    `;
    resultContainer.appendChild(fileMsg);
    scrollToBottom(); //自动滚动到底部
}

// 显示用户输入的问题
function showUserQuestionInChat(question) {
    const questionMsg = document.createElement('div');
    questionMsg.className = 'message user-message';
    questionMsg.innerHTML = `
        <div class="message-content">👤 ${question}</div>
    `;
    resultContainer.appendChild(questionMsg);
    scrollToBottom();
}

// 监听文件选择（你的#reqFile）
reqFile.addEventListener('change', (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // 验证格式
    const fileExt = selectedFile.name.slice(selectedFile.name.lastIndexOf('.')).toLowerCase();
    const allowedExts = ['.txt', '.md', '.docx', '.pdf', '.xls', '.xlsx'];
    if (!allowedExts.includes(fileExt)) {
        alert('仅支持上传.txt,.md,.docx,.pdf,.xls,.xlsx格式的文档哦~');
        reqFile.value = ''; // 清空无效选择
        return;
    }

    // 显示已上传文件名和删除按钮
    uploadedFileContainer.innerHTML = `
    <div class="uploaded-file-wrapper">
      ${selectedFile.name}
      <span class="delete-file-btn">×</span>
    </div>
  `;
    // 绑定删除按钮的点击事件
    document.querySelector('.delete-file-btn').addEventListener('click', () => {
        reqFile.value = ''; // 清空文件选择框
        uploadedFileContainer.innerHTML = '';
        // 删除右侧聊天区对应的文件信息
        const fileMsg = resultContainer.querySelectorAll('.user-message');
        fileMsg.forEach(msg => {
            if (msg.innerHTML.includes('上传文件：')) msg.remove();
        });
    });
    // 显示上传的文件名
    showUploadedFileInChat(selectedFile.name);
});

// 渲染测试用例表格的函数
function renderTestCaseTable(tableData) {
    if (!tableData || tableData.length === 0) return '';

    // 1. 构建表头（和table_data的字段对应）
    const thead = `
        <thead>
            <tr>
                <th>功能模块</th>
                <th>模块描述</th>
                <th>用例ID</th>
                <th>用例标题</th>
                <th>前置条件</th>
                <th>测试步骤</th>
                <th>预期结果</th>
            </tr>
        </thead>
    `;

    // 2. 构建表体（遍历tableData）
    let tbody = '<tbody>';
    tableData.forEach(row => {
        // 步骤字段处理：拆分、加序号、末尾加；
        const rawSteps = escapeHtml(row.steps || '');
        // 按逗号分割步骤，过滤空步骤（避免连续逗号导致的空项）
        const stepArray = rawSteps.split(',').filter(step => step.trim() !== '');
        // 给每个步骤加序号+末尾；，再用<br>换行拼接
        const numberedSteps = stepArray
            .map((step, index) => `${index + 1}. ${step.trim()}；`)
            .join('<br>');
        tbody += `
            <tr>
                <td>${escapeHtml(row.feature || '')}</td>
                <td>${escapeHtml(row.module_desc || '')}</td>
                <td>${escapeHtml(row.case_id || '')}</td>
                <td>${escapeHtml(row.title || '')}</td>
                <td>${escapeHtml(row.precondition || '')}</td>
                <td>${numberedSteps}</td>
                <td>${escapeHtml(row.expected || '')}</td>
            </tr>
        `;
    });
    tbody += '</tbody>';

    // 3. 完整表格HTML（带样式类名，后续加CSS）
    return `
        <div class="case-table-container" >
            <table class="case-table">${thead}${tbody}</table>
        </div>
    `;
}

function renderChecklistTable(tableData) {
    if (!tableData || tableData.length === 0) return '';

    // 1. 构建表头（和table_data的字段对应）
    const thead = `
        <thead>
            <tr>
                <th>检查类别</th>
                <th>类别描述</th>
                <th>检查事项步骤</th>
                <th>对应需求点编号</th>
                <th>检查标准</th>
                <th>是否通过</th>
            </tr>
        </thead>
    `;

    // 2. 构建表体（遍历tableData）
    let tbody = '<tbody>';
    tableData.forEach(row => {
        // 步骤字段处理：拆分、加序号、末尾加；
        const rawItems = escapeHtml(row.check_item || '');
        // 按逗号分割步骤，过滤空步骤（避免连续逗号导致的空项）
        const itemArray = rawItems.split(',').filter(item => item.trim() !== '');
        // 给每个步骤加序号+末尾；，再用<br>换行拼接
        const numberedItems = itemArray
            .map((item, index) => `${index + 1}. ${item.trim()}；`)
            .join('<br>');
        tbody += `
            <tr>
                <td>${escapeHtml(row.check_modules || '')}</td>
                <td>${escapeHtml(row.module_desc || '')}</td>
                <td>${numberedItems}</td>
                <td>${escapeHtml(row.corresponding_requirement || '')}</td>
                <td>${escapeHtml(row.check_standard || '')}</td>
                <td>${escapeHtml(row.is_passed || '')}</td>
            </tr>
        `;
    });
    tbody += '</tbody>';

    // 3. 完整表格HTML（带样式类名，后续加CSS）
    return `
        <div class="checklist-table-container" >
            <table class="checklist-table">${thead}${tbody}</table>
        </div>
    `;
}

// HTML转义工具函数
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// 发送按钮核心逻辑（流式请求+实时显示）
async function handleSend() {
    const commandText = chatInput.value.trim();
    const selectedFile = reqFile.files[0];
    const funcType = functionType.value;

    // 基础校验
    if (!commandText) {
        alert('请输入需求哦~');
        return 0;
    }

    // 把用户在前端输入的指令原原本本的传给后端
    let fullCommand = commandText;


    // 禁用发送按钮，防止重复点击
    sendBtn.disabled = true;
    sendBtn.textContent = '正在生成中...';

    // 创建FormData（包含文件/指令、session_id）
    const formData = new FormData();
    formData.append('command_text', fullCommand);
    if (currentSessionId) formData.append('session_id', currentSessionId)
    if (selectedFile) formData.append('file', selectedFile);

    // 清空输入框
    chatInput.value = '';

    // 显示用户输入的问题
    showUserQuestionInChat(commandText);

    // 创建AI回复容器（实时更新内容）
    const messageDiv = document.createElement('div');
    messageDiv.className = `message agent-message`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <img src="/static/img/AI-test.png" class="message-icon" alt="AI图标">
            <div class="response-content"></div>
            <button class="export-btn" onclick="exportContent()" style="display: none;">导出</button>
        </div>
    `;
    resultContainer.appendChild(messageDiv)
    const responseContent = messageDiv.querySelector('.response-content');
    // 缓存当前AI消息的导出按钮
    const currentExportBtn = messageDiv.querySelector('.export-btn');

    try {
        // 发起流式请求
        const response = await fetch('http://127.0.0.1:8000/process-command', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error(`请求失败: ${response.status}`);

        // 处理流式响应
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            // 解码并分割行（每行一个JSON）
            buffer += decoder.decode(value, {stream: true});
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // 保留未完成的最后一行

            // 逐行解析JSON并更新页面
            for (const line of lines) {
                if (!line.trim()) continue;
                const chunk = JSON.parse(line);

                // 重置session_id（首次返回时捕获）
                if (chunk.session_id && !currentSessionId) {
                    currentSessionId = chunk.session_id;
                }

                if (chunk.type === "json_chunk") {
                    continue;
                }

                if (chunk.type === "status") {
                    // 补防御：chunk.data为null/undefined时置空
                    // 核心判断：仅当data存在且包含...时，才添加加载动画优化
                    if (chunk.data && chunk.data.includes('...')) {
                        // 仅渲染一次，避免重复
                        // const existingTip = responseContent.querySelector('#loading-tip-with-dot');
                        // if (!existingTip) {
                        // 关键：把文字单独放在span#loading-text里，样式/动画单独分离
                        responseContent.innerHTML += `
                             <div class="status-with-dot" id="loading-tip-with-dot">
                                    <span class="simple-loading-spinner"></span>
                                    <span id="loading-text">${chunk.data}</span>
                             </div>
                            `;
                        // }
                    } else {
                        // 不含...的status，按原有逻辑处理
                        responseContent.innerHTML += chunk.data || '';
                    }
                    responseContent.innerHTML += '<br><div class="response-divider"></div>';
                } else if (chunk.type === "error") {
                    const loadingTip = responseContent.querySelector('#loading-tip-with-dot');
                    const loadingText = responseContent.querySelector('#loading-text');
                    if (loadingTip && loadingText) {
                        // 核心：只保留文字，清除所有样式/动画
                        loadingTip.outerHTML = loadingText.textContent; // 替换为纯文字，清除所有样式
                    }
                    // 补防御
                    responseContent.innerHTML += `<span style="color: #9b59b6; font-weight: 500; display: inline-block; 
                         padding: 4px 8px; border-radius: 4px;
                         background: #f8f0ff;">🤔 ${chunk.data || ''}</span>`;
                    responseContent.innerHTML += '<br><div class="response-divider"></div>';
                } else if (chunk.type === "success") {
                    const loadingTip = responseContent.querySelector('#loading-tip-with-dot');
                    const loadingText = responseContent.querySelector('#loading-text');
                    if (loadingTip && loadingText) {
                        // 核心：只保留文字，清除所有样式/动画
                        loadingTip.outerHTML = loadingText.textContent; // 替换为纯文字，清除所有样式
                    }
                    // 补防御：先处理null/undefined，再转义
                    const safeData = chunk.data || '';
                    const escapedData = escapeHtml(safeData);
                    responseContent.innerHTML += escapedData.replace(/\n/g, '<br>');
                } else if (chunk.type === "final") {
                    const loadingTip = responseContent.querySelector('#loading-tip-with-dot');
                    const loadingText = responseContent.querySelector('#loading-text');
                    if (loadingTip && loadingText) {
                        // 核心：只保留文字，清除所有样式/动画
                        loadingTip.outerHTML = loadingText.textContent; // 替换为纯文字，清除所有样式
                    }
                    // 补防御
                    responseContent.innerHTML += `<br>✅ ${chunk.data?.message || ''}<br>`;
                    document.getElementById('tempPath').value = chunk.data?.file_path || '';
                    currentExportBtn.style.display = 'block';

                    // 如果final数据里有case_table_data，渲染测试用例表格
                    if (chunk.data?.case_table_data) {
                        const tableHtml = renderTestCaseTable(chunk.data.case_table_data);
                        responseContent.innerHTML += tableHtml;
                    }

                    // 如果final数据里有checklist_table_data，渲染检查清单表格
                    if (chunk.data?.checklist_table_data) {
                        const tableHtml = renderChecklistTable(chunk.data.checklist_table_data);
                        responseContent.innerHTML += tableHtml;
                    }
                }
            }

            // 自动滚动到最新消息
            scrollToBottom();
        }

    } catch (error) {
        console.error('请求错误：', error);
        responseContent.innerHTML += `<br><span style="color: #e74c3c;">❌ 处理失败：${error.message}</span>`;
    } finally {
        // 恢复发送按钮
        sendBtn.disabled = false;
        sendBtn.textContent = '发送';
        scrollToBottom();
    }

}

// 5. 导出功能（配合后端/export接口）
function exportContent() {
    const tempPath = document.getElementById('tempPath').value;
    if (!tempPath) {
        alert('暂无可导出的内容！');
        return;
    }
    // 发起导出请求
    window.open(`http://localhost:8000/export?file_path=${encodeURIComponent(tempPath)}`);
}

// 6. 页面加载时重置session_id（核心：刷新/新打开页面生效）
window.addEventListener('load', () => {
    currentSessionId = null;
    resultContainer.innerHTML = ''; // 清空历史结果
});