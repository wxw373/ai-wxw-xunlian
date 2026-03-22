#!/usr/bin/env python3
"""
AI知识问答助手主程序
支持文档索引、问答查询和交互模式
"""

import argparse
import sys
from rag_pipeline import RAGPipeline
from config import Config
import logging

logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def index_command(args):
    """处理索引命令"""
    print("开始文档索引...")
    
    pipeline = RAGPipeline()
    result = pipeline.index_documents(force_recreate=args.force)
    
    if result["success"]:
        print("[OK] Document indexing completed")
        print(f"  Stats: {result['stats']}")
        print(f"  Vector store info: {result['vector_store_info']}")
    else:
        print(f"[ERROR] Document indexing failed: {result['message']}")
        sys.exit(1)

def query_command(args):
    """处理查询命令"""
    print(f"处理问题: {args.question}")
    
    pipeline = RAGPipeline()
    result = pipeline.query(args.question)
    
    if result["success"]:
        print(f"\n答案: {result['answer']}")
        
        if result["source_documents"] and args.show_sources:
            print(f"\n参考来源 ({result['total_sources']} 个):")
            for source in result["source_documents"]:
                print(f"  [{source['index']}] {source['content']}")
                print(f"     来源: {source['source']} (页码: {source['page']})")
    else:
        print(f"查询失败: {result['answer']}")
        sys.exit(1)

def interactive_command(args):
    """处理交互模式命令"""
    pipeline = RAGPipeline()
    pipeline.interactive_mode()

def info_command(args):
    """显示系统信息"""
    pipeline = RAGPipeline()
    info = pipeline.get_system_info()
    
    print("="*50)
    print("AI知识问答助手 - 系统信息")
    print("="*50)
    
    print(f"\n1. 语言模型配置:")
    print(f"   • 类型: {info['llm_type']}")
    if info['llm_type'] == 'openai':
        print(f"   • 模型: {Config.OPENAI_MODEL}")
    elif info['llm_type'] == 'ollama':
        print(f"   • 模型: {Config.OLLAMA_MODEL}")
        print(f"   • 主机: {Config.OLLAMA_HOST}")
    elif info['llm_type'] == 'deepseek':
        print(f"   • 模型: {Config.DEEPSEEK_MODEL}")
        print(f"   • API地址: {Config.DEEPSEEK_BASE_URL}")
    
    print(f"\n2. 嵌入模型配置:")
    print(f"   • 模型: {info['embedding_model']}")
    print(f"   • 维度: {Config.EMBEDDING_DIMENSION}")
    
    print(f"\n3. 向量存储配置:")
    vector_info = info['vector_store']
    print(f"   • 状态: {vector_info.get('status', '未知')}")
    if vector_info.get('status') == 'loaded':
        print(f"   • 集合名称: {vector_info.get('collection_name', '未知')}")
        print(f"   • 文档数量: {vector_info.get('document_count', 0)}")
        print(f"   • 存储路径: {vector_info.get('persist_directory', '未知')}")
    
    print(f"\n4. 文档处理配置:")
    print(f"   • 分块大小: {info['chunk_size']} 字符")
    print(f"   • 分块重叠: {Config.CHUNK_OVERLAP} 字符")
    print(f"   • 检索数量: {info['search_top_k']} 个文档")
    
    print(f"\n5. 路径配置:")
    print(f"   • 文档目录: {Config.DOCUMENTS_DIR}")
    print(f"   • 向量存储: {Config.PERSIST_DIRECTORY}")
    
    print("\n" + "="*50)

def clear_command(args):
    """清除向量存储"""
    from vector_store import VectorStoreManager
    
    confirm = input("确定要清除向量存储吗？此操作不可撤销。 (y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    manager = VectorStoreManager()
    manager.clear_vector_store()
    print("向量存储已清除")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI知识问答助手 - 基于RAG技术",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --mode index                    # 索引文档
  %(prog)s --mode query --question "问题"  # 单次问答
  %(prog)s --mode interactive              # 交互模式
  %(prog)s --mode info                     # 显示系统信息
  %(prog)s --mode clear                    # 清除向量存储
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["index", "query", "interactive", "info", "clear"],
        required=True,
        help="运行模式"
    )
    
    parser.add_argument(
        "--question", "-q",
        help="查询问题（query模式使用）"
    )
    
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="强制重新创建索引（index模式使用）"
    )
    
    parser.add_argument(
        "--show-sources", "-s",
        action="store_true",
        default=True,
        help="显示答案来源（query模式使用）"
    )
    
    parser.add_argument(
        "--no-show-sources",
        action="store_false",
        dest="show_sources",
        help="不显示答案来源"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 验证参数
    if args.mode == "query" and not args.question:
        parser.error("query模式需要 --question 参数")
    
    # 执行对应命令
    try:
        Config.validate()
        
        if args.mode == "index":
            index_command(args)
        elif args.mode == "query":
            query_command(args)
        elif args.mode == "interactive":
            interactive_command(args)
        elif args.mode == "info":
            info_command(args)
        elif args.mode == "clear":
            clear_command(args)
    
    except ValueError as e:
        print(f"配置错误: {e}")
        print("请检查 .env 文件是否正确配置")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()