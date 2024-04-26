import heapq
import json
from data_compression import DataCompression


class HuffmanCompression(DataCompression):
    """HuffmanCompression is a class that implements Huffman coding 
    for data compression.

    Args:
        DataCompression (class): The base class for data compression 
        algorithms.

    Attributes:
        _heap (list): The heap used for building the Huffman tree.
        _codes (dict): A dictionary mapping characters to Huffman codes.
        _reverse_mapping (dict): A dictionary mapping Huffman codes to 
        characters.

    Methods:
        make_frequency_dict(text: str) -> dict: Creates a frequency dictionary 
        for characters in the input text.
        make_heap(frequency: dict): Creates a heap from the frequency 
        dictionary.
        merge_nodes(): Merges nodes in the heap to build the Huffman tree.
        make_codes_helper(root, current_code): Helper function to generate 
        Huffman codes.
        make_codes(): Generates Huffman codes for characters in the input
        text.
        get_encoded_text(text: str) -> str: Encodes the input text using
        Huffman codes.
        pad_encoded_text(encoded_text: str) -> str: Pads the encoded text 
        to ensure byte alignment.
        get_byte_array(padded_encoded_text: str) -> bytearray: Converts padded
        encoded text to byte array.
        compress_data(data) -> bytes: Compresses input data using Huffman
        coding.
        remove_padding(padded_encoded_text: str) -> str: Removes padding 
        from encoded text.
        decode_data(encoded_text: str, huffman_table: dict) -> bytes: Decodes 
        Huffman encoded text.
        decompress_data(compressed_data: bytes) -> bytes: Decompresses data 
        compressed with Huffman coding.
        get_metadata() -> bytes: Retrieves metadata related to Huffman 
        compression.
    """

    def __init__(self):
        """Initialize the HuffmanCompression class.
        """
        super().__init__()
        self._heap = []
        self._codes = {}
        self._reverse_mapping = {}

    class HeapNode:
        """HeapNode represents a node in the Huffman tree.

        Args:
            char (str): The character associated with the node.
            freq (int): The frequency of the character.

        Methods:
            __lt__(self, other): Compares HeapNodes based on frequency.
            __eq__(self, other): Checks equality between HeapNodes 
            based on frequency.
        """
        def __init__(self, char: str, freq: int) -> None:
            """Initialize a HeapNode with a character and its frequency.

            Args:
                char (str): The character associated with the node.
                freq (int): The frequency of the character.
            """
            self._char = char
            self._freq = freq
            self._left = None
            self._right = None

        def __lt__(self, other):
            """Compares HeapNodes based on frequency.

            Args:
                other (HeapNode): The other HeapNode to compare.

            Returns:
                bool: True if the current node has a lower frequency than 
                the other node.
            """
            return self._freq < other._freq

        def __eq__(self, other):
            """Checks equality between HeapNodes based on frequency.

            Args:
                other (HeapNode): The other HeapNode to compare.

            Returns:
                bool: True if the frequencies of both nodes are equal.
            """
            if(other == None):
                return False
            if(not isinstance(other, self.HeapNode)):
                return False
            return self._freq == other._freq

    def make_frequency_dict(self, text: bytes) -> dict:
        """Creates a frequency dictionary for characters in the input text.

        Args:
            text (bytes): The input text for frequency analysis.

        Returns:
            dict: A dictionary mapping characters to their frequencies.
        """
        frequency = {}
        for character in text:
            if character not in frequency:
                frequency[character] = 0
            frequency[character] += 1
        return frequency

    def make_heap(self, frequency: dict) -> None:
        """Creates a heap from the frequency dictionary.

        Args:
            frequency (dict): A dictionary mapping characters 
            to their frequencies.
        """
        for key in frequency:
            node = self.HeapNode(key, frequency[key])
            heapq.heappush(self._heap, node)

    def merge_nodes(self) -> None:
        """Merges nodes in the heap to build the Huffman tree.
        """
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

    def make_codes_helper(self, root, current_code: str) -> None:
        """Helper function to generate Huffman codes.

        Args:
            root: The root of the Huffman tree.
            current_code (str): The current Huffman code being generated.
        """
        if(root == None):
            return

        if(root._char is not None):
            self._codes[root._char] = current_code
            self._reverse_mapping[current_code] = root._char
            return

        self.make_codes_helper(root._left, current_code + "0")
        if root._right is not None:
            self.make_codes_helper(root._right, current_code + "1")

    def make_codes(self) -> None:
        """Generates Huffman codes for characters in the input text.
        """
        try:
            root = heapq.heappop(self._heap)
            current_code = ""
            self.make_codes_helper(root, current_code)
        except IndexError:
            pass

    def get_encoded_text(self, text: bytes) -> str:
        """Encodes the input text using Huffman codes.

        Args:
            text (bytes): The input text to be encoded.

        Returns:
            str: The encoded text using Huffman codes.
        """
        encoded_text = ""
        for character in text:
            encoded_text += self._codes[character]
        return encoded_text

    def pad_encoded_text(self, encoded_text: str) -> str:
        """Pads the encoded text to ensure byte alignment.

        Args:
            encoded_text (str): The encoded text.

        Returns:
            str: The padded encoded text.
        """
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text: str) -> bytearray:
        """Converts padded encoded text into a byte array.

        Args:
            padded_encoded_text (str): The padded encoded text.

        Returns:
            bytearray: The byte array representation of the encoded text.
        """
        if(len(padded_encoded_text) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def compress_data(self, data: bytes) -> bytes:
        """Compresses the input data using Huffman coding.

        Args:
            data (bytes): The input data to be compressed.

        Returns:
            bytes: The compressed data.
        """
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

    def remove_padding(self, padded_encoded_text: str) -> str:
        """Removes padding from the padded encoded text.

        Args:
            padded_encoded_text (str): The padded encoded text.

        Returns:
            str: The decoded text without padding.
        """
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1 * extra_padding]

        return encoded_text

    def decode_data(self, encoded_text: str, 
                    huffman_table: dict = {}) -> bytes:
        """Decodes the encoded text using the provided Huffman table.

        Args:
            encoded_text (str): The encoded text to be decoded.
            huffman_table (dict): The Huffman table for decoding.

        Returns:
            bytes: The decoded data.
        """
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

    def decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompresses the compressed data using Huffman decoding.

        Args:
            compressed_data (bytes): The compressed data to be decompressed.

        Returns:
            bytes: The decompressed data.
        """
        if compressed_data[0] == self._bigger_than_max_bytes_sign[0] \
            and compressed_data[1] == self._bigger_than_max_bytes_sign[1] \
                and compressed_data[2] == self._bigger_than_max_bytes_sign[2]:
            start_index = 5
            huffman_table_len = self._max_bytes_range * compressed_data[3] \
                + compressed_data[4] + 4
        else:
            start_index = 1
            huffman_table_len = compressed_data[0]

        hufffman_table = json.loads(
            compressed_data[start_index:huffman_table_len + 1].decode())

        bit_string = ""
        i = huffman_table_len + 1

        while i < len(compressed_data):
            byte = compressed_data[i]
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            i += 1

        encoded_data = self.remove_padding(bit_string)
        decompressed_data = self.decode_data(encoded_text=encoded_data, 
                                             huffman_table=hufffman_table)
        return decompressed_data


    def get_metadata(self) -> bytes:
        """Gets metadata information about the huffman compression 
        algorithm.

        Returns:
            bytes: Metadata information encoded as bytes.
        """
        metadata = bytearray()
        metadata.extend(self.__class__.__name__.encode())

        return bytes(metadata)
    