from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BoxReader(ABC):
    @abstractmethod
    def read_text_from_box(self, page: int, box: Tuple[int, int, int, int]) -> Optional[str]:
        pass
