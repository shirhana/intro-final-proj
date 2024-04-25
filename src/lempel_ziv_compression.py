from data_compression import DataCompression


class LempelZivCompression(DataCompression):

    def __init__(self) -> None:
        super().__init__()
        self._last_data_bytes_sign = b"***"

    def compress_prev(self, result, prev, compress_data):
        if result[prev] >= self._max_bytes_range:
            compress_data.extend(self._bigger_than_max_bytes_sign)
            
            a = int(result[prev] / self._max_bytes_range)
            if a >= self._max_bytes_range:
                compress_data.extend(self._bigger_than_max_bytes_sign)
                a = int(a / self._max_bytes_range)
                b = a % self._max_bytes_range
                compress_data.append(a)
                compress_data.append(b)
                
            else:
                compress_data.append(a)
            
            b = result[prev] % self._max_bytes_range
            compress_data.append(b)
        else:
            compress_data.append(result[prev])

    def get_byte_representation(self, n: int):
        if n == 0:
            byte_representation = b'\x00'
        else:
            num_bytes = (n.bit_length() + 7) // 8
            byte_representation = n.to_bytes(num_bytes, byteorder='big')

        return byte_representation
        
    def compress_data(self, data):
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
                    self.compress_prev(result=result, prev=prev, compress_data=compress_data)
                    
                byte_representation = self.get_byte_representation(c)
                compress_data.extend(byte_representation)
                prev = b""
                index += 1 

        if prev == current:
            compress_data.extend(self._last_data_bytes_sign)
            self.compress_prev(result=result, prev=prev, compress_data=compress_data)
    
        return bytes(compress_data)
    
    def bigger_than_max_bytes(self, compressed_data, i):
        if compressed_data[i] == self._bigger_than_max_bytes_sign[0] and compressed_data[i+1] == self._bigger_than_max_bytes_sign[1] and compressed_data[i+2] == self._bigger_than_max_bytes_sign[2]:
            return True
        return False
    
    def decompress_data_bigger_than_max_size(self, decompress_data, compressed_data, codebook, index, i):
        if self.bigger_than_max_bytes(compressed_data=compressed_data, i=i+3):
            a = self._max_bytes_range * compressed_data[i+6] + compressed_data[i+7]
            b = compressed_data[i+8]            
            i += 9
        else:
            a = compressed_data[i+3]
            b = compressed_data[i+4]
            i += 5

        codebook_index = self._max_bytes_range * a + b
        prev = self.get_key_by_val(d=codebook, value=codebook_index)
        self.update_decompress_data(decompress_data=decompress_data, prev=prev, extra_append=compressed_data[i])
        byte_representation = self.get_byte_representation(n=compressed_data[i])
        self.update_codebook(codebook, prev, byte_representation, index)
        i += 1
        return i
    
    def end_of_data(self, compressed_data, i):
        if i+3 < len(compressed_data) and compressed_data[i] == self._last_data_bytes_sign[0] and compressed_data[i+1] == self._last_data_bytes_sign[1] and compressed_data[i+2] == self._last_data_bytes_sign[2]:
            return True
        return False
    
    def get_key_by_val(self, d: dict, value):
        try:
            return next((key for key, val in d.items() if val == value))
        except StopIteration:
            raise StopIteration(f'Error - {value} does not exist as value in dict.')

    def update_codebook(self, codebook, prev, byte_representation, index):
        p = prev + byte_representation
        codebook[p] = index

    def update_decompress_data(self, decompress_data, prev, extra_append=None):
        decompress_data.extend(prev)

        if extra_append is not None:
            decompress_data.append(extra_append)

    def decompress_end_of_data(self, compressed_data, codebook, decompress_data, i):
        if self.bigger_than_max_bytes(compressed_data=compressed_data, i=i+3):
            codebook_index = self._max_bytes_range * compressed_data[i+6] + compressed_data[i+7]
        else:
            codebook_index = compressed_data[i+3]

        prev = self.get_key_by_val(d=codebook, value=codebook_index)
        self.update_decompress_data(decompress_data=decompress_data, prev=prev)

    def decompress_regular_data(self, decompress_data, compressed_data, codebook, codebook_index, index, i):
        prev = self.get_key_by_val(d=codebook, value=codebook_index)
        self.update_decompress_data(decompress_data=decompress_data, prev=prev, extra_append=compressed_data[i+1])

        byte_representation = self.get_byte_representation(n=compressed_data[i+1])
        self.update_codebook(codebook, prev, byte_representation, index)
        i += 2
        return i

    def decompress_data(self, compressed_data: str | bytes) -> bytes:
        decompress_data = bytearray()
        codebook = {}
        index = 1
        i = 0
        while i < len(compressed_data):
            codebook_index = compressed_data[i]
            if codebook_index == 0:
                decompress_data.append(compressed_data[i+1])
                prev = b""
                byte_representation = self.get_byte_representation(n=compressed_data[i+1])
                self.update_codebook(codebook, prev, byte_representation, index)
                i += 2
            elif self.bigger_than_max_bytes(compressed_data=compressed_data, i=i):
                i = self.decompress_data_bigger_than_max_size(
                    decompress_data=decompress_data, 
                    compressed_data=compressed_data, 
                    codebook=codebook, 
                    index=index, i=i
                )
            elif self.end_of_data(compressed_data=compressed_data, i=i):
                self.decompress_end_of_data(
                    compressed_data=compressed_data,
                    codebook=codebook,
                    decompress_data=decompress_data,
                    i=i
                )
                break
            else:
                i = self.decompress_regular_data(
                    decompress_data=decompress_data,
                    compressed_data=compressed_data,
                    codebook=codebook,
                    codebook_index=codebook_index, 
                    index=index, i=i
                )
            
            index += 1
        return bytes(decompress_data)
    
    def get_metadata(self) -> bytes:
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())

        return bytes(metadata)
