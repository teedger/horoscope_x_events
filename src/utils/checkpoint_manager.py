"""
Checkpoint Manager - Явцыг хадгалж, зогссон газраас үргэлжлүүлэх

Энэ модуль нь үйл явцыг хадгалж, алдаа гарсан эсвэл зогссон тохиолдолд
зогссон газраасаа үргэлжлүүлэх боломжийг олгоно.
"""

import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import joblib


class CheckpointManager:
    """
    Checkpoint удирдах класс

    Attributes:
        checkpoint_dir (Path): Checkpoint файлуудын хавтас

    Examples:
        >>> manager = CheckpointManager()
        >>> manager.save('scraping_progress', {'year': 1950, 'count': 100})
        >>> data = manager.load('scraping_progress')
        >>> print(data)  # {'year': 1950, 'count': 100}
    """

    def __init__(self, checkpoint_dir: str = 'data/checkpoints'):
        """
        CheckpointManager-ийг эхлүүлэх

        Args:
            checkpoint_dir: Checkpoint файлууд хадгалах хавтас
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """
        Checkpoint хадгалах

        Args:
            name: Checkpoint-ийн нэр
            data: Хадгалах өгөгдөл (pickle хийгдэх)
            metadata: Нэмэлт мэдээлэл (JSON хэлбэрээр)

        Examples:
            >>> manager.save('progress', {'year': 2000}, {'desc': 'Scraping year 2000'})
        """
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"
        metadata_file = self.checkpoint_dir / f"{name}_meta.json"

        # Data хадгалах (pickle ашиглан - Python объект хадгална)
        try:
            joblib.dump(data, checkpoint_file)
        except Exception as e:
            raise Exception(f"Checkpoint хадгалах үед алдаа гарлаа: {e}")

        # Metadata хадгалах (JSON хэлбэрээр)
        if metadata is None:
            metadata = {}

        metadata['timestamp'] = datetime.now().isoformat()
        metadata['checkpoint_file'] = str(checkpoint_file)

        # Өгөгдлийн хэмжээ
        if hasattr(data, '__len__'):
            metadata['size'] = len(data)
        else:
            metadata['size'] = 'N/A'

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"✓ Checkpoint хадгалагдлаа: {name}")

    def load(self, name: str) -> Any:
        """
        Checkpoint унших

        Args:
            name: Checkpoint-ийн нэр

        Returns:
            Хадгалагдсан өгөгдөл, эсвэл None хэрэв байхгүй бол

        Examples:
            >>> data = manager.load('progress')
            >>> if data:
            ...     print(f"Loaded: {data}")
        """
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"

        if not checkpoint_file.exists():
            return None

        try:
            data = joblib.load(checkpoint_file)
            print(f"✓ Checkpoint уншигдлаа: {name}")
            return data
        except Exception as e:
            print(f"⚠ Checkpoint унших үед алдаа гарлаа ({name}): {e}")
            return None

    def exists(self, name: str) -> bool:
        """
        Checkpoint байгаа эсэхийг шалгах

        Args:
            name: Checkpoint-ийн нэр

        Returns:
            True хэрэв checkpoint байвал, үгүй бол False

        Examples:
            >>> if manager.exists('progress'):
            ...     print("Checkpoint олдсон, үргэлжлүүлнэ")
        """
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"
        return checkpoint_file.exists()

    def delete(self, name: str) -> None:
        """
        Checkpoint устгах

        Args:
            name: Checkpoint-ийн нэр
        """
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"
        metadata_file = self.checkpoint_dir / f"{name}_meta.json"

        if checkpoint_file.exists():
            checkpoint_file.unlink()
        if metadata_file.exists():
            metadata_file.unlink()

        print(f"✓ Checkpoint устгагдлаа: {name}")

    def list_checkpoints(self) -> list:
        """
        Бүх checkpoint-уудын жагсаалт

        Returns:
            Checkpoint-уудын нэрсийн жагсаалт
        """
        checkpoints = []
        for file in self.checkpoint_dir.glob("*.pkl"):
            checkpoints.append(file.stem)
        return checkpoints

    def get_metadata(self, name: str) -> Optional[Dict]:
        """
        Checkpoint-ийн metadata авах

        Args:
            name: Checkpoint-ийн нэр

        Returns:
            Metadata dictionary эсвэл None
        """
        metadata_file = self.checkpoint_dir / f"{name}_meta.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)


# Singleton instance
_default_manager = None

def get_checkpoint_manager(checkpoint_dir: str = 'data/checkpoints') -> CheckpointManager:
    """
    Global checkpoint manager авах

    Args:
        checkpoint_dir: Checkpoint хавтас

    Returns:
        CheckpointManager instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = CheckpointManager(checkpoint_dir)
    return _default_manager
