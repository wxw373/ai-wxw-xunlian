#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试脚本"""
import sys
import os

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*60)
print("开始测试AI知识问答助手...")
print("="*60)

# 测试1: 导入模块
print("\n测试1: 导入模块...")
try:
    from config import Config
    print("[OK] config导入成功")
    
    from document_loader import DocumentLoader
    print("[OK] document_loader导入成功")
    
    from vector_store import VectorStoreManager
    print("[OK] vector_store导入成功")
    
    from rag_pipeline import RAGPipeline
    print("[OK] rag_pipeline导入成功")
except Exception as e:
    print(f"[ERROR] 导入失败: {e}")
    sys.exit(1)

# 测试2: 检查配置
print("\n测试2: 检查配置...")
try:
    Config.validate()
    print(f"[OK] 配置验证通过")
    print(f"  LLM类型: {Config.LLM_TYPE}")
    print(f"  文档目录: {Config.DOCUMENTS_DIR}")
    print(f"  向量存储目录: {Config.VECTOR_DB_DIR}")
except Exception as e:
    print(f"[ERROR] 配置验证失败: {e}")
    sys.exit(1)

# 测试3: 加载文档
print("\n测试3: 加载文档...")
try:
    loader = DocumentLoader()
    documents = loader.load_and_split()
    
    if documents:
        stats = loader.get_document_stats(documents)
        print(f"[OK] 文档加载成功")
        print(f"  文档数量: {stats['total_documents']}")
        print(f"  总字符数: {stats['total_characters']}")
        print(f"  平均块大小: {stats['avg_chunk_length']:.0f}")
    else:
        print("[WARN] 未找到文档")
        print(f"  请将文档放入: {Config.DOCUMENTS_DIR}")
except Exception as e:
    print(f"[ERROR] 文档加载失败: {e}")
    sys.exit(1)

# 测试4: 创建向量存储
print("\n测试4: 创建向量存储...")
try:
    vector_manager = VectorStoreManager()
    
    if documents:
        print("  正在创建向量索引...")
        vector_store = vector_manager.create_vector_store(documents, force_recreate=True)
        info = vector_manager.get_collection_info()
        print(f"[OK] 向量存储创建成功")
        print(f"  文档数量: {info.get('document_count', 0)}")
    else:
        print("[WARN] 跳过向量存储创建（无文档）")
except Exception as e:
    print(f"[ERROR] 向量存储创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试5: 初始化RAG管道
print("\n测试5: 初始化RAG管道...")
try:
    pipeline = RAGPipeline()
    print("[OK] RAG管道初始化成功")
    print(f"  LLM类型: {Config.LLM_TYPE}")
except Exception as e:
    print(f"[ERROR] RAG管道初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[SUCCESS] 所有测试通过！系统准备就绪。")
print("="*60)

print("\n下一步:")
print("  1. 启动交互模式: python main.py --mode interactive")
print("  2. 启动Web界面: python web_app.py --mode web")
print("  3. 查看系统信息: python main.py --mode info")