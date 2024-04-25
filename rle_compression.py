from data_compression import DataCompression


class RleCompression(DataCompression):

    def __init__(self, bytes_size) -> None:
        super().__init__()
        self._bytes_size = bytes_size

    def compress_data(self, data):
        compressed_data = bytearray()
        count = 1
        for i in range(0, len(data), self._bytes_size):
            if data[i:i+self._bytes_size] == data[i+self._bytes_size:i+2*self._bytes_size]:
                count += 1
            else:
                if count > 1:
                    compressed_data.extend(self._bigger_than_max_bytes_sign)
                    compressed_data.append(count)
                compressed_data.extend(data[i:i+self._bytes_size])
                count = 1

        return bytes(compressed_data)


    def decompress_data(self, compressed_data):
        decompressed_data = bytearray()
        i = 0
        while i < len(compressed_data):
            if compressed_data[i] == self._bigger_than_max_bytes_sign[0] and compressed_data[i+1] == self._bigger_than_max_bytes_sign[1] and compressed_data[i+2] == self._bigger_than_max_bytes_sign[2]:
                count = compressed_data[i+3]
                i += 4
            else: 
                count = 1
            bytes_value = compressed_data[i:i+self._bytes_size]
            decompressed_data.extend(bytes_value * count)
            i += self._bytes_size
        return bytes(decompressed_data)
    
    def get_metadata(self):
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())
        metadata.append(self._bytes_size)

        return bytes(metadata)