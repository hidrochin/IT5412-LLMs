from configparser import ConfigParser

class Config:
    def __init__(self, config_file="./src/langgraphAgenticAI/ui/uiconfig.ini"):
        self.config=ConfigParser()
        self.config.read(config_file)

    def get_llms_option(self):
        return self.config["DEFAULT"].get("LLMs_OPTION").split(",")
    
    def get_usecase_option(self):
        return self.config["DEFAULT"].get("USE_CASE_OPTION").split(",")
    
    def get_gemini_model_option(self):
        return self.config["DEFAULT"].get("GEMINI_MODEL_OPTION").split(",")
    
    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")