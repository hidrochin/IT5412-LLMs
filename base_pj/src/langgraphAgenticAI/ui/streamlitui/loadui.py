import streamlit as st
import os

from src.langgraphAgenticAI.ui.uiconfig import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config=Config()
        self.user_control={}

    def load_streamlit_ui(self):
        st.set_page_config(self.config.get_page_title(), layout="wide")
        st.header(self.config.get_page_title())

        with st.sidebar:
            # get option from config
            llms_option = self.config.get_llms_option()
            usecase_option = self.config.get_usecase_option()

            # LLMs selection
            self.user_control["selected_llm"] = st.selectbox("Select LLM", llms_option)

            if self.user_control["selected_llm"] == "Gemini":
                # Model selection
                model_options = self.config.get_gemini_model_option()
                self.user_control["selected_gemini_model"] = st.selectbox("Select Model", model_options)
                self.user_control["GEMINI_API_KEY"] = st.session_state["GEMINI_API_KEY"] = st.text_input("API_KEY", type="password")

                # Validate:
                if not self.user_control["GEMINI_API_KEY"]:
                    st.warning("Get your Gemini API key !")

            # Usecase selection
            self.user_control["selected_usecase"]=st.selectbox("Select Usecases", usecase_option)

        return self.user_control