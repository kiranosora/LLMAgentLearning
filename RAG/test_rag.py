from openai import OpenAI
"""
简易 RAG 原型实现：基于 Playwright 网页抓取 + LangChain 构建 RAG 流程
调用本地部署的 OpenAI 兼容 API（如 Ollama、vLLM 等）

功能流程：
1. 异步抓取指定网页内容
2. 文本分割为小块并嵌入向量化存储到 ChromaDB（内存模式）
3. 用户输入查询时：
   a) 向量化问题并检索最相关文本块
   b) 生成包含上下文的 Prompt 发送给本地 LLM API
4. 返回最终答案

依赖项：
pip install langchain==0.1.2 chromadb sentence-transformers playwright beautifulsoup4
"""

import asyncio
from typing import List
import time

# --- 1. 配置区域 ---
urls_to_scrape = [
    "https://qwenlm.github.io/blog/qwen2.5-vl/",  # 替换为实际目标网页
]

# 嵌入模型配置（确保已下载对应模型）
embedding_model_name = "all-MiniLM-L6-v2"  # 英文模型
# embedding_model_name = "BAAI/bge-base-zh-v1.5"  # 中文模型

# 本地 OpenAI 兼容 API 地址（如 Ollama 默认端口）
local_api_base = "http://localhost:1234/v1"
# 如果 API 需要 KEY（如 Ollama 通常不需要），可设为任意字符串
local_api_key = "dummy"

chunk_size = 1000   # 每个文本块的最大字符数
chunk_overlap = 50  # 块与块之间的重叠区域（避免信息断层）
model_name = "qwq-32b@8bit"

# --- 导入依赖 ---
from playwright.async_api import async_playwright
from langchain.docstore.document import Document  # 文档对象基类
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma  # 向量数据库（内存模式）
from langchain_community.chat_models import ChatOpenAI
import os

# --- 2. 网页内容抓取 ---
async def scrape_web_content(urls: List[str]) -> list[Document]:
    """使用 Playwright 异步抓取网页内容并返回 LangChain Document 列表"""
    docs = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for url in urls:
            try:
                page = await browser.new_page()
                
                # 访问网页并等待 DOM 加载完成
                await page.goto(url, timeout=60_000)
                
                # 提取网页主要文本内容（可根据实际结构调整选择器）
                content = await page.locator("body").inner_text()
                
                # 创建 Document 对象，记录来源 URL
                docs.append(Document(
                    page_content=content,
                    metadata={"source": url}
                ))
                
            except Exception as e:
                print(f"抓取 {url} 失败：{str(e)}")
            finally:
                await page.close()
        
        await browser.close()

    return docs

# --- 3. 构建 RAG 流程 ---
async def build_rag_chain(query: str):
    total_start = time.time()
    """执行完整 RAG 处理流程"""
    
    # --- 步骤 1：抓取网页内容 ---
    print("开始抓取目标网页...")
    
    start_scrape = time.time()  # 添加计时起点
    # 获取原始文档列表
    raw_docs = await scrape_web_content(urls_to_scrape)
    
    if not raw_docs:
        print("未成功抓取任何网页内容，无法继续！")
        return
    end_scrape = time.time()
    print(f"网页抓取耗时: {end_scrape - start_scrape:.2f}秒")

    # --- 步骤 2：文本分块 ---
    start_split = time.time()
    print("正在分割文档为小段...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # 将长文本分割为小块（每个块生成一个 Document 对象）
    split_docs = text_splitter.split_documents(raw_docs)
    end_split = time.time()
    print(f"文本分块耗时: {end_split - start_split:.2f}秒")

    # --- 步骤 3：向量化并存储到 ChromaDB ---
    start_vectorize = time.time()  # 添加计时起点
    print("正在生成文本块的嵌入向量...")
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    embeddings = SentenceTransformerEmbeddings(model_name=embedding_model_name)
    print(f"embeddings device: {embeddings.client.device}")
    from chromadb.utils import embedding_functions
    default_ef = embedding_functions.DefaultEmbeddingFunction()

    # 创建向量数据库（内存模式）
    vector_db = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings
    )
    end_vectorize = time.time()  # 添加计时终点
    print(f"向量化存储耗时: {end_vectorize - start_vectorize:.2f}秒")

    # --- 步骤 4：定义检索器 ---
    retriever = vector_db.as_retriever(
        search_kwargs={"k": 3}   # 返回最相关的前 3 块
    )
    
    # --- 步骤5：定义 LLM 客户端 ---
    start_llm_init = time.time()  # 添加计时起点
    print("初始化本地大模型客户端...")
    
    llm = ChatOpenAI(
        openai_api_base=local_api_base,
        openai_api_key=local_api_key,  # 如果不需要可设为空字符串
        model=model_name
    )    
    end_llm_init = time.time()  # 添加计时终点
    print(f"模型初始化耗时: {end_llm_init - start_llm_init:.2f}秒")
    # --- 步骤6：定义 Prompt 模板 ---
    prompt_template = """
    上下文信息：
    {context}

    问题：{question}
    
    答案（请严格基于上下文回答，不确定时说明）：
    """
    
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # --- 步骤7：构建 RAG 链 ---
    start_invoke = time.time() 
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    
    rag_chain = (
        {
            "context": retriever, 
            "question": RunnablePassthrough()  # 直接传递原始查询
        }  
        | prompt 
        | llm
        | StrOutputParser()  # 将 LLM 输出解析为字符串
    )
    
    print(f"\n正在处理查询：'{query}'")
    answer = rag_chain.invoke(query)
    end_invoke = time.time()  # 添加计时终点
    print(f"模型响应耗时: {end_invoke - start_invoke:.2f}秒")
    print("\n--- 系统回答 ---\n")
    print(answer)
    total_end = time.time()
    print(f"\n执行总耗时: {total_end - total_start:.2f}秒")

# === 主程序入口 ===
if __name__ == "__main__":
    
    # 确保 Playwright 浏览器已安装
    try:
        import playwright.async_api  # 触发自动检查，若未找到浏览器会提示安装
    except:
        print("请先运行：python -m playwright install")
    
    # 设置 Windows 环境的事件循环策略（若需要）
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 用户输入查询
    #user_query = input("请输入您的问题（例如：'页面1的主旨是什么？')：")
    user_query = "介绍Qwen2.5-VL-72B的性能表现和技术指标"
    
    # 执行 RAG 流程
    try:
        asyncio.run(build_rag_chain(user_query))
    
    except Exception as e:
        print(f"运行时发生错误：{str(e)}")
