import uuid
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import config
from db.vector_db_manager import VectorDbManager
from db.parent_store_manager import ParentStoreManager
from document_chunker import DocumentChuncker
from rag_agent.tools import ToolFactory
from rag_agent.graph import create_agent_graph

class RAGSystem:
    
    def __init__(self, collection_name=config.CHILD_COLLECTION):
        self.collection_name = collection_name
        self.vector_db = VectorDbManager()
        self.parent_store = ParentStoreManager()
        self.chunker = DocumentChuncker()
        self.agent_graph = None
        self.thread_id = str(uuid.uuid4())
        
    def initialize(self):
        self.vector_db.create_collection(self.collection_name)
        collection = self.vector_db.get_collection(self.collection_name)
        # self.llm = ChatGoogleGenerativeAI(model=config.GEMINI_MODEL, temperature=config.LLM_TEMPERATURE)
        self.llm = ChatOpenAI(model=config.OPENAI_MODEL, temperature=config.LLM_TEMPERATURE)
        # self.llm = ChatOllama(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)
        # self.llm_quiz = ChatGroq(model=config.GROQ_MODEL, temperature=config.LLM_TEMPERATURE)
        self.llm_quiz = ChatOpenAI(model=config.OPENAI_MODEL, temperature=config.LLM_TEMPERATURE)
        tools = ToolFactory(collection).create_tools()
        self.agent_graph = create_agent_graph(
            llm=self.llm, 
            tools_list=tools,
            llm_quiz=self.llm_quiz,
            )
        
    def get_config(self):
        return {"configurable": {"thread_id": self.thread_id}}
    
    def reset_thread(self):
        try:
            self.agent_graph.checkpointer.delete_thread(self.thread_id)
        except Exception as e:
            print(f"Warning: Could not delete thread {self.thread_id}: {e}")
        self.thread_id = str(uuid.uuid4())