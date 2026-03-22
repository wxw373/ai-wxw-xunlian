# AI知识问答助手 - 快速启动指南

## 🚀 快速启动方法

### 方法1：双击启动脚本（推荐）

1. **命令行交互模式**
   - 双击 `start_interactive.bat`
   - 在命令行窗口中输入问题
   - 输入 `exit` 或 `quit` 退出

2. **Web图形界面**
   - 双击 `start_web.bat`
   - 浏览器自动打开 http://localhost:8501
   - 或手动访问该地址

### 方法2：命令行启动

```bash
# 交互模式
.\venv\Scripts\python.exe main.py --mode interactive

# Web界面
.\venv\Scripts\python.exe -m streamlit run web_app.py

# API服务
.\venv\Scripts\python.exe web_app.py --mode api
```

## 📝 使用说明

### 交互模式命令
- 输入问题后按回车获取答案
- 输入 `exit` 或 `quit` 退出程序
- 输入 `info` 查看系统信息

### Web界面功能
- 侧边栏选择LLM类型
- 输入API密钥
- 文档搜索
- 实时问答对话

## 🔧 系统要求

- Python 3.8+
- 虚拟环境已创建（venv目录）
- 依赖包已安装
- API密钥已配置

## 📂 添加知识文档

1. 将文档放入 `data/documents/` 目录
2. 支持格式：PDF、TXT、MD、DOCX
3. 重新索引：
   ```bash
   .\venv\Scripts\python.exe main.py --mode index --force
   ```

## ⚙️ 配置文件

- `.env` - 环境变量配置（API密钥等）
- `config.py` - 系统参数配置

## 🆘 故障排除

### 启动脚本无法运行
- 确保在项目根目录
- 检查venv目录是否存在
- 右键以管理员身份运行

### 导入错误
```bash
.\venv\Scripts\pip.exe install -r requirements.txt
```

### API密钥错误
- 检查 `.env` 文件中的API密钥
- 确保密钥格式正确（通常以 sk- 开头）

## 📧 获取帮助

查看详细文档：
- `README.md` - 项目说明
- `INSTALL.md` - 安装指南