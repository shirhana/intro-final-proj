import pytest
from rle_compression import *

data_compression = RleCompression()


@pytest.mark.parametrize("string, bytes_size, result", [
    ("WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", 1, "12W1B12W3B24W1B14W"),
    ("WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW", 2, "6WW1BW5WW1WB1BB12WW1BW6WW1W"),
    ("ABCSDDDDDD", 1, "1A1B1C1S6D"),
    ("ABCSDDDDDD", 2, "1AB1CS3DD")

])
def test_rle_compress(string, bytes_size, result):
    assert result == data_compression.compress_data(data=string, bytes_size=bytes_size)


@pytest.mark.parametrize("compressed_data, bytes_size, result", [
    ("12W1B12W3B24W1B14W", 1, "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"),
    ("6WW1BW5WW1WB1BB12WW1BW6WW1W", 2, "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"),
    ( "1A1B1C1S6D", 1, "ABCSDDDDDD"),
    ("1AB1CS3DD", 2, "ABCSDDDDDD")
])
def test_rle_extract(compressed_data, bytes_size, result):
    assert result == data_compression.decompress_data(compressed_data=compressed_data, bytes_size=bytes_size)
