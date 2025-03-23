from enum import Enum
from rle_compression import RleCompression
from huffman_compression import HuffmanCompression
from lempel_ziv_compression import LempelZivCompression


class CompressionTypes(Enum):
    """An enumeration defining compression types supported by the system.

    This enum maps compression type names to their corresponding
    compression classes.

    Attributes:
        RLE (class): Represents the Run-Length Encoding compression.
        HUFFMAN (class): Represents the Huffman compression.
        LZ (class): Represents the Lempel-Ziv compression.

    """

    RLE = RleCompression
    HUFFMAN = HuffmanCompression
    LZ = LempelZivCompression
