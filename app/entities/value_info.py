from dataclasses import dataclass

"""保存到ES中字段枚举文档对象"""

@dataclass
class ValueInfo:
  id: str
  value: str
  column_id: str