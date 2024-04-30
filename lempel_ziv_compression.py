from data_compression import DataCompression


class LempelZivCompression(DataCompression):
    """
    Implements the Lempel-Ziv compression algorithm for data compression.

    This class inherits from DataCompression and provides methods for
    compressingand decompressing data using the Lempel-Ziv algorithm.

    Attributes:
        _last_data_bytes_sign (bytes): The sign used to mark the last
        data bytes.

    Methods:
        __init__: Initialize the LempelZivCompression object.
        compress_prev: Compress the previous sequence in the compression
        process.
        get_byte_representation: Get the byte representation of an integer.
        compress_data: Compress data using the Lempel-Ziv algorithm.
        bigger_than_max_bytes: Check if the compressed data uses a
        bigger-than-maximum byte representation.
        decompress_data_bigger_than_max_size: Decompress data with a
        bigger-than-maximum byte representation.
        end_of_data: Check if the compressed data indicates the end of
        the data.
        get_key_by_val: Get a key from a dictionary by its value.
        update_codebook: Update the codebook used in decompression.
        update_decompress_data: Update the decompressed data during
        decompression.
        decompress_regular_data: Decompress regular data in the
        decompression process.
        get_special_signs: special signs for the compression algorithm.
        decompress_data: Decompress data using the Lempel-Ziv algorithm.
    """

    def __init__(self) -> None:
        """
        Initializes the LempelZivCompression object.

        This constructor initializes the object and
        sets the last data bytes sign.
        """
        super().__init__()
        self._last_data_bytes_sign = b"!@#"

    def compress_prev(
        self, result: dict, prev: bytes, compress_data: bytearray
    ) -> None:
        """Compresses the previous sequence in Lempel-Ziv compression.

        Args:
            result (dict): The compression result dictionary.
            prev (bytes): The previous sequence.
            compress_data (bytearray): The compressed data.
        """
        if result[prev] >= self._max_bytes_range:
            compress_data.extend(self._bigger_than_max_bytes_sign)

            original_a = int(result[prev] / self._max_bytes_range)
            if original_a >= self._max_bytes_range:
                compress_data.extend(self._bigger_than_max_bytes_sign)

                a = int(original_a / self._max_bytes_range)
                b = original_a % self._max_bytes_range
                if self.valid_append_for_compression(
                    compress_data=compress_data, extra_append=a):
                    compress_data.append(a)
                if self.valid_append_for_compression(
                    compress_data=compress_data, extra_append=b):
                    compress_data.append(b)
            else:
                if self.valid_append_for_compression(
                    compress_data=compress_data, extra_append=original_a):
                    compress_data.append(original_a)

            c = result[prev] % self._max_bytes_range
            if self.valid_append_for_compression(
                    compress_data=compress_data, extra_append=c):
                compress_data.append(c)
        else:
            if self.valid_append_for_compression(
                    compress_data=compress_data, extra_append=result[prev]):
                compress_data.append(result[prev])

    def get_byte_representation(self, n: int) -> bytes:
        """Converts an integer into its byte representation.

        Args:
            n (int): The integer to be converted.

        Returns:
            bytes: The byte representation of the integer.
        """
        if n == 0:
            byte_representation = b"\x00"
        else:
            num_bytes = (n.bit_length() + 7) // 8
            byte_representation = n.to_bytes(num_bytes, byteorder="big")

        return byte_representation

    def compress_data(self, data: bytes) -> bytes:
        """Compresses the input data using Lempel-Ziv compression.

        Args:
            data (bytes): The input data to be compressed.

        Returns:
            bytes: The compressed data.
        """
        compress_data = bytearray()
        index = 1
        result = {}
        prev = b""
        current = None
        for c in data:
            byte_representation = self.get_byte_representation(c)
            current = prev + byte_representation
            if current in result:
                prev = current
            else:
                result[current] = index
                if prev == b"":
                    compress_data.append(0)
                else:
                    self.compress_prev(
                        result=result, prev=prev, compress_data=compress_data
                    )

                if self.valid_extend_for_compression(
                    compress_data=compress_data, extra_extend=byte_representation):
                    compress_data.extend(byte_representation)
                prev = b""
                index += 1

        if prev == current:
            compress_data.extend(self._last_data_bytes_sign)
            self.compress_prev(
                result=result, prev=prev, compress_data=compress_data
            )

        return bytes(compress_data)

    def bigger_than_max_bytes(self, compressed_data: bytes, i: int) -> bool:
        """Checks if the data size is bigger than the maximum bytes range.

        Args:
            compressed_data (bytes): The compressed data.
            i (int): The index to check in the compressed data.

        Returns:
            bool: True if the size is bigger than the max bytes range,
            False otherwise.
        """
        if (
            compressed_data[i] == self._bigger_than_max_bytes_sign[0]
            and compressed_data[i + 1] == self._bigger_than_max_bytes_sign[1]
            and compressed_data[i + 2] == self._bigger_than_max_bytes_sign[2]
        ):
            return True
        return False

    def decompress_data_bigger_than_max_size(
        self,
        decompress_data: bytearray,
        compressed_data: bytes,
        codebook: dict,
        index: int,
        i: int,
    ) -> int:
        """Decompresses data that is bigger than the maximum bytes range.

        Args:
            decompress_data (bytearray): The decompressed data.
            compressed_data (bytes): The compressed data.
            codebook (dict): The codebook for decompression.
            index (int): The current index for decompression.
            i (int): The current index in the compressed data.

        Returns:
            int: The updated index in the compressed data.
        """
        if self.bigger_than_max_bytes(
            compressed_data=compressed_data, i=i + 3
        ):
            a = (
                self._max_bytes_range * compressed_data[i + 6]
                + compressed_data[i + 7]
            )
            b = compressed_data[i + 8]
            i += 9
        else:
            a = compressed_data[i + 3]
            b = compressed_data[i + 4]
            i += 5

        codebook_index = self._max_bytes_range * a + b
        prev = self.get_key_by_val(d=codebook, value=codebook_index)

        byte_representation = self.get_byte_representation(
            n=compressed_data[i]
        )
        self.update_decompress_data(
            decompress_data=decompress_data,
            prev=prev,
            extra_append=byte_representation,
        )
        self.update_codebook(codebook, prev, byte_representation, index)
        i += 1
        return i

    def end_of_data(self, compressed_data: bytes, i: int) -> bool:
        """Checks if the end of data is reached in decompression.

        Args:
            compressed_data (bytes): The compressed data.
            i (int): The current index in the compressed data.

        Returns:
            bool: True if end of data, False otherwise.
        """
        if (
            i + 3 < len(compressed_data)
            and compressed_data[i] == self._last_data_bytes_sign[0]
            and compressed_data[i + 1] == self._last_data_bytes_sign[1]
            and compressed_data[i + 2] == self._last_data_bytes_sign[2]
        ):
            
            return True
        return False

    def get_key_by_val(self, d: dict, value: any) -> any:
        """Gets the key from a dictionary by its value.

        Args:
            d (dict): The dictionary.
            value: The value to search for.

        Returns:
            Any: The key corresponding to the value.
        """
        try:
            return next((key for key, val in d.items() if val == value))
        except StopIteration:
            raise StopIteration(
                f"Error - {value} does not exist as value in dict."
            )

    def update_codebook(
        self,
        codebook: dict,
        prev: bytes,
        byte_representation: bytes,
        index: int,
    ) -> None:
        """Updates the codebook during decompression.

        Args:
            codebook (dict): The codebook dictionary.
            prev (bytes): The previous sequence.
            byte_representation (bytes): The byte representation of the
            current sequence.
            index (int): The current index for decompression.
        """
        p = prev + byte_representation
        codebook[p] = index

    def update_decompress_data(
        self,
        decompress_data: bytearray,
        prev: bytes,
        extra_append: bytes = None,
    ) -> None:
        """Updates the decompressed data during decompression.

        Args:
            decompress_data (bytearray): The decompressed data.
            prev (bytes): The previous sequence.
            extra_append (bytes): Additional byte to append to the
            decompressed data.
        """
        decompress_data.extend(prev)

        if extra_append is not None:
            decompress_data.extend(extra_append)

    def decompress_end_of_data(
        self,
        compressed_data: bytes,
        codebook: dict,
        decompress_data: bytearray,
        i: int,
    ) -> None:
        """Handles decompression at the end of data.

        Args:
            compressed_data (bytes): The compressed data.
            codebook (dict): The codebook for decompression.
            decompress_data (bytearray): The decompressed data.
            i (int): The current index in the compressed data.
        """
        if self.bigger_than_max_bytes(
            compressed_data=compressed_data, i=i + 3
        ):
            codebook_index = (
                self._max_bytes_range * compressed_data[i + 6]
                + compressed_data[i + 7]
            )
        else:
            codebook_index = compressed_data[i + 3]

        prev = self.get_key_by_val(d=codebook, value=codebook_index)
        self.update_decompress_data(decompress_data=decompress_data, prev=prev)

    def decompress_regular_data(
        self,
        decompress_data: bytearray,
        compressed_data: bytes,
        codebook: dict,
        codebook_index: int,
        index: int,
        i: int,
    ) -> int:
        """Handles decompression of regular data.

        Args:
            decompress_data (bytearray): The decompressed data.
            compressed_data (bytes): The compressed data.
            codebook (dict): The codebook for decompression.
            codebook_index (int): The index in the codebook.
            index (int): The current index for decompression.
            i (int): The current index in the compressed data.

        Returns:
            int: The updated index in the compressed data.
        """
        prev = self.get_key_by_val(d=codebook, value=codebook_index)

        byte_representation = self.get_byte_representation(
            n=compressed_data[i + 1]
        )
        self.update_decompress_data(
            decompress_data=decompress_data,
            prev=prev,
            extra_append=byte_representation,
        )
        self.update_codebook(codebook, prev, byte_representation, index)
        i += 2
        return i

    def decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompresses the compressed data using Lempel-Ziv decompression.

        Args:
            compressed_data (bytes): The compressed data to be decompressed.

        Returns:
            bytes: The decompressed data.
        """
        decompress_data = bytearray()
        codebook = {}
        index = 1
        i = 0
        while i < len(compressed_data):
            codebook_index = compressed_data[i]
            if codebook_index == 0:
                decompress_data.append(compressed_data[i + 1])
                prev = b""
                byte_representation = self.get_byte_representation(
                    n=compressed_data[i + 1]
                )
                self.update_codebook(
                    codebook, prev, byte_representation, index
                )
                i += 2
            elif self.bigger_than_max_bytes(
                compressed_data=compressed_data, i=i
            ):
                i = self.decompress_data_bigger_than_max_size(
                    decompress_data=decompress_data,
                    compressed_data=compressed_data,
                    codebook=codebook,
                    index=index,
                    i=i,
                )
            elif self.end_of_data(compressed_data=compressed_data, i=i):
                self.decompress_end_of_data(
                    compressed_data=compressed_data,
                    codebook=codebook,
                    decompress_data=decompress_data,
                    i=i,
                )
                break
            else:
                i = self.decompress_regular_data(
                    decompress_data=decompress_data,
                    compressed_data=compressed_data,
                    codebook=codebook,
                    codebook_index=codebook_index,
                    index=index,
                    i=i,
                )

            index += 1

        return bytes(decompress_data)

    def get_metadata(self) -> bytes:
        """Gets metadata information about the compression algorithm.

        Returns:
            bytes: Metadata information encoded as bytes.
        """
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())

        return bytes(metadata)

    def get_special_signs(self) -> list:
        """Get the special signs for the compression algorithm.

        Returns:
            list: A list of special signs, including the last data bytes sign.
        """
        special_signs = super().get_special_signs()
        special_signs.append(self._last_data_bytes_sign)

        return special_signs

