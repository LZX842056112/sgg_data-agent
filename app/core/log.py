import asyncio
import sys
import uuid
from pathlib import Path

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import request_id_ctx_var

# 配置日志格式
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "  # 绿色显示日志时间（精确到毫秒）
    "<level>{level: <8}</level> | "  # 按级别颜色显示日志级别（左对齐，占8个字符）
    "<magenta>request_id - {extra[request_id]}</magenta> | "  # 品红色显示request_id（从日志extra中获取）
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "  # 青色显示日志所在文件、函数、行号
    "<level>{message}</level>"  # 按级别颜色显示日志正文
)


def inject_request_id(record):
    """
    Loguru 日志补丁函数：为日志记录对象注入 request_id（请求唯一标识）
    保证每条日志都能关联到对应的请求，便于问题排查和请求链路追踪

    Args:
        record: Loguru 的日志记录对象，包含日志的所有上下文信息（如时间、级别、extra 等）
    """
    try:
        # 尝试从上下文变量中获取当前请求的 request_id
        # 上下文变量适配异步/多请求场景，可保证不同请求的 request_id 互不干扰
        request_id = request_id_ctx_var.get()
    except Exception as e:
        # 若获取失败（如上下文变量未初始化、无有效值等异常），生成 UUID4 作为兜底的唯一标识
        # 避免因 request_id 获取失败导致日志记录异常
        request_id = uuid.uuid4()
    # 将 request_id 存入日志记录的 extra 字段，供日志格式中 {extra[request_id]} 调用
    record["extra"]["request_id"] = request_id


# 移除Loguru默认的控制台输出（避免重复输出日志）
logger.remove()

# 给日志打补丁，使其在输出每条日志前执行inject_request_id函数，注入request_id
logger = logger.patch(inject_request_id)

# 如果配置中开启了控制台日志输出
if app_config.logging.console.enable:
    # 添加控制台日志输出器
    logger.add(sink=sys.stdout, level=app_config.logging.console.level, format=log_format)

# 如果配置中开启了文件日志输出
if app_config.logging.file.enable:
    # 1. 获取项目根目录（当前文件所在目录的上层/上层，根据实际结构调整）
    # 核心逻辑：__file__ 是当前文件路径，.parent 向上找根目录
    # 如果你不确定层级，可以打印调试：print(Path(__file__).absolute())
    PROJECT_ROOT = Path(__file__).parents[2]  # 根据实际项目结构调整
    # 2. 拼接日志路径：项目根目录 / logs / app.log
    LOG_DIR = PROJECT_ROOT / "logs"
    LOG_FILE = LOG_DIR / "app.log"

    # 3. 创建日志目录（确保存在）
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    # 添加文件日志输出器
    logger.add(
        sink=LOG_FILE,  # 日志文件完整路径
        level=app_config.logging.file.level,  # 文件日志输出级别
        format=log_format,  # 使用自定义的日志格式
        rotation=app_config.logging.file.rotation,  # 日志文件分割规则（如按大小/时间）
        retention=app_config.logging.file.retention,  # 日志文件保留时长
        encoding="utf-8"  # 日志文件编码格式
    )
if __name__ == '__main__':
    async def graph(request: str):
        # 获取ID值
        id = request_id_ctx_var.get()
        # 输出结果
        logger.info(id)


    async def test1():
        # 接收到请求
        request_id_ctx_var.set("111111111")

        # 模拟处理
        await asyncio.sleep(1)
        await graph("request-1")


    async def test2():
        # 接收到请求sink
        request_id_ctx_var.set("2222222222")

        # 模拟处理
        await asyncio.sleep(1)
        await graph("request-2")


    async def main():
        await asyncio.gather(test1(), test2())


    asyncio.run(main())
