import asyncio

import jieba.analyse
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """Graph入口节点，将用户问题进行抽取关键词"""
    # 写回当前节点自定义数据
    query = state["query"]
    # 1.获取流写入器对象 方式一：通过函数get_stream_writer获取 方式二：通过Runtime获取
    writer = get_stream_writer()
    # 2.写自定义数据 正在处理中
    writer({"type": "progress", "step": "抽取关键字", "status": "running"})
    try:

        # 3. 使用jieba分词器进行分词
        # 3.1 创建指定词性元组
        allow_pos = (
            "n",  # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",  # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",  # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng",  # 英文
            "i",  # 成语
            "l",  # 常用固定短语
        )
        # 3.2 对用户问题进行分词
        keywords = jieba.analyse.extract_tags(query, topK=10, allowPOS=allow_pos)
        # 4. 拼接原query得到关键词列表（去重）
        keywords = list(set(keywords + [query]))
        writer({"type": "progress", "step": "抽取关键字", "status": "success"})
        logger.info(f"抽取关键字成功:{keywords}")
        # 5.更新state节点数据
        return {"keywords": keywords}
    except Exception as e:
        logger.error(f"抽取关键字节点执行异常:{e}")
        writer({"type": "progress", "step": "抽取关键字", "status": "error"})
        raise
