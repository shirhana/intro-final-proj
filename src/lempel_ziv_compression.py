from data_compression import DataCompression


class LempelZivCompression(DataCompression):
        
    def compress_data(self, data):
        compress_data = bytearray()
        index = 1
        result = {}
        prev = b""
        for c in data:
            if c == 0:
                byte_representation = b'\x00'
            else:
                num_bytes = (c.bit_length() + 7) // 8
                byte_representation = c.to_bytes(num_bytes, byteorder='big')
            current = prev + byte_representation
            if current in result:
                prev = current
            else:
                result[current] = index
                if prev == b"":
                    compress_data.append(0)
                else:
                    if result[prev] >= 256:
                        compress_data.extend(b'***')
                        a = int(result[prev] / 256)
                        b = result[prev] % 256
                        compress_data.append(a)
                        compress_data.append(b)
                    else:
                        compress_data.append(result[prev])

                # compress_data.extend(chr(c).encode())
                if c == 0:
                    byte_representation = b'\x00'
                else:
                    num_bytes = (c.bit_length() + 7) // 8
                    byte_representation = c.to_bytes(num_bytes, byteorder='big')
                
                compress_data.extend(byte_representation)
                
                prev = b""
                index += 1 

        if prev == current:
            compress_data.extend(b'*^&')
            if result[prev] >= 256:
                compress_data.extend(b'***')
                a = int(result[prev] / 256)
                b = result[prev] % 256
                compress_data.append(a)
                compress_data.append(b)
            else:
                compress_data.append(result[prev])
    
        return bytes(compress_data)

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
                if compressed_data[i+1] == 0:
                    byte_representation = b'\x00'
                else:
                    num_bytes = (compressed_data[i+1].bit_length() + 7) // 8
                    byte_representation = compressed_data[i+1].to_bytes(num_bytes, byteorder='big')
                p = prev + byte_representation
                codebook[p] = index
                i += 2
            elif i+5 < len(compressed_data) and compressed_data[i] == 42 and compressed_data[i+1] == 42 and compressed_data[i+2] == 42:
                codebook_index = 256 * compressed_data[i+3] + compressed_data[i+4]
                prev = next((key for key, val in codebook.items() if val == codebook_index))
                decompress_data.extend(prev)
                decompress_data.append(compressed_data[i+5])
                

                if compressed_data[i+5] == 0:
                    byte_representation = b'\x00'
                else:
                    num_bytes = (compressed_data[i+5].bit_length() + 7) // 8
                    byte_representation = compressed_data[i+5].to_bytes(num_bytes, byteorder='big')
                

                p = prev + byte_representation
                codebook[p] = index
                i += 6
            elif i+3 < len(compressed_data) and compressed_data[i] == 42 and compressed_data[i+1] == 94 and compressed_data[i+2] == 38:
                if i+7 < len(compressed_data) and compressed_data[i+3] == 42 and compressed_data[i+4] == 42 and compressed_data[i+5] == 42:
                    codebook_index = 256 * compressed_data[i+6] + compressed_data[i+7]
                    prev = next((key for key, val in codebook.items() if val == codebook_index))
                    decompress_data.extend(prev)
                else:
                    prev = next((key for key, val in codebook.items() if val == compressed_data[i+3]))
                    decompress_data.extend(prev)
                break
            else:
                prev = next((key for key, val in codebook.items() if val == codebook_index))
                decompress_data.extend(prev)
                decompress_data.append(compressed_data[i+1])


                if compressed_data[i+1] == 0:
                    byte_representation = b'\x00'
                else:
                    num_bytes = (compressed_data[i+1].bit_length() + 7) // 8
                    byte_representation = compressed_data[i+1].to_bytes(num_bytes, byteorder='big')
                p = prev + byte_representation
                codebook[p] = index
                i += 2
            
            index += 1
        return bytes(decompress_data)
    
    def get_metadata(self) -> bytes:
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())

        return bytes(metadata)
