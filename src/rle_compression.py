from data_compression import DataCompression
from typing import Union
from utility import print_progress_bar, timer, Logger


class RleCompression(DataCompression):

    def compress_data(self, data: Union[str, bytes], bytes_size=1):
        if isinstance(data, bytes):
            try: 
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                pass
        encoded_data = []
        count = 1

        for i in range(0, len(data), bytes_size):
            if data[i:i+bytes_size] == data[i+bytes_size:i+2*bytes_size]:
                count += 1
            else:
                if count > 1:
                    encoded_data.append(f'{count}{data[i:i+bytes_size]}')
                else: 
                    encoded_data.append(data[i:i+bytes_size])
                count = 1

            if i == len(data):
                if count > 1:
                    encoded_data.append(f'{count}{data[i:i+bytes_size]}')
                else: 
                    encoded_data.append(data[i:i+bytes_size])

            print_progress_bar(iteration=i+1, total=len(data))


        return "".join(encoded_data)

    # TODO - what happens if data contains digits as strings

    def decompress_data(self, compressed_data: Union[str, bytes], bytes_size=1) -> str:
        if isinstance(compressed_data, bytes):
            compressed_data = compressed_data.decode('utf-8')
        decoded_data = []
        count = ''
        i = 0
        while i < len(compressed_data):

            while compressed_data[i].isdigit():
                count += str(compressed_data[i])
                i += 1

            if not count:
                count = '1'

            # i += 1
            decoded_data.append(int(count) * compressed_data[i:i+bytes_size])
            i += bytes_size
            count = ''
            print_progress_bar(iteration=i+1, total=len(compressed_data))

        return "".join(decoded_data)
