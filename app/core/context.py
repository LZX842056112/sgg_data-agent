from contextvars import ContextVar

# 定义上下文变量request_id_ctx_var，用于在异步/多请求场景下存储和获取当前请求的唯一标识request_id
# 参数1："request_id" - 上下文变量的名称，用于标识该变量的用途
# 参数2：default=1 - 默认值，当未显式设置request_id时，获取到的值为1
request_id_ctx_var = ContextVar("request_id", default=1)
