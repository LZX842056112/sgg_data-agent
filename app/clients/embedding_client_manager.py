from typing import Optional
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddedClientManager:
    """
    嵌入式向量嵌入客户端管理器类
    用于管理 HuggingFaceEndpointEmbeddings 客户端的初始化和配置
    """

    def __init__(self, config: EmbeddingConfig):
        """
        初始化嵌入式客户端管理器

        Args:
            config (EmbeddingConfig): 嵌入服务的配置对象，包含 host、port 等关键配置
        """
        # 保存嵌入服务配置
        self.config = config
        # 初始化嵌入客户端对象，初始值为 None，后续通过 init 方法初始化
        self.client: Optional[HuggingFaceEndpointEmbeddings] = None

    def _get_url(self):
        """
        私有方法：根据配置拼接嵌入服务的完整 URL

        Returns:
            str: 拼接后的嵌入式服务地址（http://host:port 格式）
        """
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        """
        初始化 HuggingFaceEndpointEmbeddings 客户端
        将拼接好的服务 URL 作为模型地址传入客户端
        """
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())


# 创建 EmbeddedClientManager 实例（全局变量），传入应用配置中的嵌入服务配置
embedding_client_manager = EmbeddedClientManager(app_config.embedding)

# 主程序入口：测试嵌入式客户端功能
if __name__ == '__main__':
    # 创建 EmbeddedClientManager 实例
    client = EmbeddedClientManager(app_config.embedding)
    # 初始化嵌入客户端
    client.init()
    # 对文本 "hello world" 进行向量嵌入
    query = client.client.embed_query("hello world")
    # 打印嵌入向量的长度
    print(len(query))
    # 打印嵌入向量的具体值
    print(query)
