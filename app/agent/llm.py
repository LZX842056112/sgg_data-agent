from langchain.chat_models import init_chat_model
from app.conf.app_config import app_config

# 构建langchain模型对象
llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key=app_config.llm.api_key,
    temperature=0)
if __name__ == '__main__':
    for chunk in llm.stream("who are you?"):
        print(chunk.text, end="")
