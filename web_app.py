"""
AI 知识问答助手 - Streamlit Web 界面。
"""

import logging
import os
import sys
import warnings

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

warnings.filterwarnings("ignore")
logging.basicConfig(level=Config.LOG_LEVEL)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)

st.set_page_config(
    page_title="AI知识问答助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="正在加载 RAG 管道和嵌入模型，首次运行可能需要下载模型...")
def get_rag_pipeline():
    from rag_pipeline import RAGPipeline

    return RAGPipeline()


def count_knowledge_files() -> int:
    if not os.path.exists(Config.DOCUMENTS_DIR):
        return 0

    supported_exts = {".pdf", ".txt", ".md", ".docx"}
    return sum(
        1
        for name in os.listdir(Config.DOCUMENTS_DIR)
        if os.path.isfile(os.path.join(Config.DOCUMENTS_DIR, name))
        and os.path.splitext(name)[1].lower() in supported_exts
    )


def vector_index_exists() -> bool:
    return os.path.exists(os.path.join(Config.PERSIST_DIRECTORY, "chroma.sqlite3"))


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🤖 AI知识问答助手")
st.markdown("### 基于 RAG 技术的智能知识问答系统")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ 系统配置")
    st.success("✅ Web 界面已就绪")

    st.divider()
    st.header("📊 系统状态")
    st.info(f"**LLM 类型:** {Config.LLM_TYPE}")
    st.info(f"**嵌入模型:** {Config.EMBEDDING_MODEL.split('/')[-1]}")
    st.info(f"**知识文档:** {count_knowledge_files()} 个")

    if vector_index_exists():
        st.success("**向量索引:** 已生成")
    else:
        st.warning("**向量索引:** 未生成，请先运行 `python main.py --mode index --force`")

    st.divider()
    st.header("📖 使用说明")
    st.markdown(
        """
        1. 在对话框输入问题
        2. 首次提问时系统会加载模型
        3. 回答会优先引用知识库内容

        **提示：**
        - 请先在 `.env` 中配置 API Key
        - 支持 DeepSeek、OpenAI 和 Ollama
        - 新增文档后需要重建向量索引
        """
    )

    st.divider()
    if st.button("🗑️ 清空对话历史", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

tab_chat, tab_info = st.tabs(["💬 问答对话", "ℹ️ 系统信息"])

with tab_chat:
    st.subheader("💬 问答对话")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在检索知识库并生成回答..."):
                try:
                    Config.validate()
                    rag_pipeline = get_rag_pipeline()
                    result = rag_pipeline.query(prompt)

                    if result["success"]:
                        answer_type = result.get("answer_type", "unknown")
                        if answer_type == "knowledge_base":
                            st.info("📚 答案来自知识库")
                        elif answer_type == "general_knowledge":
                            st.info("🌐 答案来自通用知识")

                        st.write(result["answer"])
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": result["answer"]}
                        )
                    else:
                        st.error(result["answer"])
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": result["answer"]}
                        )
                except Exception as exc:
                    error_msg = f"处理问题时出错：{exc}"
                    st.error(error_msg)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": error_msg}
                    )

with tab_info:
    st.subheader("ℹ️ 系统详细信息")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**🤖 语言模型配置**")
        st.write(f"- 类型: {Config.LLM_TYPE}")
        if Config.LLM_TYPE == "deepseek":
            st.write(f"- 模型: {Config.DEEPSEEK_MODEL}")
            st.write(f"- API 地址: {Config.DEEPSEEK_BASE_URL}")
        elif Config.LLM_TYPE == "openai":
            st.write(f"- 模型: {Config.OPENAI_MODEL}")
        elif Config.LLM_TYPE == "ollama":
            st.write(f"- 模型: {Config.OLLAMA_MODEL}")
            st.write(f"- 主机: {Config.OLLAMA_HOST}")

    with col2:
        st.write("**🔎 嵌入模型配置**")
        st.write(f"- 模型: {Config.EMBEDDING_MODEL}")
        st.write(f"- 维度: {Config.EMBEDDING_DIMENSION}")

    st.divider()
    st.write("**📄 文档处理配置**")
    st.write(f"- 文档目录: {Config.DOCUMENTS_DIR}")
    st.write(f"- 知识文档: {count_knowledge_files()} 个")
    st.write(f"- 分块大小: {Config.CHUNK_SIZE} 字符")
    st.write(f"- 分块重叠: {Config.CHUNK_OVERLAP} 字符")
    st.write(f"- 检索数量: {Config.SEARCH_TOP_K} 个片段")

    st.divider()
    st.write("**💾 向量存储信息**")
    st.write(f"- 存储路径: {Config.PERSIST_DIRECTORY}")
    st.write(f"- 索引状态: {'已生成' if vector_index_exists() else '未生成'}")

st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: gray;">
    <p>AI 知识问答助手 v1.0 | RAG + Chroma + LangChain</p>
</div>
""",
    unsafe_allow_html=True,
)
