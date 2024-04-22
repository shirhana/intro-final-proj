import pytest
from src.lempel_ziv_compression import *


@pytest.mark.parametrize("bytes_input, result", [
    (b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", b'\x00W\x01W\x02W\x03W\x02B\x04W\x06W\x01B\x00B\tW\x07W\x0bW\x0cB\x0cW***\x06'),
    (b"ABCSDDDDDD", b'\x00A\x00B\x00C\x00S\x00D\x05D\x06D'),
    (b"1", b'\x001'), 
    (b"12", b'\x001\x002'),
    (b"",  b'')
])
def test_compress(bytes_input, result):
    data_compression = LempelZivCompression()
    print(data_compression.compress_data(data=bytes_input))
    assert result == data_compression.compress_data(data=bytes_input)


@pytest.mark.parametrize("result, compressed_data", [
    (b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", b'\x00W\x01W\x02W\x03W\x02B\x04W\x06W\x01B\x00B\tW\x07W\x0bW\x0cB\x0cW***\x06'),
    (b"ABCSDDDDDD", b'\x00A\x00B\x00C\x00S\x00D\x05D\x06D'),
    (b"1", b'\x001'), 
    (b"12", b'\x001\x002'),
    (b"", b"")
])
def test_decompress(result, compressed_data):
    data_compression = LempelZivCompression()
    assert result == data_compression.decompress_data(compressed_data=compressed_data)
