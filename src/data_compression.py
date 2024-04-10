from abc import ABC, abstractmethod
from typing import Union


class DataCompression(ABC):
    
    @abstractmethod
    def compress_data(data: Union[str, bytes]) -> str:
        pass

    @abstractmethod
    def decompress_data(compressed_data: Union[str, bytes]) -> str:
        pass