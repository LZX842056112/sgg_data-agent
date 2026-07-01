from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "校验SQL", "status": "running"})

    # 1.获取状态中SQL
    try:
        sql = state["sql"]
        # 2.验证SQL
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        await dw_mysql_repository.validate_sql(sql)

        writer({"type": "progress", "step": "校验SQL", "status": "success"})
        return {"error": None}
    except Exception as e:
        writer({"type": "progress", "step": "校验SQL", "status": "error"})
        logger.error(f"校验SQL失败, 错误信息: {str(e)}")
        return {"error": str(e)}


"""
# 执行计划，SQL性能分析关键词
EXPLAIN SELECT SUM(fo.order_amount) AS GMV
FROM fact_order fo
JOIN dim_region dr ON fo.region_id = dr.region_id
WHERE dr.region_name = '华北';

#SQL好坏指标 type 取值性能从低到高：all(全表扫描)<index(全索引扫描)<range(范围查询)<ref(普通索引等值)<const(主键等值)<system

EXPLAIN SELECT * from fact_order WHERE order_id = 'ORD20250103001';

EXPLAIN SELECT * from fact_order WHERE region_id = 'ORD20250103001'

EXPLAIN SELECT * from fact_order WHERE order_amount BETWEEN 10 and 1000

EXPLAIN SELECT order_id from fact_order;
EXPLAIN SELECT * from fact_order;
"""