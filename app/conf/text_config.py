# 需求：读取配置文件得到用户对象  采用OmegaConf
from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

from app.conf.app_config import app_config


# 配置类
@dataclass
class UserInfo:
    name: str
    age: int
    height: float


@dataclass
class MyConfig:
    user: UserInfo
    fav: list[str]


# 1.获取配置文件路径
config_path = Path(__file__).parents[2] / 'conf' / 'text_config.yaml'
# 2.通过OmegaConf读取配置文件 得到字典对象 通过字段名称访问 不方便
context = OmegaConf.load(config_path)

# 3.从dataclass对象加载OmegaConf对象 没有数据
structured = OmegaConf.structured(MyConfig)

# 4.合并结构跟数据 还是字典结构
# 5.将字段转为对象
conf_to_object: MyConfig = OmegaConf.to_object(OmegaConf.merge(structured, context))
# print(conf_to_object)
# print(context["name"])

print(app_config.es)
