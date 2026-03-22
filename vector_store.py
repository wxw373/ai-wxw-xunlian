import os
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore
from huggingface_hub import snapshot_download
from config import Config
import logging

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# 关闭第三方库的INFO日志
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

class VectorStoreManager:
    """向量存储管理类"""
    
    def __init__(self):
        self.embeddings = self._create_embeddings()
        self.vector_store = None
    
    def _create_embeddings(self):
        """创建嵌入模型"""
        logger.info(f"加载嵌入模型: {Config.EMBEDDING_MODEL}")

        model_name = Config.EMBEDDING_MODEL
        local_files_only = os.getenv("HF_HUB_OFFLINE") == "1" or os.getenv("TRANSFORMERS_OFFLINE") == "1"
        try:
            model_name = snapshot_download(model_name, local_files_only=local_files_only)
            logger.info(f"使用本地缓存模型: {model_name}")
        except Exception as e:
            if local_files_only:
                raise RuntimeError(
                    "未找到本地嵌入模型缓存。请取消 HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE 后重新运行，"
                    "或先手动下载 sentence-transformers 模型。"
                ) from e
            logger.warning(f"未找到本地缓存模型，将尝试在线加载: {e}")
        
        # 使用 HuggingFace 嵌入模型
        model_kwargs = {'device': 'cpu', 'local_files_only': local_files_only}  # 可以使用 'cuda' 如果 GPU 可用
        encode_kwargs = {'normalize_embeddings': True}
        
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        logger.info("嵌入模型加载完成")
        return embeddings
    
    def create_vector_store(self, documents: List[Document], force_recreate: bool = False) -> VectorStore:
        """创建向量存储"""
        if os.path.exists(Config.PERSIST_DIRECTORY) and not force_recreate:
            logger.info(f"加载现有向量存储从: {Config.PERSIST_DIRECTORY}")
            try:
                self.vector_store = Chroma(
                    persist_directory=Config.PERSIST_DIRECTORY,
                    embedding_function=self.embeddings,
                    collection_name=Config.COLLECTION_NAME
                )
                logger.info("向量存储加载成功")
                return self.vector_store
            except Exception as e:
                logger.warning(f"加载现有向量存储失败: {e}, 重新创建")
        
        logger.info("创建新的向量存储")
        
        if not documents:
            raise ValueError("没有文档可用于创建向量存储")
        
        logger.info(f"开始创建向量索引，文档数量: {len(documents)}")
        
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=Config.PERSIST_DIRECTORY,
            collection_name=Config.COLLECTION_NAME
        )
        
        # Chroma 新版本自动持久化，无需手动调用 persist()
        logger.info(f"向量存储创建完成，已保存到: {Config.PERSIST_DIRECTORY}")
        
        return self.vector_store
    
    def load_vector_store(self) -> Optional[VectorStore]:
        """加载现有的向量存储"""
        if not os.path.exists(Config.PERSIST_DIRECTORY):
            logger.warning(f"向量存储目录不存在: {Config.PERSIST_DIRECTORY}")
            return None
        
        try:
            self.vector_store = Chroma(
                persist_directory=Config.PERSIST_DIRECTORY,
                embedding_function=self.embeddings,
                collection_name=Config.COLLECTION_NAME
            )
            logger.info("向量存储加载成功")
            return self.vector_store
        except Exception as e:
            logger.error(f"加载向量存储失败: {e}")
            return None
    
    def search_similar(self, query: str, k: Optional[int] = None) -> List[Document]:
        """搜索相似文档"""
        if self.vector_store is None:
            self.vector_store = self.load_vector_store()
        
        if self.vector_store is None:
            logger.error("向量存储未初始化")
            return []
        
        if k is None:
            k = Config.SEARCH_TOP_K
        
        logger.info(f"搜索查询: '{query}' (top_k={k}, threshold={Config.SEARCH_SCORE_THRESHOLD})")
        
        try:
            # 先获取带分数的结果
            scored_results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # 过滤掉低于阈值的结果
            filtered_results = []
            for doc, score in scored_results:
                if score >= Config.SEARCH_SCORE_THRESHOLD:
                    filtered_results.append(doc)
                    logger.debug(f"文档分数: {score:.3f} (保留)")
                else:
                    logger.debug(f"文档分数: {score:.3f} (过滤)")
            
            logger.info(f"找到 {len(filtered_results)} 个相关文档 (过滤后)")
            return filtered_results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def search_with_scores(self, query: str, k: Optional[int] = None) -> List[tuple]:
        """搜索相似文档并返回分数"""
        if self.vector_store is None:
            self.vector_store = self.load_vector_store()
        
        if self.vector_store is None:
            logger.error("向量存储未初始化")
            return []
        
        if k is None:
            k = Config.SEARCH_TOP_K
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"找到 {len(results)} 个相关文档")
            return results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """获取集合信息"""
        if self.vector_store is None:
            self.vector_store = self.load_vector_store()
        
        if self.vector_store is None:
            return {"status": "not_initialized"}
        
        try:
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "status": "loaded",
                "collection_name": Config.COLLECTION_NAME,
                "document_count": count,
                "embedding_dimension": Config.EMBEDDING_DIMENSION,
                "persist_directory": Config.PERSIST_DIRECTORY
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def clear_vector_store(self):
        """清空向量存储"""
        if os.path.exists(Config.PERSIST_DIRECTORY):
            import shutil
            try:
                shutil.rmtree(Config.PERSIST_DIRECTORY)
                logger.info(f"向量存储已清空: {Config.PERSIST_DIRECTORY}")
                self.vector_store = None
            except Exception as e:
                logger.error(f"清空向量存储失败: {e}")
        else:
            logger.info("向量存储目录不存在，无需清空")


if __name__ == "__main__":
    # 测试向量存储
    manager = VectorStoreManager()
    
    # 显示嵌入模型信息
    print("嵌入模型信息:")
    print(f"模型: {Config.EMBEDDING_MODEL}")
    print(f"维度: {Config.EMBEDDING_DIMENSION}")
    
    # 获取向量存储信息
    info = manager.get_collection_info()
    print(f"\n向量存储信息: {info}")
    
    # 测试搜索（如果有向量存储）
    if info.get("status") == "loaded":
        test_query = "人工智能"
        results = manager.search_similar(test_query, k=3)
        
        print(f"\n测试搜索: '{test_query}'")
        for i, doc in enumerate(results):
            print(f"\n--- 结果 {i+1} ---")
            print(f"内容: {doc.page_content[:150]}...")
            print(f"来源: {doc.metadata.get('source', '未知')}")
    else:
        print("\n向量存储未初始化，请先运行文档索引")
