import heapq
import json
from data_compression import DataCompression


class HuffmanCompression(DataCompression):

    def __init__(self):
        super().__init__()
        self._heap = []
        self._codes = {}
        self._reverse_mapping = {}

    class HeapNode:
        def __init__(self, char, freq):
            self._char = char
            self._freq = freq
            self._left = None
            self._right = None

        def __lt__(self, other):
            return self._freq < other._freq

        def __eq__(self, other):
            if(other == None):
                return False
            if(not isinstance(other, self.HeapNode)):
                return False
            return self._freq == other._freq

    def make_frequency_dict(self, text):
        frequency = {}
        for character in text:
            if character not in frequency:
                frequency[character] = 0
            frequency[character] += 1
        return frequency

    def make_heap(self, frequency):
        for key in frequency:
            node = self.HeapNode(key, frequency[key])
            heapq.heappush(self._heap, node)

    def merge_nodes(self):
        if len(self._heap) == 1:
            node1 = heapq.heappop(self._heap)
            merged = self.HeapNode(None, node1._freq)
            merged._left = node1

            heapq.heappush(self._heap, merged)

        while(len(self._heap) > 1):
            node1 = heapq.heappop(self._heap)
            node2 = heapq.heappop(self._heap)

            merged = self.HeapNode(None, node1._freq + node2._freq)
            merged._left = node1
            merged._right = node2

            heapq.heappush(self._heap, merged)

    def make_codes_helper(self, root, current_code):
        if(root == None):
            return

        if(root._char is not None):
            self._codes[root._char] = current_code
            self._reverse_mapping[current_code] = root._char
            return

        self.make_codes_helper(root._left, current_code + "0")
        if root._right is not None:
            self.make_codes_helper(root._right, current_code + "1")

    def make_codes(self):
        try:
            root = heapq.heappop(self._heap)
            current_code = ""
            self.make_codes_helper(root, current_code)
        except IndexError:
            pass

    def get_encoded_text(self, text):
        encoded_text = ""
        for character in text:
            encoded_text += self._codes[character]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if(len(padded_encoded_text) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def compress_data(self, data):
        self._reverse_mapping = {}
        data = data.rstrip()
        frequency = self.make_frequency_dict(data)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()

        encoded_text = self.get_encoded_text(data)
        padded_encoded_text = self.pad_encoded_text(encoded_text)

        byte_array = self.get_byte_array(padded_encoded_text)
        compress_data = bytearray()
        huffman_table_len = len(json.dumps(self._reverse_mapping).encode())
        if huffman_table_len >= self._max_bytes_range:
            a = huffman_table_len // self._max_bytes_range
            b = huffman_table_len % self._max_bytes_range
            compress_data.extend(self._bigger_than_max_bytes_sign)
            compress_data.extend(a.to_bytes(1, byteorder='big'))
            compress_data.extend(b.to_bytes(1, byteorder='big'))
        else:
            compress_data.append(huffman_table_len)
        compress_data.extend(json.dumps(self._reverse_mapping).encode())
        compress_data.extend(bytes(byte_array))

        return bytes(compress_data)

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1 * extra_padding]

        return encoded_text

    def decode_data(self, encoded_text, huffman_table={}):
        current_code = ""
        b = bytearray()

        if huffman_table:
            self._reverse_mapping = huffman_table

        for bit in encoded_text:
            current_code += bit
            if(current_code in self._reverse_mapping):
                character = self._reverse_mapping[current_code]
                b.extend(character.to_bytes(byteorder='little'))
                current_code = ""

        return bytes(b)

    def decompress_data(self, compressed_data):
        if compressed_data[0] == self._bigger_than_max_bytes_sign[0] and compressed_data[1] == self._bigger_than_max_bytes_sign[1] and compressed_data[2] == self._bigger_than_max_bytes_sign[2]:
            start_index = 5
            huffman_table_len = self._max_bytes_range * compressed_data[3] + compressed_data[4] + 4
        else:
            start_index = 1
            huffman_table_len = compressed_data[0]

        hufffman_table = json.loads(compressed_data[start_index:huffman_table_len + 1].decode())

        bit_string = ""
        i = huffman_table_len + 1

        while i < len(compressed_data):
            byte = compressed_data[i]
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            i += 1

        encoded_data = self.remove_padding(bit_string)
        decompressed_data = self.decode_data(encoded_text=encoded_data, huffman_table=hufffman_table)
        return decompressed_data


    def get_metadata(self) -> bytes:
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())

        return bytes(metadata)
    