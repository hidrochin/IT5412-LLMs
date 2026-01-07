from dotenv import load_dotenv
import gradio as gr
import uuid
from langchain_core.messages import HumanMessage
from core.chat_interface import ChatInterface
from core.document_manager import DocumentManager
from core.rag_system import RAGSystem

def create_gradio_ui():
    load_dotenv()
    
    # Initialize Core Systems
    rag_system = RAGSystem()
    rag_system.initialize()
    
    doc_manager = DocumentManager(rag_system)
    chat_interface = ChatInterface(rag_system)
    
    # --- HELPER FUNCTIONS (Original Logic) ---
    def format_file_list():
        files = doc_manager.get_markdown_files()
        if not files:
            return "📭 No documents available in the knowledge base"
        return "\n".join([f"{f}" for f in files])
    
    def upload_handler(files, progress=gr.Progress()):
        if not files:
            return None, format_file_list()
            
        added, skipped = doc_manager.add_documents(
            files, 
            progress_callback=lambda p, desc: progress(p, desc=desc)
        )
        gr.Info(f"✅ Added: {added} | Skipped: {skipped}")
        return None, format_file_list()
    
    def clear_handler():
        doc_manager.clear_all()
        gr.Info(f"🗑️ Removed all documents")
        return format_file_list()
    
    def chat_handler(msg, hist):
        return chat_interface.chat(msg, hist)
    
    def clear_chat_handler():
        chat_interface.clear_session()

    # --- ADAPTIVE LEARNING HANDLERS ---
    def run_adaptive_session(message, history, thread_id):
        """
        Custom handler for the Adaptive Learning Tab.
        Forces the 'mode' to 'adaptive' to trigger quiz generation.
        """
        if not message:
            return history, gr.update(visible=False), "", gr.update(choices=[]), -1, ""

        # 1. Initialize History if None
        if history is None:
            history = []

        # 2. Setup Config
        config = {"configurable": {"thread_id": thread_id}}
        
        # 3. Prepare Inputs
        inputs = {
            "messages": [HumanMessage(content=message)],
            "mode": "adaptive"  # Force adaptive mode
        }
        
        bot_msg = "Error generating response."
        quiz = None
        
        try:
            # Invoke Graph
            current_state = rag_system.agent_graph.get_state(config)
            if current_state.next:
                 result = rag_system.agent_graph.invoke(None, config)
            else:
                 result = rag_system.agent_graph.invoke(inputs, config)
            
            # Extract Answer
            if result and "messages" in result and result['messages']:
                bot_msg = result['messages'][-1].content
            else:
                bot_msg = "No response from agent."
            
            # Extract Quiz
            quiz = result.get("quiz_data")
            
        except Exception as e:
            bot_msg = f"Error: {str(e)}"

        # 4. Update History (Proper Gradio Chatbot Format)
        # Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_msg})
        
        # 5. Return Results
        if quiz:
            return (
                history, 
                gr.update(visible=True), 
                f"📝 **Quick Review:** {quiz['question_text']}",
                gr.update(choices=quiz['options'], value=None),
                quiz['correct_option_index'],
                quiz['explanation'],
                quiz['options']
            )
        else:
            return (
                history, 
                gr.update(visible=False), 
                "", 
                gr.update(choices=[]), 
                -1, 
                "",
                []
            )

    def check_quiz(user_choice, correct_idx, options, explanation):
        if not user_choice: return "⚠️ Please select an answer."
        try:
            user_idx = options.index(user_choice)
            if user_idx == correct_idx:
                return f"✅ **Correct!**\n\n{explanation}"
            else:
                # Handle case where options might not match index
                correct_text = options[correct_idx] if 0 <= correct_idx < len(options) else "Unknown"
                return f"❌ **Incorrect.** The answer was: **{correct_text}**.\n\n{explanation}"
        except:
            return "Error processing answer."

    # --- UI LAYOUT ---
    with gr.Blocks(title="Agentic RAG") as demo:
        
        # State for Adaptive Learning Thread
        adaptive_thread_id = gr.State(lambda: str(uuid.uuid4()))

        # === ORIGINAL TAB 1: DOCUMENTS ===
        with gr.Tab("Documents", elem_id="doc-management-tab"):
            gr.Markdown("## Add New Documents")
            gr.Markdown("Upload PDF or Markdown files. Duplicates will be automatically skipped.")
            
            files_input = gr.File(
                label="Drop PDF or Markdown files here",
                file_count="multiple",
                type="filepath",
                height=200,
                show_label=False
            )
            
            add_btn = gr.Button("Add Documents", variant="primary", size="md")
            
            gr.Markdown("## Current Documents in the Knowledge Base")
            file_list = gr.Textbox(
                value=format_file_list(),
                interactive=False,
                lines = 7,
                max_lines=10,
                elem_id="file-list-box",
                show_label=False
            )
            
            with gr.Row():
                refresh_btn = gr.Button("Refresh", size="md")
                clear_btn = gr.Button("Clear All", variant="stop", size="md")
            
            add_btn.click(
                upload_handler, 
                [files_input], 
                [files_input, file_list], 
                show_progress="corner"
            )
            refresh_btn.click(format_file_list, None, file_list)
            clear_btn.click(clear_handler, None, file_list)
        
        # === ORIGINAL TAB 2: STANDARD CHAT ===
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot(
                height=600, 
                placeholder="Ask me anything about your documents!",
                show_label=False
            )
            chatbot.clear(clear_chat_handler)
            gr.ChatInterface(fn=chat_handler, chatbot=chatbot)

        # === NEW TAB 3: ADAPTIVE LEARNING ===
        with gr.Tab("Adaptive Learning (Quiz Mode)"):
            gr.Markdown("### 🎓 Adaptive Tutor")
            gr.Markdown("This agent will explain concepts and then **quiz you** to ensure you understood.")
            
            # Standard Chatbot (Not ChatInterface, to allow custom events)
            adaptive_chatbot = gr.Chatbot(height=450, placeholder="Start learning...")
            adaptive_msg = gr.Textbox(placeholder="What topic do you want to learn?", show_label=False)
            
            # Hidden Quiz Group
            with gr.Group(visible=False) as quiz_group:
                gr.Markdown("---")
                quiz_q = gr.Markdown("## Question")
                quiz_opts = gr.Radio(label="Select Answer")
                quiz_res = gr.Markdown("")
                quiz_btn = gr.Button("Check Answer")
                
                # Hidden state variables
                correct_idx = gr.State(-1)
                explanation = gr.State("")
                options_state = gr.State([])
            # Event Handling
            adaptive_msg.submit(
                run_adaptive_session,
                inputs=[adaptive_msg, adaptive_chatbot, adaptive_thread_id],
                outputs=[adaptive_chatbot, quiz_group, quiz_q, quiz_opts, correct_idx, explanation, options_state]
            )
            
            # Clear input after submit
            adaptive_msg.submit(lambda: "", None, adaptive_msg)

            quiz_btn.click(
                check_quiz,
                inputs=[quiz_opts, correct_idx, options_state, explanation],
                outputs=[quiz_res]
            )

    return demo