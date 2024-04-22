import pytest
from src.rle_compression import *



@pytest.mark.parametrize("bytes_input, bytes_size, result", [
    (b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", 1,  b'*^&\x0cWB*^&\x0cW*^&\x03B*^&\x18WB*^&\x0eW'),
    (b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", 2, b'*^&\x06WWBW*^&\x05WWWBBB*^&\x0cWWBW*^&\x06WWW'),
    (b"ABCSDDDDDD", 1,  b'ABCS*^&\x06D'),
    (b"ABCSDDDDDD", 2,  b'ABCS*^&\x03DD')

])
def test_rle_compress(bytes_input, bytes_size, result):
    data_compression = RleCompression(bytes_size=bytes_size)
    assert result == data_compression.compress_data(data=bytes_input)


@pytest.mark.parametrize("compressed_data, bytes_size, result", [
    (b'*^&\x0cWB*^&\x0cW*^&\x03B*^&\x18WB*^&\x0eW', 1, b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"),
    (b'*^&\x06WWBW*^&\x05WWWBBB*^&\x0cWWBW*^&\x06WWW', 2, b"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"),
    (b'ABCS*^&\x06D', 1, b"ABCSDDDDDD"),
    (b'ABCS*^&\x03DD', 2, b"ABCSDDDDDD")
])
def test_rle_extract(compressed_data, bytes_size, result):
    data_compression = RleCompression(bytes_size=bytes_size)
    assert result == data_compression.decompress_data(compressed_data=compressed_data)
