import os
from typing import List, Optional
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import Config
import logging

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class DocumentLoader:
    """文档加载和预处理类"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
    
    def load_documents(self, directory: Optional[str] = None) -> List[Document]:
        """从目录加载所有文档"""
        if directory is None:
            directory = Config.DOCUMENTS_DIR
        
        if not os.path.exists(directory):
            logger.error(f"文档目录不存在: {directory}")
            return []
        
        documents = []
        supported_extensions = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.md': UnstructuredMarkdownLoader,
            '.docx': Docx2txtLoader,
        }
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue
            
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                try:
                    logger.info(f"加载文档: {filename}")
                    loader_class = supported_extensions[ext]
                    loader = loader_class(filepath)
                    docs = loader.load()
                    documents.extend(docs)
                    logger.info(f"成功加载 {len(docs)} 个文档块来自 {filename}")
                except Exception as e:
                    logger.error(f"加载文档 {filename} 时出错: {e}")
            else:
                logger.warning(f"不支持的文件格式: {filename}")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档为更小的块"""
        if not documents:
            return []
        
        logger.info(f"开始分割 {len(documents)} 个文档")
        split_docs = self.text_splitter.split_documents(documents)
        logger.info(f"分割完成，共 {len(split_docs)} 个文本块")
        
        # 添加元数据
        for i, doc in enumerate(split_docs):
            if not doc.metadata:
                doc.metadata = {}
            doc.metadata["chunk_id"] = i
        
        return split_docs
    
    def load_and_split(self, directory: Optional[str] = None) -> List[Document]:
        """加载并分割文档"""
        documents = self.load_documents(directory)
        if not documents:
            logger.warning("未找到任何文档")
            return []
        
        split_docs = self.split_documents(documents)
        return split_docs
    
    def get_document_stats(self, documents: List[Document]) -> dict:
        """获取文档统计信息"""
        if not documents:
            return {"total_documents": 0, "total_chunks": 0, "avg_chunk_length": 0}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_length = total_chars / len(documents) if documents else 0
        
        return {
            "total_documents": len(documents),
            "total_chunks": len(documents),
            "avg_chunk_length": avg_length,
            "total_characters": total_chars
        }


if __name__ == "__main__":
    # 测试文档加载
    loader = DocumentLoader()
    docs = loader.load_and_split()
    
    if docs:
        stats = loader.get_document_stats(docs)
        print(f"文档统计: {stats}")
        
        # 显示前3个文本块
        for i, doc in enumerate(docs[:3]):
            print(f"\n--- 文本块 {i+1} ---")
            print(f"内容预览: {doc.page_content[:200]}...")
            print(f"元数据: {doc.metadata}")
    else:
        print("未找到文档，请将文档放入 data/documents/ 目录")