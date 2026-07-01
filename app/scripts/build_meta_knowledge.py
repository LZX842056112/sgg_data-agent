import asyncio
from argparse import ArgumentParser
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(meta_config_path: Path):
    # 1. 初始化操作
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()

    # 2. 创建业务层对象，调用元数据库业务层对象完成元数据库构建
    async with (dw_mysql_client_manager.session_factory() as dw_session, meta_mysql_client_manager.session_factory() as meta_session):
        meta_knowledge_service = MetaKnowledgeService(
            dw_mysql_repository=DWMySQLRepository(dw_session),
            meta_mysql_repository=MetaMySQLRepository(meta_session),
            column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
            embedding_client=embedding_client_manager.client,
            value_es_repository=ValueESRepository(es_client_manager.client),
            metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client)
        )
        await meta_knowledge_service.build(meta_config_path)
    # 3.关闭资源
    await dw_mysql_client_manager.close()
    await meta_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()


if __name__ == '__main__':
    # 1.获取到命令行参数 目的：获取增量动态新增配置信息 sys.argv通过索引获取命令行参数 不方便维护
    # logger.info(argv[2])
    # 1.1 构建参数解析器对象ArgumentParser
    parser = ArgumentParser()
    # 1.2 添加可选命令参数名称或标记名称 对应命令行参数中：xx.py -c
    parser.add_argument("-c", "--conf")
    # 1.3 解析器并将提取的数据
    args = parser.parse_args()
    # 2. 调用脚本执行元数据库构建
    asyncio.run(build(Path(args.conf)))
