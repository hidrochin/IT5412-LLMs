from langchain_core.messages import HumanMessage

class ChatInterface:
    
    def __init__(self, rag_system):
        self.rag_system = rag_system
        
    def chat(self, message, history):

        if not self.rag_system.agent_graph:
            return "⚠️ System not initialized!"
            
        try:
            result = self.rag_system.agent_graph.invoke(
                {"messages": [HumanMessage(content=message.strip())]},
                self.rag_system.get_config()
            )
            # Extract the last message content from the agent's response
            last_message = result["messages"][-1].content
            
            # Return in Gradio ChatInterface expected format: a string that will be automatically formatted
            # by the ChatInterface component
            return last_message
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def clear_session(self):
        self.rag_system.reset_thread()