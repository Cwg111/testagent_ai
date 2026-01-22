// 元素绑定
const reqFile = document.getElementById('reqFile');
const uploadedFileContainer = document.querySelector('.uploaded-file-container');
const resultContainer = document.querySelector('.result-container');
const sendBtn = document.querySelector('.send-btn');
const chatInput = document.querySelector('.chat-input');
const functionType = document.querySelector('.function-type');

// 会话ID：页面刷新/新打开时重置为null
let currentSessionID = null;

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
    })
});

// 发送按钮核心逻辑（流式请求+实时显示）
async function handleSend() {
    const commandText = chatInput.value.trim();
    const selectedFile = reqFile.files[0];
    const funcType = functionType.value;

    // 基础校验
    if (!commandText){
        alert('请输入需求哦~');
        return 0;
    }

    // 拼接功能类型指令
    let fullCommand='';
    if (funcType === 'test') fullCommand=`测试岗：${commandText}，生成功能用例+web脚本`;
    else if (funcType === 'dev') fullCommand=`开发岗：${commandText}，生成接口自动化脚本`;
    else if (funcType === 'product') fullCommand=`产品岗：${commandText}，生成需求验证用例`;

    // 禁用发送按钮，防止重复点击
    sendBtn.disabled = true;
    sendBtn.textContent = '正在生成中...';

    // 创建FormData（包含文件/指令、session_id）
    const formData = new FormData();
    formData.append('command_text',fullCommand);
    if (currentSessionID) formData.append('session_id',currentSessionID)
    if (selectedFile) formData.append('file',selectedFile);

    // 清空输入框
    chatInput.value = '';

    // 创建AI回复容器（实时更新内容）
    const messageDiv=document.createElement('div');
    messageDiv.className=`message agent-message`;
    messageDiv.innerHTML=`
        <div class="message-content">
            <img src="/static/img/AI-test.png" class="message-icon" alt="AI图标">
            <div class="response-content"></div>
        </div>
    `;
    resultContainer.appendChild(messageDiv)
    const responseContent=messageDiv.querySelector('.response-content');

    try{
        // 发起流式请求
        const response=await fetch('http://localhost:8080/process-command',{
            method:'POST',
            body:formData,
        });

        if (!response.ok) throw new Error(`请求失败: ${response.status}`);

        // 处理流式响应
        const reader=response.body.getReader();
        const decoder=new TextDecoder('utf-8');
        let buffer='';
        while (true) {
            const {done,value}=await reader.read();
            if (done) break;
            // 解码并分割行（每行一个JSON）
            buffer += decoder.decode(value, { stream: true });
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

                // 区分响应类型：状态/内容/错误/最终结果
                if (chunk.status === 'success' || chunk.type === 'status') {
                    responseContent.textContent += chunk.data || '';
                } else if (chunk.type === 'final') {
                    responseContent.textContent += `\n\n✅ ${chunk.data.message}（文件路径：${chunk.data.file_path}）`;
                    document.getElementById('exportBtn').hidden = false;
                    document.getElementById('tempPath').value = chunk.data.file_path;
                } else if (chunk.status === 'error' || chunk.type === 'error') {
                    responseContent.innerHTML += `<br><span style="color: #e74c3c;">❌ ${chunk.data}</span>`;
                }
            }

            // 自动滚动到最新消息
            resultContainer.scrollTop = resultContainer.scrollHeight;
        }

    } catch (error) {
        console.error('请求错误：', error);
        responseContent.innerHTML += `<br><span style="color: #e74c3c;">❌ 处理失败：${error.message}</span>`;
    } finally {
        // 恢复发送按钮
        sendBtn.disabled = false;
        sendBtn.textContent = '发送';
        resultContainer.scrollTop = resultContainer.scrollHeight;
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
    document.getElementById('exportBtn').hidden = true;
});