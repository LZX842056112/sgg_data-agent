from sys import argv


from app.core.log import logger


def build():
    print(argv[2])
    logger.info("构建知识库脚本执行了")


if __name__ == '__main__':
    """需求：通过脚本参数 传入人工配置文件路径（包含同步表、字段、说明信息）"""
    build()
