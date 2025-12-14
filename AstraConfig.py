# config.py - AstraConfig "星册" 全局配置系统
# 一册藏宙，万律归序

import json
import time
import threading
from typing import Any, Callable, Optional
from pathlib import Path

class AstraConfig:
    """
    AstraConfig "星册" —— 全局配置管理类
    特性：
      - 单例模式，全局共享
      - 支持 JSON / YAML 配置文件
      - 热加载（文件变更自动重载）
      - 线程安全
      - 支持点式嵌套访问：config.get("database.host")
      - 支持配置变更监听
    """
    _instance = None
    _lock = threading.RLock()
    _watchers = []  # 监听器列表：func(old, new)

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
            self._config: dict = {}
            self.config_path: Optional[Path] = None
            self._last_modified: float = 0
            self._polling_interval: float = 2.0
            self._running: bool = False
            self._thread: Optional[threading.Thread] = None
            self.initialized = True

    # ==================================================================================
    # 类方法接口（对外使用）
    # ==================================================================================

    @classmethod
    def load(cls, config_path: str, format_type: Optional[str] = None) -> None:
        """
        加载配置文件（类方法）
        :param config_path: 配置文件路径
        :param format_type: 格式 "json" 或 "yaml"，若为 None 则自动推断
        """
        instance = cls()
        instance._load(config_path, format_type)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置项（类方法）
        :param key: 点式路径，如 "core.model"
        :param default: 默认值
        :return: 配置值
        """
        instance = cls()
        return instance._get(key, default)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        运行时设置配置项（不写入文件）
        """
        instance = cls()
        instance._set(key, value)

    @classmethod
    def reload(cls) -> None:
        """
        手动触发重载
        """
        instance = cls()
        instance._reload()

    @classmethod
    def to_dict(cls) -> dict:
        """
        导出当前配置副本
        """
        instance = cls()
        return instance._to_dict()

    @classmethod
    def add_watcher(cls, callback: Callable[[dict, dict], None]) -> None:
        """
        添加配置变更监听器
        :param callback: 回调函数，参数为 (old_config, new_config)
        """
        instance = cls()
        instance._add_watcher(callback)

    # ==================================================================================
    # 实例方法实现（内部逻辑）
    # ==================================================================================

    def _load(self, config_path: str, format_type: Optional[str]) -> None:
        path = Path(config_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"配置文件未找到: {path}")

        fmt = format_type or self._detect_format(path)
        config_data = self._read_config(path, fmt)

        with self._lock:
            self.config_path = path
            self._config = config_data
            self._last_modified = path.stat().st_mtime
            self._start_watcher()

    def _get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            keys = key.split('.')
            value = self._config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value

    def _set(self, key: str, value: Any) -> None:
        with self._lock:
            keys = key.split('.')
            target = self._config
            for k in keys[:-1]:
                if k not in target or not isinstance(target[k], dict):
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value

    def _reload(self) -> None:
        if not self.config_path or not self.config_path.exists():
            raise RuntimeError("配置文件路径无效，无法重载")

        fmt = self._detect_format(self.config_path)
        new_config = self._read_config(self.config_path, fmt)

        with self._lock:
            old_config = dict(self._config)  # 浅拷贝用于通知
            self._config = new_config
            self._last_modified = self.config_path.stat().st_mtime
            self._trigger_watchers(old_config, new_config)

    def _to_dict(self) -> dict:
        with self._lock:
            import copy
            return copy.deepcopy(self._config)

    def _add_watcher(self, callback: Callable[[dict, dict], None]) -> None:
        with self._lock:
            if callback not in self._watchers:
                self._watchers.append(callback)

    def _read_config(self, path: Path, fmt: str) -> dict:
        try:
            content = path.read_text(encoding='utf-8')
            if fmt == "json":
                return json.loads(content)
            elif fmt == "yaml":
                try:
                    import yaml
                except ImportError:
                    raise RuntimeError("使用 YAML 配置需安装 PyYAML: pip install pyyaml")
                return yaml.safe_load(content) or {}
            else:
                raise ValueError(f"不支持的配置格式: {fmt}")
        except Exception as e:
            raise RuntimeError(f"配置文件解析失败 [{path}]: {e}")

    def _detect_format(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in [".yml", ".yaml"]:
            return "yaml"
        return "json"

    def _start_watcher(self) -> None:
        """启动热加载监控线程"""
        if self._running or self.config_path is None:
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def _watch_loop(self) -> None:
        """轮询检测文件修改"""
        while self._running:
            time.sleep(self._polling_interval)
            if not self.config_path or not self.config_path.exists():
                continue
            try:
                mtime = self.config_path.stat().st_mtime
                if mtime > self._last_modified:
                    self._reload()  # 会加锁
            except Exception as e:
                print(f"[AstraConfig] 热加载检测异常: {e}")

    def _trigger_watchers(self, old: dict, new: dict) -> None:
        """触发所有监听器"""
        for watcher in self._watchers:
            try:
                watcher(old, new)
            except Exception as e:
                print(f"[AstraConfig] 监听器执行失败: {e}")

    def stop_watcher(self):
        """停止热加载线程（可选）"""
        self._running = False


# ==================================================================================
# 模块级快捷方式（可选）
# ==================================================================================

# 使用方式：from config import load, get, reload
load = AstraConfig.load
get = AstraConfig.get
reload = AstraConfig.reload
to_dict = AstraConfig.to_dict
add_watcher = AstraConfig.add_watcher