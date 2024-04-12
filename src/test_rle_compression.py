import pytest
from rle_compression import *

data_compression = RleCompression()


@pytest.mark.parametrize("string, bytes_size, result", [
    ("WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", 1, "12WB12W3B24WB14W"),
    ("WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", 2, "6WWBW5WWWBBB12WWBW6WWW"),
    ("ABCSDDDDDD", 1, "ABCS6D"),
    ("ABCSDDDDDD", 2, "ABCS3DD")

])
def test_rle_compress(string, bytes_size, result):
    assert result == data_compression.compress_data(data=string, bytes_size=bytes_size)


@pytest.mark.parametrize("compressed_data, bytes_size, result", [
    ("12WB12W3B24WB14W", 1, "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"),
    ("6WWBW5WWWBBB12WWBW6WWW", 2, "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"),
    ( "ABCS6D", 1, "ABCSDDDDDD"),
    ("ABCS3DD", 2, "ABCSDDDDDD")
])
def test_rle_extract(compressed_data, bytes_size, result):
    assert result == data_compression.decompress_data(compressed_data=compressed_data, bytes_size=bytes_size)
