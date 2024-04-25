from enum import Enum
from rle_compression import RleCompression
from huffman_compression import HuffmanCompression
from lempel_ziv_compression import LempelZivCompression


class CompressionTypes(Enum):
    RLE = RleCompression
    HUFFMAN = HuffmanCompression
    LZ = LempelZivCompression