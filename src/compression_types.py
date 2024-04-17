from enum import Enum
from rle_compression import RleCompression
from huffman_compression import HuffmanCompression


class CompressionTypes(Enum):
    RLE = RleCompression
    HUFFMAN = HuffmanCompression