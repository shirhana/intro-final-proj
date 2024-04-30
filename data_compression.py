from abc import ABC, abstractmethod
from exceptions import InvalidDataForCompressionAlgorithem

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
        compress_data(data: bytes): Abstract method for compressing data.
        decompress_data(compressed_data: bytes): Abstract method for decompressing data.
        get_metadata(): Abstract method for retrieving metadata related to the compression.
        get_special_signs(): special signs for the compression algorithm.
        valid_append_for_compression(compress_data: bytearray, extra_append: int): check if extra append for compression is valid.
        valid_extend_for_compression(compress_data: bytearray, extra_append: int): check if extra extend for compression is valid.
    """

    def __init__(self) -> None:
        """Initialize the DataCompression interface."""
        self._max_bytes_range = 256
        self._bigger_than_max_bytes_sign = b"*^&"

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

    def get_special_signs(self) -> list:
        """Get the special signs for the compression algorithm.

        Returns:
            list: A list of special signs, including the last data bytes sign.
        """
        special_signs = []
        special_signs.append(self._bigger_than_max_bytes_sign)

        return special_signs
    
    def valid_append_for_compression(
            self, compress_data: bytearray, extra_append: int) -> bool:
        """
        Checks if appending extra data is valid for compression.

        Parameters:
        - compress_data (bytearray): The data to be compressed.
        - extra_append (int): The extra data to append.

        Returns:
        bool: True if the append operation is valid, False otherwise.

        Raises:
        InvalidDataForCompressionAlgorithem: If the data is invalid 
        for compression.
        """
        special_signs = self.get_special_signs()
        for sign in special_signs:
            if len(compress_data) > 1 and compress_data[-2] == sign[0] \
                and compress_data[-1] == sign[1] and extra_append == sign[2]:
                raise InvalidDataForCompressionAlgorithem('Error')
            
        return True
    
    def valid_extend_for_compression(
                self, compress_data: bytearray, extra_extend: bytes) -> bool:
            """
            Checks if extending data is valid for compression.

            Parameters:
            - compress_data (bytearray): The data to be compressed.
            - extra_extend (bytes): The extra data to extend with.

            Returns:
            bool: True if the extend operation is valid, False otherwise.

            Raises:
            InvalidDataForCompressionAlgorithem: If the data is invalid 
            for compression.
            """
            
            special_signs = self.get_special_signs()
            for sign in special_signs:
                if (sign in extra_extend) or (len(compress_data) > 1 and \
                    compress_data[-2] == sign[0] and \
                        compress_data[-1] == sign[1] and \
                            extra_extend[0] == sign[2]):
                    raise InvalidDataForCompressionAlgorithem('Error')
                
            return True

