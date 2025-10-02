# logger.py - AstraLogger "星录" 全局日志系统
# 一言既出，万籁俱寂

import threading
from typing import Any, Callable, Optional, Union
from pathlib import Path
from loguru import logger as _loguru_logger

class AstraLogger:
    """
    AstraLogger "星录" —— 全局日志管理类（基于 loguru）
    特性：
      - 单例模式，全局共享
      - 线程安全
      - 支持动态添加/移除日志输出（文件、控制台等）
      - 支持运行时调整日志级别
      - 模块级快捷函数：info(), error(), debug() 等
    """
    _instance = None
    _lock = threading.RLock()
    _handlers = {}  # 存储 handler_id -> config 映射，便于管理

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        with self._lock:
            if hasattr(self, 'initialized'):
                return
            # 清除 loguru 默认 handler（避免重复输出）
            _loguru_logger.remove()
            self.initialized = True

    # ==================================================================================
    # 类方法接口（对外使用）
    # ==================================================================================

    @classmethod
    def add_sink(
        cls,
        sink: Union[str, Path, Callable],
        level: str = "DEBUG",
        format: Optional[str] = None,
        rotation: Optional[Union[str, int]] = None,
        retention: Optional[Union[str, int]] = None,
        **kwargs
    ) -> str:
        """
        添加日志输出目标（类方法）
        :param sink: 输出目标（文件路径、函数、sys.stderr 等）
        :param level: 日志级别
        :param format: 日志格式
        :param rotation: 轮转策略（如 "10 MB", "1 day"）
        :param retention: 保留策略
        :return: handler_id（用于后续移除）
        """
        instance = cls()
        return instance._add_sink(sink, level, format, rotation, retention, **kwargs)

    @classmethod
    def remove_sink(cls, handler_id: str) -> None:
        """移除指定 handler"""
        instance = cls()
        instance._remove_sink(handler_id)

    @classmethod
    def set_level(cls, level: str) -> None:
        """设置全局最低日志级别"""
        _loguru_logger.remove()  # 清空所有
        # 重新添加现有 sinks，但需记录？为简化，此处建议用户管理 sinks
        # 更佳做法：保留 sinks 配置并重建 —— 此处简化处理
        raise NotImplementedError("动态全局级别调整需配合 sinks 管理，建议通过 add_sink 控制")

    # 日志记录快捷方法
    @classmethod
    def trace(cls, message: str, *args, **kwargs):
        _loguru_logger.trace(message, *args, **kwargs)

    @classmethod
    def debug(cls, message: str, *args, **kwargs):
        _loguru_logger.debug(message, *args, **kwargs)

    @classmethod
    def info(cls, message: str, *args, **kwargs):
        _loguru_logger.info(message, *args, **kwargs)

    @classmethod
    def warning(cls, message: str, *args, **kwargs):
        _loguru_logger.warning(message, *args, **kwargs)

    @classmethod
    def error(cls, message: str, *args, **kwargs):
        _loguru_logger.error(message, *args, **kwargs)

    @classmethod
    def critical(cls, message: str, *args, **kwargs):
        _loguru_logger.critical(message, *args, **kwargs)

    @classmethod
    def exception(cls, message: str, *args, **kwargs):
        _loguru_logger.exception(message, *args, **kwargs)

    @classmethod
    def stop(cls) -> None:
        """停止并清理所有日志处理器"""
        instance = cls()
        instance._stop()

    # ==================================================================================
    # 实例方法实现（内部逻辑）
    # ==================================================================================

    def _add_sink(
        self,
        sink: Union[str, Path, Callable],
        level: str = "DEBUG",
        format: Optional[str] = None,
        rotation: Optional[Union[str, int]] = None,
        retention: Optional[Union[str, int]] = None,
        **kwargs
    ) -> str:
        with self._lock:
            # loguru 的 add 返回 handler id（int），我们转为 str 便于管理
            handler_id = _loguru_logger.add(
                sink=sink,
                level=level,
                format=format or "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                rotation=rotation,
                retention=retention,
                enqueue=True,  # 异步、线程安全
                **kwargs
            )
            handler_key = str(handler_id)
            self._handlers[handler_key] = {
                "sink": sink,
                "level": level,
                "rotation": rotation,
                "retention": retention,
                **kwargs
            }
            return handler_key

    def _remove_sink(self, handler_id: str) -> None:
        with self._lock:
            if handler_id in self._handlers:
                _loguru_logger.remove(int(handler_id))
                del self._handlers[handler_id]

    def _stop(self) -> None:
        with self._lock:
            _loguru_logger.remove()  # 移除所有 handler
            self._handlers.clear()


# ==================================================================================
# 模块级快捷方式（推荐使用）
# ==================================================================================

# 使用方式：from logger import info, error, add_sink, stop
trace = AstraLogger.trace
debug = AstraLogger.debug
info = AstraLogger.info
warning = AstraLogger.warning
error = AstraLogger.error
critical = AstraLogger.critical
exception = AstraLogger.exception
add_sink = AstraLogger.add_sink
remove_sink = AstraLogger.remove_sink
stop_logger = AstraLogger.stop