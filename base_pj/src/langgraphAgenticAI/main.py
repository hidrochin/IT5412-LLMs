import streamlit as st
from src.langgraphAgenticAI.ui.streamlitui.loadui import LoadStreamlitUI

def load_langgraph_agentic_ui():
    # load ui
    ui = LoadStreamlitUI()
    user_input=ui.load_streamlit_ui()

    if not user_input:
        st.error("Fail to load user input from UI")
        return
    
    user_message = st.chat_input("Enter your message: ")