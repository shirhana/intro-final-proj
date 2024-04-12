from data_compression import DataCompression
from typing import Union
from utility import print_progress_bar, timer, Logger


class RleCompression(DataCompression):

    def compress_data(self, data, bytes_size=2):
        compressed_data = bytearray()
        count = 1
        for i in range(0, len(data), bytes_size):
            if data[i:i+bytes_size] == data[i+bytes_size:i+2*bytes_size]:
                count += 1
            else:
                if count > 1:
                    compressed_data.append(42) # ord('*')
                    compressed_data.append(94) # ord('^')
                    compressed_data.append(38) # ord('&')
                    compressed_data.append(count)
                compressed_data.extend(data[i:i+bytes_size])
                count = 1

        return bytes(compressed_data)


    def decompress_data(self, compressed_data, bytes_size=1):
        decompressed_data = bytearray()
        i = 0
        while i < len(compressed_data):
            if compressed_data[i] == 42 and compressed_data[i+1] == 94 and compressed_data[i+2] == 38: # ord('*'), ord('^'), ord('&')
                count = compressed_data[i+3]
                i += 4
            else: 
                count = 1
            bytes_value = compressed_data[i:i+bytes_size]
            decompressed_data.extend(bytes_value * count)
            i += bytes_size
        return bytes(decompressed_data)
    

    # def compress_data(self, data, bytes_size):
    #     compressed_data = bytearray()
    #     count = 1
    #     prev_pixel = data[0]
    #     for pixel in data[1:]:
    #         if pixel == prev_pixel:
    #             count += 1
    #         else:
    #             compressed_data.append(count)
    #             compressed_data.append(prev_pixel)
    #             count = 1
    #             prev_pixel = pixel
    #     compressed_data.append(count)
    #     compressed_data.append(prev_pixel)
    #     return bytes(compressed_data)

    # def decompress_data(self, compressed_data, bytes_size):
    #     decompressed_data = bytearray()
    #     i = 0
    #     while i < len(compressed_data):
    #         count = compressed_data[i]
    #         pixel = compressed_data[i + 1]
    #         decompressed_data.extend([pixel] * count)
    #         i += 2
    #     return bytes(decompressed_data)

   