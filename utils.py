import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging


class JsonLoader:
    """JSON文件加载器 - 基础版本"""

    @staticmethod
    def load_json_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> Any:
        """
        读取单个JSON文件

        Args:
            file_path: JSON文件路径
            encoding: 文件编码

        Returns:
            JSON数据（字典、列表等）

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path

        # 验证文件
        if not path.exists():
            raise FileNotFoundError(f"JSON文件不存在: {path}")
        if not path.is_file():
            raise ValueError(f"路径不是文件: {path}")
        if path.suffix.lower() != '.json':
            logging.warning(f"文件后缀不是.json: {path}")

        # 读取文件
        try:
            with open(path, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError as e:
            # 尝试其他编码
            encodings = ['utf-8-sig', 'gbk', 'gb2312', 'latin-1']
            for enc in encodings:
                try:
                    with open(path, 'r', encoding=enc) as f:
                        return json.load(f)
                except UnicodeDecodeError:
                    continue
            raise e

class JsonWriter:
    """JSON文件写入器 - 基础版本"""

    @staticmethod
    def write_json(
            data: Dict[str, Any],
            file_path: Union[str, Path],
            encoding: str = 'utf-8',
            indent: int = 2,
            ensure_ascii: bool = False
    ) -> bool:
        """
        将字典写入JSON文件

        Args:
            data: 要写入的字典数据
            file_path: 输出文件路径
            encoding: 文件编码
            indent: 缩进空格数
            ensure_ascii: 是否确保ASCII编码

        Returns:
            bool: 是否写入成功
        """
        try:
            path = Path(file_path) if isinstance(file_path, str) else file_path

            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)

            # 写入JSON文件
            with open(path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

            logging.info(f"JSON文件写入成功: {path}")
            return True

        except Exception as e:
            logging.error(f"JSON文件写入失败 {file_path}: {e}")
            return False



if __name__ == '__main__':
    a = JsonLoader.load_json_file(r"config/config.json")
    print(a)