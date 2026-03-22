import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
    VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
    
    # 确保目录存在
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    # 文档处理配置
    CHUNK_SIZE = 1000  # 文本分块大小
    CHUNK_OVERLAP = 200  # 文本块重叠大小
    
    # 嵌入模型配置
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION = 384  # 上述模型的嵌入维度
    
    # 向量数据库配置
    VECTOR_STORE_TYPE = "chroma"  # chroma 或 faiss
    COLLECTION_NAME = "knowledge_base"
    PERSIST_DIRECTORY = VECTOR_DB_DIR
    
    # 检索配置
    SEARCH_TOP_K = 15  # 增加召回数量
    SEARCH_TYPE = "similarity"  # similarity, mmr, similarity_score_threshold
    SEARCH_SCORE_THRESHOLD = 0.3  # 降低相似度阈值，提高召回率
    
    # LLM配置
    LLM_TYPE = os.getenv("LLM_TYPE", "openai")  # openai, ollama, deepseek
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE = 0.1
    OPENAI_MAX_TOKENS = 1000
    
    # Ollama配置
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # DeepSeek配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.1"))
    DEEPSEEK_MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", "1000"))
    
    # 日志配置
    LOG_LEVEL = "WARNING"  # 只显示警告和错误日志
    LOG_FILE = os.path.join(BASE_DIR, "rag_system.log")
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if cls.LLM_TYPE == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未设置，请在 .env 文件中配置")
        
        if cls.LLM_TYPE == "deepseek" and not cls.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置，请在 .env 文件中配置")
        
        if not os.path.exists(cls.DOCUMENTS_DIR):
            print(f"警告: 文档目录不存在，已创建: {cls.DOCUMENTS_DIR}")
        
        return True