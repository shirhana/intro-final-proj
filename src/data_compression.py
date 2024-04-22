from abc import ABC, abstractmethod
from typing import Union


class DataCompression(ABC):

    def __init__(self) -> None:
        self._bigger_than_256_sign = b'*^&'
    
    @abstractmethod
    def compress_data(data: Union[str, bytes]) -> bytes:
        pass

    @abstractmethod
    def decompress_data(compressed_data: Union[str, bytes]) -> bytes:
        pass

    @abstractmethod
    def get_metadata() -> bytes:
        pass