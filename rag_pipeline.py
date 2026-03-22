from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from config import Config
from document_loader import DocumentLoader
from vector_store import VectorStoreManager
import logging

# 设置日志级别
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# 关闭第三方库的INFO日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)
logging.getLogger("langchain_core").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

class RAGPipeline:
    """RAG管道类"""
    
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.vector_store_manager = VectorStoreManager()
        self.llm = self._create_llm()
        self.qa_chain = None
    
    def _create_llm(self):
        """创建语言模型"""
        logger.info(f"创建语言模型，类型: {Config.LLM_TYPE}")
        
        if Config.LLM_TYPE == "openai":
            from langchain_openai import ChatOpenAI
            
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API密钥未设置，请在.env文件中配置OPENAI_API_KEY")
            
            llm = ChatOpenAI(
                model_name=Config.OPENAI_MODEL,
                temperature=Config.OPENAI_TEMPERATURE,
                max_tokens=Config.OPENAI_MAX_TOKENS,
                openai_api_key=Config.OPENAI_API_KEY
            )
            logger.info(f"OpenAI模型加载完成: {Config.OPENAI_MODEL}")
        
        elif Config.LLM_TYPE == "ollama":
            from langchain_community.llms import Ollama
            
            llm = Ollama(
                base_url=Config.OLLAMA_HOST,
                model=Config.OLLAMA_MODEL
            )
            logger.info(f"Ollama模型加载完成: {Config.OLLAMA_MODEL}")
        
        elif Config.LLM_TYPE == "deepseek":
            from langchain_openai import ChatOpenAI
            
            if not Config.DEEPSEEK_API_KEY:
                raise ValueError("DeepSeek API密钥未设置，请在.env文件中配置DEEPSEEK_API_KEY")
            
            llm = ChatOpenAI(
                model_name=Config.DEEPSEEK_MODEL,
                temperature=Config.DEEPSEEK_TEMPERATURE,
                max_tokens=Config.DEEPSEEK_MAX_TOKENS,
                openai_api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
            logger.info(f"DeepSeek模型加载完成: {Config.DEEPSEEK_MODEL}")
        
        else:
            raise ValueError(f"不支持的LLM类型: {Config.LLM_TYPE}")
        
        return llm
    
    def _create_prompt_template(self):
        """创建提示模板（知识库模式）"""
        template = """基于以下上下文信息，请回答用户的问题。

上下文信息:
{context}

问题: {question}

请用中文提供详细、准确的答案:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _create_general_prompt_template(self):
        """创建通用知识提示模板"""
        template = """请回答用户的问题。如果问题涉及专业知识，请明确说明这是基于通用知识的回答。

问题: {question}

请用中文提供详细、准确的答案:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["question"]
        )
    
    def index_documents(self, force_recreate: bool = False) -> Dict[str, Any]:
        """索引文档"""
        logger.info("开始文档索引流程")
        
        # 加载和分割文档
        documents = self.document_loader.load_and_split()
        if not documents:
            return {"success": False, "message": "未找到文档"}
        
        stats = self.document_loader.get_document_stats(documents)
        logger.info(f"文档统计: {stats}")
        
        # 创建向量存储
        try:
            vector_store = self.vector_store_manager.create_vector_store(
                documents, force_recreate=force_recreate
            )
            
            # 创建QA链
            prompt = self._create_prompt_template()
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(
                    search_kwargs={"k": Config.SEARCH_TOP_K}
                ),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
            logger.info("文档索引完成")
            return {
                "success": True,
                "message": "文档索引完成",
                "stats": stats,
                "vector_store_info": self.vector_store_manager.get_collection_info()
            }
        
        except Exception as e:
            logger.error(f"文档索引失败: {e}")
            return {"success": False, "message": f"文档索引失败: {str(e)}"}
    
    def query(self, question: str) -> Dict[str, Any]:
        """查询问题（混合模式）"""
        logger.info(f"处理问题: {question}")
        
        try:
            # 第一步：尝试从知识库检索
            source_documents = []
            knowledge_base_answer = None
            
            # 加载向量存储
            if self.qa_chain is None:
                vector_store = self.vector_store_manager.load_vector_store()
                if vector_store is not None:
                    prompt = self._create_prompt_template()
                    self.qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        chain_type="stuff",
                        retriever=vector_store.as_retriever(
                            search_kwargs={"k": Config.SEARCH_TOP_K}
                        ),
                        chain_type_kwargs={"prompt": prompt},
                        return_source_documents=True
                    )
            
            # 如果有向量存储，尝试从知识库回答
            if self.qa_chain is not None:
                result = self.qa_chain.invoke({"query": question})
                knowledge_base_answer = result.get("result", "")
                source_documents = result.get("source_documents", [])
                
                # 检查是否有相关的知识库内容
                # 只要检索到文档，就使用知识库的答案
                has_relevant_content = (
                    source_documents and 
                    len(source_documents) > 0
                )
                
                if has_relevant_content:
                    # 格式化源文档信息
                    formatted_sources = []
                    for i, doc in enumerate(source_documents):
                        formatted_sources.append({
                            "index": i + 1,
                            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                            "source": doc.metadata.get("source", "未知"),
                            "page": doc.metadata.get("page", "未知")
                        })
                    
                    logger.info(f"从知识库找到答案，来源文档数: {len(formatted_sources)}")
                    
                    return {
                        "success": True,
                        "question": question,
                        "answer": knowledge_base_answer,
                        "source_documents": formatted_sources,
                        "total_sources": len(formatted_sources),
                        "answer_type": "knowledge_base"
                    }
            
            # 第二步：如果知识库中没有相关内容，使用LLM通用知识
            logger.info("知识库中未找到相关内容，使用LLM通用知识回答")
            
            general_prompt = self._create_general_prompt_template()
            general_chain = general_prompt | self.llm
            general_answer = general_chain.invoke({"question": question})
            
            answer_text = general_answer.content if hasattr(general_answer, 'content') else str(general_answer)
            
            logger.info(f"使用通用知识回答完成，答案长度: {len(answer_text)}")
            
            return {
                "success": True,
                "question": question,
                "answer": answer_text,
                "source_documents": [],
                "total_sources": 0,
                "answer_type": "general_knowledge"
            }
        
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return {
                "success": False,
                "question": question,
                "answer": f"查询失败: {str(e)}",
                "source_documents": [],
                "total_sources": 0,
                "answer_type": "error"
            }
    
    def search_similar_documents(self, query: str, k: Optional[int] = None) -> List[Document]:
        """搜索相似文档（不生成答案）"""
        return self.vector_store_manager.search_similar(query, k)
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        vector_store_info = self.vector_store_manager.get_collection_info()
        
        return {
            "llm_type": Config.LLM_TYPE,
            "embedding_model": Config.EMBEDDING_MODEL,
            "vector_store": vector_store_info,
            "chunk_size": Config.CHUNK_SIZE,
            "search_top_k": Config.SEARCH_TOP_K
        }
    
    def interactive_mode(self):
        """交互式模式"""
        print("\n" + "="*50)
        print("AI知识问答助手 - 交互模式")
        print("输入 '退出' 或 'exit' 结束")
        print("输入 '信息' 或 'info' 查看系统信息")
        print("="*50)
        
        # 确保系统已初始化
        if self.qa_chain is None:
            print("\n正在初始化系统...")
            result = self.index_documents()
            if not result["success"]:
                print(f"初始化失败: {result['message']}")
                return
        
        while True:
            try:
                question = input("\n请输入问题: ").strip()
                
                if question.lower() in ["退出", "exit", "quit", "q"]:
                    print("再见！")
                    break
                
                if question.lower() in ["信息", "info", "system"]:
                    info = self.get_system_info()
                    print(f"\n系统信息:")
                    print(f"LLM类型: {info['llm_type']}")
                    print(f"嵌入模型: {info['embedding_model']}")
                    print(f"向量存储状态: {info['vector_store'].get('status', '未知')}")
                    if info['vector_store'].get('status') == 'loaded':
                        print(f"文档数量: {info['vector_store'].get('document_count', 0)}")
                    continue
                
                if not question:
                    continue
                
                result = self.query(question)
                
                if result["success"]:
                    # 显示答案来源类型
                    answer_type = result.get("answer_type", "unknown")
                    if answer_type == "knowledge_base":
                        print(f"\n答案 (来自知识库):")
                    elif answer_type == "general_knowledge":
                        print(f"\n答案 (来自通用知识):")
                    else:
                        print(f"\n答案:")
                    
                    print(f"{result['answer']}")
                else:
                    print(f"\n错误: {result['answer']}")
            
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"\n处理问题时出错: {e}")


if __name__ == "__main__":
    # 测试RAG管道
    pipeline = RAGPipeline()
    
    print("RAG系统测试")
    print("1. 测试文档索引")
    print("2. 测试问答")
    print("3. 进入交互模式")
    print("4. 显示系统信息")
    
    choice = input("\n请选择测试项目 (1-4): ").strip()
    
    if choice == "1":
        result = pipeline.index_documents(force_recreate=True)
        print(f"\n索引结果: {result}")
    
    elif choice == "2":
        test_question = "什么是人工智能？"
        print(f"\n测试问题: {test_question}")
        result = pipeline.query(test_question)
        
        if result["success"]:
            print(f"\n答案: {result['answer']}")
            if result["source_documents"]:
                print(f"\n参考来源:")
                for source in result["source_documents"]:
                    print(f"  [{source['index']}] {source['content']}")
        else:
            print(f"\n错误: {result['answer']}")
    
    elif choice == "3":
        pipeline.interactive_mode()
    
    elif choice == "4":
        info = pipeline.get_system_info()
        print(f"\n系统信息: {info}")
    
    else:
        print("无效选择")