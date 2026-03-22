import os
import sys
os.chdir(r'c:\Users\23149\Documents\trae_projects\ai-project')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

print("Step 1: Loading PDFs with pypdf...", flush=True)
from pypdf import PdfReader

pdf_files = [
    'data/documents/AI深度学习在年龄相关性黄斑变性辅助诊断中的应用_廖德盛.pdf',
    'data/documents/人在回路深度学习垂体分割模型的建立_冷渌清.pdf',
    'data/documents/基于深度学习人工智能辅助系统用于CT检出肋骨新鲜骨折_梁洁.pdf',
    'data/documents/基于深度学习自动化诊断颈动脉狭窄效能的人机对照研究_董铮.pdf',
]

all_text = []
for pdf in pdf_files:
    print(f"  Loading: {os.path.basename(pdf)}", flush=True)
    try:
        reader = PdfReader(pdf)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        all_text.append({"source": os.path.basename(pdf), "content": text})
        print(f"    -> {len(reader.pages)} pages, {len(text)} chars", flush=True)
    except Exception as e:
        print(f"    -> Error: {e}", flush=True)

print(f"\nTotal documents: {len(all_text)}", flush=True)

print("\nStep 2: Splitting text...", flush=True)
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
)

from langchain_core.documents import Document
split_docs = []
for doc in all_text:
    chunks = text_splitter.split_text(doc["content"])
    for i, chunk in enumerate(chunks):
        split_docs.append(Document(page_content=chunk, metadata={"source": doc["source"], "chunk_id": i}))

print(f"Total chunks: {len(split_docs)}", flush=True)

print("\nStep 3: Creating vector store...", flush=True)
from vector_store import VectorStoreManager
manager = VectorStoreManager()
vector_store = manager.create_vector_store(split_docs, force_recreate=True)

info = manager.get_collection_info()
print(f"\n[SUCCESS] Vector index created!", flush=True)
print(f"Documents in index: {info.get('document_count', 0)}", flush=True)
