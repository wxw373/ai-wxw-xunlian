# AI知识问答助手 - 安装和使用指南

## 系统要求

- Python 3.8 或更高版本
- 至少 4GB 内存
- 10GB 可用磁盘空间（用于模型和向量存储）
- 网络连接（用于下载模型和API调用）

## 安装步骤

### 1. 克隆或下载项目

```bash
# 克隆项目（如果你使用Git）
git clone <项目地址>
cd ai-project

# 或者直接使用当前目录
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置环境变量

复制环境变量示例文件并配置：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，设置你的API密钥
```

编辑 `.env` 文件，根据你的需求配置：

```env
# 使用OpenAI（需要API密钥）
OPENAI_API_KEY=your_openai_api_key_here

# 或者使用Ollama（本地运行）
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 5. 准备知识文档

将你的文档放入 `data/documents/` 目录，支持格式：
- PDF (.pdf)
- 文本 (.txt)
- Markdown (.md)
- Word文档 (.docx)

系统已包含一个示例文档 `knowledge_base.md`。

## 快速开始

### 方法1：命令行界面

#### 文档索引
```bash
# 构建向量索引
python main.py --mode index

# 强制重新构建索引
python main.py --mode index --force
```

#### 问答查询
```bash
# 单次问答
python main.py --mode query --question "什么是人工智能？"

# 交互式问答
python main.py --mode interactive
```

#### 系统信息
```bash
# 显示系统信息
python main.py --mode info

# 清除向量存储
python main.py --mode clear
```

### 方法2：Web API接口

```bash
# 启动FastAPI服务器
python web_app.py --mode api

# 指定主机和端口
python web_app.py --mode api --host 0.0.0.0 --port 8000
```

启动后访问：
- API文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

### 方法3：Web图形界面

```bash
# 启动Streamlit界面
python web_app.py --mode web
```

启动后访问：http://localhost:8501

## 配置说明

### 主要配置文件：`config.py`

可以调整以下参数：

```python
# 文档处理
CHUNK_SIZE = 1000      # 文本分块大小
CHUNK_OVERLAP = 200    # 文本块重叠大小

# 嵌入模型
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# 向量数据库
VECTOR_STORE_TYPE = "chroma"
COLLECTION_NAME = "knowledge_base"

# 检索配置
SEARCH_TOP_K = 5       # 检索返回的文档数量

# LLM配置
LLM_TYPE = "openai"    # openai, ollama 或 deepseek
```

### 环境变量：`.env`

- `OPENAI_API_KEY`: OpenAI API密钥
- `OLLAMA_HOST`: Ollama服务地址（默认 http://localhost:11434）
- `OLLAMA_MODEL`: Ollama模型名称（默认 llama2）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DEEPSEEK_BASE_URL`: DeepSeek API地址（默认 https://api.deepseek.com）
- `DEEPSEEK_MODEL`: DeepSeek模型名称（默认 deepseek-chat）
- `DEEPSEEK_TEMPERATURE`: 温度参数（默认 0.1）
- `DEEPSEEK_MAX_TOKENS`: 最大token数（默认 1000）

## 测试系统

运行完整测试：

```bash
python test_rag.py
```

测试包括：
1. 文档加载测试
2. 向量存储测试
3. RAG管道测试
4. 文档索引测试
5. 查询功能测试

## 使用示例

### 示例1：构建企业知识库

1. 将公司文档（手册、流程、政策）放入 `data/documents/`
2. 运行索引：`python main.py --mode index`
3. 启动Web界面：`python web_app.py --mode web`
4. 员工可以通过Web界面查询公司知识

### 示例2：研究助手

1. 将研究论文、报告放入文档目录
2. 使用命令行交互模式：`python main.py --mode interactive`
3. 提问研究相关问题，系统会基于文档提供答案

### 示例3：教育工具

1. 将教材、讲义放入文档目录
2. 启动API服务：`python web_app.py --mode api`
3. 开发教育应用调用API接口

## 故障排除

### 常见问题

1. **导入错误：No module named 'xxx'**
   - 解决方案：运行 `pip install -r requirements.txt`

2. **OpenAI API密钥错误**
   - 解决方案：检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确

3. **文档加载失败**
   - 解决方案：确保文档在 `data/documents/` 目录中，且格式受支持

4. **内存不足**
   - 解决方案：减少 `CHUNK_SIZE` 或使用更小的嵌入模型

5. **向量存储损坏**
   - 解决方案：运行 `python main.py --mode clear` 清除后重新索引

### 性能优化建议

1. **大型文档集**：增加 `CHUNK_SIZE` 减少分块数量
2. **快速检索**：使用 `SEARCH_TOP_K = 3` 减少检索数量
3. **本地运行**：使用Ollama避免API调用延迟
4. **GPU加速**：安装CUDA版本的PyTorch加速嵌入计算

## 扩展开发

### 添加新文档格式

编辑 `document_loader.py` 中的 `supported_extensions` 字典，添加新的加载器。

### 使用其他向量数据库

修改 `vector_store.py` 中的 `VectorStoreManager` 类，支持FAISS、Pinecone等其他向量数据库。

### 集成其他LLM

在 `rag_pipeline.py` 的 `_create_llm` 方法中添加新的LLM支持。

## 许可证

本项目基于MIT许可证开源。

## 获取帮助

如有问题，请：
1. 查看日志文件：`rag_system.log`
2. 运行测试脚本：`python test_rag.py`
3. 检查配置文件和环境变量