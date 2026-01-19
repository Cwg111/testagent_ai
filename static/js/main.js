// 绑定你现有的文件选择框
const reqFile = document.getElementById('reqFile');
const uploadedFileContainer = document.querySelector('.uploaded-file-container');

// 监听文件选择（你的#reqFile）
reqFile.addEventListener('change', (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // 验证格式
    const fileExt = selectedFile.name.slice(selectedFile.name.lastIndexOf('.')).toLowerCase();
    const allowedExts = ['.txt', '.md'];
    if (!allowedExts.includes(fileExt)) {
        alert('仅支持上传.txt或.md格式的文档哦~');
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