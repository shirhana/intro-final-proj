import pytest
from huffman_compression import *


@pytest.mark.parametrize("bytes_input, result", [
    (b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", b'\x12{"0": 66, "1": 87}\x05\xff\xf7\xff\x8f\xff\xff\xf7\xff\xe0'),
    (b"ABCSDDDDDD", b'5{"000": 65, "001": 67, "010": 66, "011": 83, "1": 68}\x06\x08\xbf\xc0'),
    (b"1", b'\t{"0": 49}\x07\x00'), 
    (b"12", b'\x12{"0": 49, "1": 50}\x06@'),
    (b"",  b'\x02{}\x08\x00')
])
def test_compress(bytes_input, result):
    data_compression = HuffmanCompression()
    print(data_compression.compress_data(data=bytes_input))
    assert result == data_compression.compress_data(data=bytes_input)


@pytest.mark.parametrize("result, compressed_data", [
    (b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", b'\x12{"0": 66, "1": 87}\x05\xff\xf7\xff\x8f\xff\xff\xf7\xff\xe0'),
    (b"ABCSDDDDDD", b'5{"000": 65, "001": 67, "010": 66, "011": 83, "1": 68}\x06\x08\xbf\xc0'),
    (b"1", b'\t{"0": 49}\x07\x00'),
    (b"12", b'\x12{"0": 49, "1": 50}\x06@'),
    (b"",  b'\x02{}\x08\x00')
])
def test_decompress(result, compressed_data):
    data_compression = HuffmanCompression()
    assert result == data_compression.decompress_data(compressed_data=compressed_data)
    