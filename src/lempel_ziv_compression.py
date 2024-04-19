from data_compression import DataCompression


class LempelZivCompression(DataCompression):
        
    def compress_data(self, data):
        compress_data = bytearray()
        index = 1
        result = {}
        prev = ""
        for c in data:
            current = prev + chr(c)
            if current in result:
                prev = current
            else:
                result[current] = index
                if prev == "":
                    compress_data.append(0)
                else:
                    compress_data.append(result[prev])

                compress_data.extend(chr(c).encode())
                
                prev = ""
                index += 1 

        if prev == current:
            compress_data.extend(b'*^&')
            compress_data.append(result[prev])
    
        return bytes(compress_data)

    def decompress_data(self, compressed_data: str | bytes) -> bytes:
        decompress_data = bytearray()
        codebook = {}
        index = 1
        for i in range(0, len(compressed_data), 2):
            codebook_index = compressed_data[i]
            if codebook_index == 0:
                decompress_data.append(compressed_data[i+1])
                prev = ""
            elif i+3 < len(compressed_data) and compressed_data[i] == 42 and compressed_data[i+1] == 94 and compressed_data[i+2] == 38:

                prev = next((key for key, val in codebook.items() if val == compressed_data[i+3]))
                decompress_data.extend(prev.encode())
                break
            else:
                prev = next((key for key, val in codebook.items() if val == codebook_index))
                decompress_data.extend(prev.encode())
                decompress_data.append(compressed_data[i+1])

            codebook[f"{prev}{chr(compressed_data[i+1])}"] = index
            index += 1
        return bytes(decompress_data)
    
    def get_metadata(self) -> bytes:
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())

        return bytes(metadata)






# with open('free-nature-images.jpg', 'rb') as f:
#     data = f.read()

#     print(data[:10])

# h = LempelZivCompression()
# a = h.compress_data(data=data[:10])

# print(f'a: {a}')
# b = h.decompress_data(a)
# print(f'b: {b}')