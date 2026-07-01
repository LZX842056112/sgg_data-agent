import uuid
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class MetaKnowledgeService:

    # 通过构造函数传入各种持久层对象
    def __init__(self, dw_mysql_repository: DWMySQLRepository,
                 meta_mysql_repository: MetaMySQLRepository,
                 column_qdrant_repository: ColumnQdrantRepository,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 value_es_repository: ValueESRepository,
                 metric_qdrant_repository: MetricQdrantRepository
                 ):
        self.dw_mysql_repository = dw_mysql_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.embedding_client = embedding_client
        self.value_es_repository = value_es_repository
        self.metric_qdrant_repository = metric_qdrant_repository

    async def build(self, meta_config_path: Path):
        # 1. 读取传入元数据配置文件，用于获取需要同步的信息
        # 1.1 加载文件内容
        context = OmegaConf.load(meta_config_path)
        # 1.2 通过加载dataClass对象获取存放数据结构
        structured = OmegaConf.structured(MetaConfig)
        # 1.3 将内容跟结构合并，转为dataclass对象
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(structured, context))
        logger.info(meta_config)
        # 2. 核心业务逻辑-处理表格（包含字段）信息
        if meta_config.tables:
            # 2.1  保存表格（包含字段）信息到meta数据库 返回字段信息列表
            column_infos: list[ColumnInfo] = await self._save_table_info_to_meta_db(meta_config)
            logger.info("保存表格信息到meta数据库成功")
            # 2.2  为字段信息建立向量索引
            await self._save_column_info_to_qdrant(column_infos)
            logger.info("为字段信息建立了向量索引成功")
            # 2.3 为字段取值建立全文索引，将字段所有值保存到ES中
            await self._save_value_to_es(meta_config, column_infos)
            logger.info("为字段取值建立全文索引成功")

        # 3. 核心业务逻辑-处理指标（包含字段指标关系）信息
        if meta_config.metrics:
            # 3.1 保存指标（包含字段指标关系）信息到meta数据库
            metric_infos: list[MetricInfo] = await self._save_metric_info_to_meta_db(meta_config)
            logger.info("保存指标信息到meta数据库成功")
            # 3.2 为指标信息建立向量索引
            await self._save_metric_info_to_qdrant(metric_infos)
            logger.info("为指标信息建立向量索引成功")

    async def _save_table_info_to_meta_db(self, meta_config: MetaConfig) -> list[ColumnInfo]:
        # 1.初始化存放表信息dataclass列表, 字段信息dataclass列表
        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []
        # 2.解析配置对象中表信息
        for table in meta_config.tables:
            table_info = TableInfo(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description
            )
            # 3.遍历表信息包含字段列列表
            # 3.1 调用数仓持久层获取数据仓库 指定表中每个字段类型 返回字段结构{字段名称:字段类型}
            column_type_dict: dict[str, str] = await self.dw_mysql_repository.get_column_types(table.name)
            for column in table.columns:
                # 3.2 调用数仓持久层获取数据仓库 指定表中字段部分取值（10个）
                values: list[str] = await self.dw_mysql_repository.get_column_values(table.name, column.name)
                column_info = ColumnInfo(
                    id=f"{table.name}.{column.name}",
                    name=column.name,
                    type=column_type_dict[column.name],
                    role=column.role,
                    examples=values,
                    description=column.description,
                    alias=column.alias,
                    table_id=table.name
                )
                column_infos.append(column_info)
            table_infos.append(table_info)
        async with self.meta_mysql_repository.session.begin():
            await self.meta_mysql_repository.save_table_infos(table_infos)
            await self.meta_mysql_repository.save_column_infos(column_infos)
        return column_infos

    async def _save_column_info_to_qdrant(self, column_infos: list[ColumnInfo]):
        """将字段信息保存到向量索引库qdrant"""
        # 1. 创建存放字段信息向量集合
        await self.column_qdrant_repository.ensure_collection()

        # 2. 准备持久层向量数据点所需啊的三项数据：id, embedding_text, payload
        points = []
        for column_info in column_infos:
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": column_info.name,
                "payload": column_info
            })
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": column_info.description,
                "payload": column_info
            })
            for alias in column_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": alias,
                    "payload": column_info
                })
        # 2.1 对数据点中文本进行分批次向量化,得到向量列表
        embeddings = []
        batch_size = 10
        embedding_texts = [point["embedding_text"] for point in points]
        for i in range(0, len(embedding_texts), batch_size):
            batch = embedding_texts[i:i + batch_size]
            batch_embeddings = await self.embedding_client.aembed_documents(batch)
            embeddings.extend(batch_embeddings)
        # 2.2 获取到数据点ID列表
        ids = [point["id"] for point in points]
        # 2.3 获取到数据点payload列表
        payloads = [point["payload"] for point in points]
        # 3. 调用向量库持久层保存数据点
        await self.column_qdrant_repository.upsert(ids, embeddings, payloads)

    async def _save_value_to_es(self, meta_config: MetaConfig, column_infos: list[ColumnInfo]):
        """将部分字段取值存入ES"""
        # 1. 创建存放字段取值索引库
        await self.value_es_repository.ensure_index()
        # 2.构建保存文档所需要的数据
        value_infos = []
        # 2.1 获取到需要同步数据到到ES 字段名称列表
        column2es = [column.name for table in meta_config.tables for column in table.columns if column.sync == True]
        # 2.2 遍历字段信息列表 处理需要同步到ES字段
        for column_info in column_infos:
            column_name = column_info.name
            table_name = column_info.table_id
            if column_name in column2es:
                # 2.2.1 根据表名+字段名称 获取字段所有取值
                values = await self.dw_mysql_repository.get_column_values(table_name, column_name, limit=100000)
                # 2.2.1 将字段取值列表转为ValueInfo列表
                for value in values:
                    value_info = ValueInfo(
                        id=f"{column_info.id}.{value}",
                        value=value,
                        column_id=column_info.id
                    )
                    value_infos.append(value_info)
        # 3. 调用ES持久层批量保存
        await self.value_es_repository.upsert(value_infos)

    async def _save_metric_info_to_meta_db(self, meta_config: MetaConfig) -> list[MetricInfo]:
        # 1.初始化存放指标信息dataclass列表，字段指标关系dataclass列表
        metric_infos: list[MetricInfo] = []
        column_metric_infos: list[ColumnMetric] = []
        for metric in meta_config.metrics:
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            )
            for relevant_column in metric.relevant_columns:
                column_metric_info = ColumnMetric(
                    column_id=relevant_column,
                    metric_id=metric.name
                )
                column_metric_infos.append(column_metric_info)
            metric_infos.append(metric_info)
        # 2.调用元数据库持久层保存指标信息，字段指标关系信息
        async with self.meta_mysql_repository.session.begin():
            await self.meta_mysql_repository.save_metric_infos(metric_infos)
            await self.meta_mysql_repository.save_column_metric_infos(column_metric_infos)
        return metric_infos

    async def _save_metric_info_to_qdrant(self, metric_infos: list[MetricInfo]):
        # 1.创建存放指标信息向量集合
        await self.metric_qdrant_repository.ensure_collection()
        # 2.准备持久层向量数据点所需要的三项数据：id, embedding_text, payload
        embeddings = []
        points = []
        for metric_info in metric_infos:
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": metric_info.name,
                "payload": metric_info
            })
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": metric_info.description,
                "payload": metric_info
            })
            for alias in metric_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": alias,
                    "payload": metric_info
                })
        embedding_texts = [point["embedding_text"] for point in points]
        batch_size = 10
        for i in range(0, len(embedding_texts), batch_size):
            batch = embedding_texts[i:i + batch_size]
            batch_embeddings = await self.embedding_client.aembed_documents(batch)
            embeddings.extend(batch_embeddings)
        ids = [point["id"] for point in points]
        payloads = [point["payload"] for point in points]
        # 3.调用向量库持久层保存数据点
        await self.metric_qdrant_repository.upsert(ids, embeddings, payloads)
