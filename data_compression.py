from abc import ABC, abstractmethod


class DataCompression(ABC):
    """DataCompression is an interface for data compression algorithms.

    Args:
        ABC: A metaclass for defining abstract base classes.

    Attributes:
        _max_bytes_range (int): The maximum range of bytes supported by 
        the compression algorithm.
        _bigger_than_max_bytes_sign (bytes): A special sign used to indicate
        data exceeding the maximum byte range.

    Methods:
        compress_data(data: bytes) -> bytes: Abstract method for 
        compressing data.
        decompress_data(compressed_data: bytes) -> bytes: Abstract 
        method for decompressing data.
        get_metadata() -> bytes: Abstract method for retrieving 
        metadata related to the compression.
    """ 

    def __init__(self) -> None:
        """Initialize the DataCompression interface.
        """        
        self._max_bytes_range = 256
        self._bigger_than_max_bytes_sign = b'*^&'

    
    @abstractmethod
    def compress_data(data: bytes) -> bytes:
        """Compresses input data.

        Args:
            data (bytes): The data to be compressed.

        Returns:
            bytes: The compressed data.
        """
        pass

    @abstractmethod
    def decompress_data(compressed_data: bytes) -> bytes:
        """Decompresses input data.

        Args:
            compressed_data (bytes): The compressed data.

        Returns:
            bytes: The decompressed data.
        """
        pass

    @abstractmethod
    def get_metadata() -> bytes:
        """Retrieves metadata related to the compression.

        Returns:
            bytes: The metadata information.
        """
        pass