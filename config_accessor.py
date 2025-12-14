# config_accessors.py
import functools
import sys
from typing import Any, Optional, Callable
from datetime import datetime




class ConfigAccessor:
    """
    配置访问器 - 提供热加载配置的便捷访问方式
    """

    def __init__(self, config_key: str, default: Any = None,
                 description: str = "", required: bool = False):
        """
        初始化配置访问器

        Args:
            config_key: 配置键名（支持点式路径）
            default: 默认值
            description: 配置项描述
            required: 是否为必需配置
        """
        self.config_key = config_key
        self.default = default
        self.description = description
        self.required = required
        self._last_value = None
        self._last_access_time = None
        self._access_count = 0

    def __get__(self, obj, objtype=None) -> Any:
        """描述符协议 - 用于属性访问"""
        from AstraConfig import AstraConfig
        AstraConfig.load("config/config.json")
        value = AstraConfig.get(self.config_key, self.default)

        # 记录访问信息
        self._access_count += 1
        self._last_access_time = datetime.now()
        self._last_value = value

        # 检查必需配置
        if self.required and value is None:
            raise ValueError(
                f"必需配置项 '{self.config_key}' 未设置。{self.description}"
            )

        return value

    @property
    def value(self) -> Any:
        """直接获取值"""
        return self.__get__(None)

    @property
    def access_info(self) -> dict:
        """获取访问统计信息"""
        return {
            'key': self.config_key,
            'last_value': self._last_value,
            'last_access_time': self._last_access_time,
            'access_count': self._access_count,
            'description': self.description,
            'required': self.required
        }

    def __call__(self, func: Callable) -> Callable:
        """作为装饰器使用"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取配置值
            value = self.value

            # 如果装饰的函数需要配置值作为参数
            if func.__code__.co_argcount > 0:
                return func(value, *args, **kwargs)
            else:
                # 否则直接调用原函数
                return func(*args, **kwargs)

        return wrapper


# ==================================================================================
# 常用配置访问器定义
# ==================================================================================

# API 相关配置


OPENAI_API_KEY = ConfigAccessor(
    config_key="AstraCore.api.api_key",
    default="",
    description="OpenAI API密钥",
    required=True
)

OPENAI_API_BASE = ConfigAccessor(
    config_key="AstraCore.api.api_base",
    default="https://api.openai.com/v1",
    description="OpenAI API基础URL"
)

OPENAI_MODEL = ConfigAccessor(
    config_key="AstraCore.api.model",
    default="gpt-3.5-turbo",
    description="OpenAI模型名称"
)

OPENAI_TIMEOUT = ConfigAccessor(
    config_key="openai.timeout",
    default=30,
    description="API调用超时时间(秒)"
)
OPENAI_TEMPERATURE = ConfigAccessor(
    config_key="AstraCore.api.temperature",
    default=0.7,
    description="模型温度"
)
OPENAI_PROMPT = ConfigAccessor(
    config_key="AstraCore.api.system_prompt",
    default="You are a helpful AI",
    description="模型提示词"
)
# 数据库配置
DATABASE_URL = ConfigAccessor(
    config_key="database.url",
    default="sqlite:///./data.db",
    description="数据库连接URL",
    required=True
)

DATABASE_POOL_SIZE = ConfigAccessor(
    config_key="database.pool_size",
    default=10,
    description="数据库连接池大小"
)

# 日志配置
LOG_LEVEL = ConfigAccessor(
    config_key="log.level",
    default="INFO",
    description="日志级别"
)

LOG_FILE = ConfigAccessor(
    config_key="log.file",
    default="./logs/app.log",
    description="日志文件路径"
)

# 服务器配置
SERVER_HOST = ConfigAccessor(
    config_key="server.host",
    default="0.0.0.0",
    description="服务器主机"
)

SERVER_PORT = ConfigAccessor(
    config_key="server.port",
    default=8000,
    description="服务器端口"
)

# 缓存配置
REDIS_URL = ConfigAccessor(
    config_key="cache.redis_url",
    default="redis://localhost:6379/0",
    description="Redis连接URL"
)

CACHE_TTL = ConfigAccessor(
    config_key="cache.ttl",
    default=3600,
    description="缓存过期时间(秒)"
)


# ==================================================================================
# 使用示例函数
# ==================================================================================
def get_openai_config() -> dict:
    """获取完整的OpenAI配置"""
    return {
        'api_key': OPENAI_API_KEY.value,
        'api_base': OPENAI_API_BASE.value,
        'model': OPENAI_MODEL.value,
        'timeout': OPENAI_TIMEOUT.value
    }


def print_all_config_access_info():
    """打印所有配置访问器的统计信息"""
    import inspect

    # 获取当前模块的所有配置访问器
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if isinstance(obj, ConfigAccessor):
            info = obj.access_info
            print(f"\n{name}:")
            print(f"  配置键: {info['key']}")
            print(f"  当前值: {info['last_value']}")
            print(f"  访问次数: {info['access_count']}")
            print(f"  最后访问: {info['last_access_time']}")
            print(f"  描述: {info['description']}")
            print(f"  必需: {info['required']}")
if __name__ == '__main__':

    print(get_openai_config())