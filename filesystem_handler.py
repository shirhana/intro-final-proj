import os
from data_compression import DataCompression
from compression_types import CompressionTypes
from typing import BinaryIO, Dict, List, Optional, Tuple, Union
from exceptions import *


class FilesystemHandler:
    """Filesystem class for handling file compression and
    decompression operations.

    This class provides methods to work with file compression
    algorithms, read and write files, compress data to files,
    decompress files, handle metadata, define compression algorithms,
    and perform validation checks.

    Attributes:
        _compression_algorithem (DataCompression): The data compression
        algorithm instance.
        _output_file (file): The output file object for writing compressed
        data.
        _folder_suffix (str): The suffix used for indicating directories.
        _bytes_length (int): The number of bytes used for storing length
        metadata.

    Methods:
        __init__(self, data_compression_algorithem: DataCompression) -> None:
            Initialize the FilesystemHandler object with a specified
            compression algorithm.

        get_compression_algorithem_name(self) -> str:
            Get the name of the compression algorithm.

        set_compression_algorithem() -> None:
            Set the compression algorithm.

        open_output_file() -> None:
            Open the output file for writing compressed data.

        close_output_file(self) -> None:
            Close the output file.

        read_file() -> bytes:
            Read data from a file.

        write_file() -> None:
            Write data to a file.

        compress_data_to_file() -> None:
            Compress data and write it to the output file.

        get_decompressed_data() -> Tuple[bytes, int]:
            Get decompressed data from compressed data.

        define_compression_algorithem() -> None:
            Define the compression algorithm based on metadata.

        valid_for_compression() -> bool:
            True if the data is valid for compression, False otherwise.

        write_metadata(self) -> None:
            Write metadata about the compression algorithm to the output file.

        read_metadata() -> Tuple[str, int]:
            Read metadata from compressed data.

        compress() -> None:
            Compress files and directories recursively.

        compress_with_error():
            Handles compression errors and raises exceptions.   

        should_stop() -> bool:
            Check if the compression or decompression process should stop.

        should_read_compressed_file() -> bool:
            Check if a compressed file should be read.

        handle_init_decompression() -> int:
            Handle initialization for decompression.

        get_next_path_from_archive() -> int:
            Get the next path from the compressed archive.

        decompress() -> None:
            Decompress files and directories recursively.

        decompress_files() -> None:
            Decompress multiple files.

        def remove_paths() -> None:
            Removes files specified by a list of file paths.

        remove_from_archive() -> int:
            Remove files from an archive and update the archive.

        update_archive() -> None:
            Update an existing archive with new files.

        check_validation() -> dict:
            Check the validation of archived files and directories.

    """

    def __init__(self, data_compression_algorithem: DataCompression) -> None:
        """Initialize the FilesystemHandler object with a specified
        compression algorithm.

        Args:
            data_compression_algorithem (DataCompression):
            The data compression algorithm instance.
        """
        self._compression_algorithem: DataCompression = \
            data_compression_algorithem
        self._output_file: Optional[BinaryIO] = None
        self._folder_suffix = "/"
        self._bytes_length = 16

    def get_compression_algorithem_name(self) -> str:
        """Get the name of the compression algorithm.

        Returns:
            str: The name of the compression algorithm.
        """
        return self._compression_algorithem.__class__.__name__

    def set_compression_algorithem(
        self, compression_algorithem: DataCompression
    ) -> None:
        """Set the compression algorithm.

        Args:
            compression_algorithem (DataCompression):
            The compression algorithm to set.
        """
        self._compression_algorithem = compression_algorithem

    def open_output_file(self, output_file_path: str) -> None:
        """Open the output file for writing compressed data.

        Args:
            output_file_path (str): The path to the output file.
        """
        self._output_file = open(output_file_path, "ab")

    def close_output_file(self) -> None:
        """Close the output file."""
        if self._output_file is not None:
            self._output_file.close()

    def read_file(self, file: str) -> bytes:
        """Read data from a file.

        Args:
            file (str): The path to the file.

        Returns:
            bytes: The data read from the file.
        """
        with open(file, "rb") as f:
            return f.read()

    def write_file(self, file: str, data: bytes) -> None:
        """Write data to a file.

        Args:
            file (str): The path to the file.
            data (str): The data to write to the file.
        """
        sub_directories = os.path.dirname(file)
        if sub_directories:
            os.makedirs(sub_directories, exist_ok=True)
        if data:
            with open(file, "wb") as f:
                f.write(data)

    def compress_data_to_file(self, data: bytes) -> None:
        """Compress data and write it to the output file.

        Args:
            data (bytes): The data to compress and write.
        """
        compressed_data = self._compression_algorithem.compress_data(
            data=data)
        data_len = len(compressed_data).to_bytes(
            self._bytes_length, byteorder="big"
        )
        if self._output_file:
            self._output_file.write(data_len)
            self._output_file.write(compressed_data)

    def get_decompressed_data(
        self, compressed_data: bytes, index: int = 0
    ) -> Tuple[bytes, int]:
        """Get decompressed data from compressed data.

        Args:
            compressed_data (bytes): The compressed data.
            index (int, optional): The index to start reading from in the
            compressed data. Defaults to 0.

        Returns:
            Tuple[bytes, int]: The decompressed data and the next index
            in the compressed data.
        """
        bytes_len = compressed_data[index : index + self._bytes_length][::-1]
        compressed_len = int.from_bytes(bytes_len, byteorder="little")
        next_index = self._bytes_length + index + compressed_len
        compressed = compressed_data[index + self._bytes_length : next_index]
        decompress_data = self._compression_algorithem.decompress_data(
            compressed_data=compressed
        )

        return decompress_data, next_index

    def define_compression_algorithem(self, algorithem_type: bytes) -> None:
        """Define the compression algorithm based on metadata.

        Args:
            algorithem_type (bytes): The metadata indicating the
            compression algorithm type.
        """

        algo: Optional[DataCompression] = None
        
        # RLE algorithem
        if algorithem_type.startswith(
            CompressionTypes.RLE.value.__name__.encode()
        ):
            rle_len = len(CompressionTypes.RLE.value.__name__)
            bytes_size = int.from_bytes(
                algorithem_type[rle_len:][::-1], byteorder="little"
            )
            algo = CompressionTypes.RLE.value(bytes_size=bytes_size)

        # HUFFMAN algorithem
        elif algorithem_type.startswith(
            CompressionTypes.HUFFMAN.value.__name__.encode()
        ):
            algo = CompressionTypes.HUFFMAN.value()

        # LEMPEL_ZIV algorithem
        elif algorithem_type.startswith(
            CompressionTypes.LZ.value.__name__.encode()
        ):
            algo = CompressionTypes.LZ.value()

        else:
            raise InvalidCompressionAlgorithem(f"Invalid compression format!")

        self.set_compression_algorithem(compression_algorithem=algo)

    def write_metadata(self) -> None:
        """Write metadata about the compression algorithm to the output file.
        """
        algo_metadata = self._compression_algorithem.get_metadata()
        metadata_len = len(algo_metadata).to_bytes(
            self._bytes_length, byteorder="big"
        )
        if self._output_file:
            self._output_file.write(metadata_len)
            self._output_file.write(algo_metadata)

    def read_metadata(
        self, compressed_data: bytes, index: int = 0
    ) -> Tuple[bytes, int]:
        """Read metadata from compressed data.

        Args:
            compressed_data (bytes): The compressed data.
            index (int, optional): The index to start reading from in the
            compressed data. Defaults to 0.

        Returns:
            Tuple[str, int]: The metadata and the next index in the
            compressed data.
        """
        location = compressed_data[index : index + self._bytes_length][::-1]
        metadata_len = int.from_bytes(location, byteorder="little")
        next_index = self._bytes_length + index + metadata_len
        metadata = compressed_data[index + self._bytes_length : next_index]

        return metadata, next_index

    def valid_for_compression(self, data: bytes) -> bool:
        """Checks if the data is valid for compression based on special signs.

        Args:
            data (bytes): The data to be checked for special signs.

        Returns:
            bool: True if the data is valid for compression, False otherwise.
        """
        special_signs = self._compression_algorithem.get_special_signs()
        for sign in special_signs:
            if sign in data:
                return False

        return True

    def compress_with_error(
            self, should_remove_output: bool, exception_type: Exception) -> None:
        """
        Handles compression errors and raises exceptions.

        Parameters:
        - should_remove_output (bool): Whether to remove the output file 
        if an error occurs.
        - exception_type (Exception): The type of exception to raise 
        (default: Exception).
        - aborted_msg (str): The error message to use if no message
          is provided (default: '').
        - full_dir_path (str): The full directory path related to the 
        compression operation (default: '').

        Raises:
        InvalidDataForCompressionAlgorithem: If the compression operation 
        fails.
        Exception: If a specific exception type is provided and the 
        operation fails.

        Notes:
        - If should_remove_output is True, the output file will be 
        removed if an error occurs.
        - If aborted_msg is not provided, a default error message 
        will be generated.
        - If exception_type is provided, that specific exception will 
        be raised; otherwise, a generic Exception will be raised.
        """
        self.close_output_file()
        if should_remove_output and self._output_file:
            os.remove(self._output_file.name)

        raise exception_type

    def compress(
        self,
        directories: List[str],
        subfolder: str = "",
        ignore_folders: List[str] = [],
        ignore_files: List[str] = [],
        ignore_extensions: List[str] = [],
        init_compression: bool = False,
        remove_output: bool = True,
    ) -> None:
        """Compress files and directories recursively.

        Args:
            directories (list): List of directories to compress.
            subfolder (str, optional): Subfolder path. Defaults to ''.
            ignore_folders (list, optional): List of folders to ignore.
            Defaults to [].
            ignore_files (list, optional): List of files to ignore.
            Defaults to [].
            ignore_extensions (list, optional): List of file extensions
            to ignore. Defaults to [].
            init_compression (bool, optional): Whether it's the initial
            compression operation. Defaults to False.
            remove_output (bool, optional): Whether an error occured,
            option to remove the output path. Defaults to True.
        """
        if init_compression:
            self.write_metadata()

        ignore_folders = [os.path.normpath(path) for path in ignore_folders]
        # pass on each given directory
        for dir in directories:
            full_dir_path = os.path.join(subfolder, dir)
            # if it is directory to folder
            if os.path.isdir(full_dir_path):

                if os.path.normpath(full_dir_path) not in ignore_folders:

                    files_in_folder = os.listdir(full_dir_path)
                    # if it is an empty folder, compress full folder path name
                    if len(files_in_folder) == 0:
                        full_dir_path += self._folder_suffix
                        self.compress_data_to_file(
                            data=full_dir_path.encode())

                    # compress recursive the files which inside the directory to current folder
                    self.compress(
                        directories=files_in_folder,
                        subfolder=full_dir_path,
                        ignore_files=ignore_files,
                        ignore_extensions=ignore_extensions,
                        ignore_folders=ignore_folders,
                    )

            # if it is directory to file
            elif os.path.isfile(full_dir_path):

                if (
                    full_dir_path not in ignore_files
                    and not full_dir_path.endswith(tuple(ignore_extensions))
                ):
                    # read data from current file
                    full_file_data = self.read_file(file=full_dir_path)
                    file_path = full_dir_path.encode()

                    exception_type = self.get_invalid_data_exception(
                                full_dir_path=full_dir_path)

                    if self.valid_for_compression(
                        data=full_file_data
                    ) and self.valid_for_compression(data=file_path):
                        try: 
                            # compress full file path name
                            self.compress_data_to_file(data=file_path)
                            # compress file data
                            self.compress_data_to_file(data=full_file_data)
                        except Exception:
                            self.compress_with_error(
                            should_remove_output=remove_output,
                            exception_type=exception_type
                        )
                    else: 
                        self.compress_with_error(
                            should_remove_output=remove_output,
                            exception_type=exception_type
                        ) 

            else:
                aborted_msg = f"Error - {full_dir_path} does not exist."
                self.compress_with_error(
                    should_remove_output=remove_output, 
                    exception_type=MissingInputPath(aborted_msg),
                    )
                
    def get_invalid_data_exception(self, full_dir_path: str) -> Exception:
        """Returns invalid data for compression exception according
        to the full dir path.

        Args:
            full_dir_path (str): Path to the compressed file.

        Returns:
            Exception: invalid data for compression exception.
        """
        algo_name = self.get_compression_algorithem_name()
        aborted_msg = f"Could not compress {full_dir_path} "
        aborted_msg += f"using {algo_name}."
        return InvalidDataForCompressionAlgorithem(aborted_msg)

    def should_stop(
        self, compressed_file_path: str = "", compressed_data: bytes = b""
    ) -> bool:
        """Check if the compression or decompression process should stop.

        Args:
            compressed_file_path (str, optional): Path to the compressed file.
            Defaults to ''.
            compressed_data (bytes, optional): Compressed data.
            Defaults to b''.

        Returns:
            bool: True if the process should stop, False otherwise.
        """

        # if compressed_data is empty & compressed file path was not inserted
        if compressed_data == b"" and not compressed_file_path:
            return True
        return False

    def should_read_compressed_file(
        self, compressed_file_path: str = "", compressed_data: bytes = b""
    ) -> bool:
        """Check if a compressed file should be read.

        Args:
            compressed_file_path (str, optional): Path to the compressed file.
            Defaults to ''.
            compressed_data (bytes, optional): Compressed data.
            Defaults to b''.

        Returns:
            bool: True if the compressed file should be read, False otherwise.
        """
        # if compressed_data is empty and compressed file path was inserted
        if compressed_data == b"" and compressed_file_path:
            return True
        return False

    def handle_init_decompression(
        self,
        compressed_data: bytes,
        view_mode: bool = False,
        debug_mode: bool = False,
        compressed_file_path: str = "",
    ) -> int:
        """Handle initialization for decompression.

        Args:
            compressed_data: The compressed data.
            view_mode (bool, optional): Whether to display the decompression
            mode. Defaults to False.
            debug_mode (bool, optional): Whether to enable debug mode.
            Defaults to False.
            compressed_file_path (str, optional): Path to the compressed file.
            Defaults to ''.

        Returns:
            int: The next index in the compressed data.
        """
        # get full file path from compressed data
        algorithem_type, next_index = self.read_metadata(
            compressed_data=compressed_data
        )
        self.define_compression_algorithem(algorithem_type=algorithem_type)
        if view_mode and not debug_mode:
            algo_name = self.get_compression_algorithem_name()
            msg = f"{compressed_file_path} - [{algo_name}] "
            msg += "compressed file contains:"
            print(msg)

        return next_index

    def get_next_path_from_archive(
        self,
        compressed_data: bytes,
        view_mode: bool = False,
        debug_mode: bool = True,
        index: int = 0,
        output_path: str = "",
    ) -> Tuple[int, bytes]:
        """Get the next path from the compressed archive.

        Args:
            compressed_data: The compressed data.
            view_mode (bool, optional): Whether to display the
            decompression mode. Defaults to False.
            debug_mode (bool, optional): Whether to enable debug mode.
            Defaults to True.
            index (int, optional): The index to start reading from in
            the compressed data. Defaults to 0.
            Defaults to False.
            output_path (str, optional): The output path for decompressed
            files. Defaults to "".

        Returns:
            int: The next index in the compressed data.
        """
        # get full file path from compressed data
        path, next_index = self.get_decompressed_data(
            compressed_data=compressed_data, index=index
        )

        # if path presents a folder
        if path.decode().endswith(self._folder_suffix):
            file_data = b""

        # if path presents a file
        else:
            # get original file data from compressed data
            file_data, next_index = self.get_decompressed_data(
                compressed_data=compressed_data, index=next_index
            )

        file_name = path.decode()
        if file_name and view_mode and not debug_mode:
            print(f"{file_name} - size [{len(file_data)}]")
        elif file_name and not debug_mode:
            file_path = os.path.join(output_path, file_name)
            self.write_file(file=file_path, data=file_data)
            print(f"Done extract & write {file_path}.")

        return next_index, path
        

    def decompress(
        self,
        compressed_file_path: str = "",
        compressed_data: bytes = b"",
        subfolder: str = "",
        view_mode: bool = False,
        debug_mode: bool = False,
        init_decompression: bool = False,
        output_path: str = "",
        internal_paths: List[str] = []
    ) -> None:
        """Decompress files and directories recursively.

        Args:
            compressed_file_path (str, optional): Path to the
            compressed file. Defaults to ''.
            compressed_data (bytes, optional): Compressed data.
            Defaults to b''.
            subfolder (str, optional): Subfolder path. Defaults to ''.
            view_mode (bool, optional): Whether to display the
            decompression mode. Defaults to False.
            debug_mode (bool, optional): Whether to enable debug mode.
            Defaults to False.
            init_decompression (bool, optional): Whether it's the initial
            decompression operation. Defaults to False.
            output_path (str, optional): The output path for decompressed
            files. Defaults to "".
        """
        if self.should_stop(
            compressed_file_path=compressed_file_path,
            compressed_data=compressed_data,
        ):
            return

        if self.should_read_compressed_file(
            compressed_file_path=compressed_file_path,
            compressed_data=compressed_data,
        ):
            compressed_data = self.read_file(file=compressed_file_path)

        if init_decompression:
            next_index = self.handle_init_decompression(
                compressed_data=compressed_data,
                view_mode=view_mode,
                debug_mode=debug_mode,
                compressed_file_path=compressed_file_path,
            )
        else:
            next_index = 0

        next_index, file_path = self.get_next_path_from_archive(
            compressed_data=compressed_data,
            view_mode=view_mode,
            debug_mode=debug_mode,
            index=next_index,
            output_path=output_path,
        )

        # save data about all files and dirs inside archive file        
        internal_paths.append(os.path.join(output_path, file_path.decode()))

        # decompress the original data recursivlly from the
        # rest of the compressed data
        self.decompress(
            compressed_data=compressed_data[next_index:],
            subfolder=subfolder,
            view_mode=view_mode,
            debug_mode=debug_mode,
            output_path=output_path,
            internal_paths=internal_paths
        )

    def decompress_files(
        self,
        directories: List[str],
        output_path: str = "",
        view_mode: bool = False,
        debug_mode: bool = False,
    ) -> Dict[str, str]:
        """Decompress multiple files.

        Args:
            directories (list): List of compressed files to decompress.
            output_path (str, optional): The output path for decompressed
            files. Defaults to ''.
            view_mode (bool, optional): Whether to display the decompression
            mode. Defaults to False.
            debug_mode (bool, optional): Whether to enable debug mode.

        Returns:
            dict: A dictionary containing non-valid archive paths
            and their corresponding error messages.
        """
        non_valid_archive_paths = {}
        for compressed_file in directories:
            internal_paths: List[str] = []
            try:
                self.decompress(
                    compressed_file_path=compressed_file,
                    view_mode=view_mode,
                    init_decompression=True,
                    output_path=output_path,
                    debug_mode=debug_mode,
                    internal_paths=internal_paths
                )
            except Exception as e:
                non_valid_archive_paths[compressed_file] = (
                    f"raise {type(e).__name__}({e})"
                )
                # remove all files of an invalid archive path
                self.remove_paths(paths=internal_paths)

        return non_valid_archive_paths
    
    def remove_paths(self, paths: List[str]) -> None:
        """
        Removes files specified by a list of file paths.

        Parameters:
        - paths (List[str]): A list of file paths to be removed.

        Raises:
        - FileNotFoundError: If a specified path does not exist.
        - PermissionError: If permission is denied to remove a file

        Notes:
        - If a specified path does not exist, a FileNotFoundError is raised, 
        but the removal process continues for other paths.
        - If permission is denied to remove a file, a PermissionError is 
        raised, but the removal process continues for other paths.
        - If no exceptions occur during the removal process, a success 
        message is printed for each file removed.
        - If an exception occurs during the removal process, a message 
        is printed indicating which file encountered the exception, 
        and the removal process continues for other paths.
        """
        for path in paths:
            try:
                # ensures that only files are removed, not folders, 
                # as removing folders can be dangerous and lead to data loss.
                if os.path.isfile(path):
                    os.remove(path)
                    print(f'Done removing {path} because exception occurred.')
            except (FileNotFoundError, PermissionError) as e:
                print(f'Failed to remove {path} - {type(e).__name__}: {e}')

    def remove_from_archive(
            self, input_paths: List[str], 
            archive_path: str) -> Union[int, str, bool, Dict[str,str], None]:
        """Remove files from an archive and update the archive.

        Args:
            input_paths (list): List of paths to remove from the archive.
            archive_path (str): Path to the archive.

        Returns:
            int | None: Number of files removed from the archive.
        """
        try:
            count_files_removes = 0
            update_compressed_data = bytearray()
            compressed_data = self.read_file(file=archive_path)

            next_index = self.handle_init_decompression(
                compressed_data=compressed_data
            )
            update_compressed_data.extend(compressed_data[0:next_index])

            i = next_index
            while i < len(compressed_data):

                next_index, file_path = self.get_next_path_from_archive(
                    compressed_data=compressed_data,
                    index=next_index,
                )
                if file_path.decode().startswith(tuple(input_paths)):
                    count_files_removes += 1
                else:
                    update_compressed_data.extend(
                        compressed_data[i:next_index]
                    )

                i = next_index
        except Exception as e:
            return None

        self.write_file(file=archive_path, data=bytes(update_compressed_data))
        return count_files_removes

    def update_archive(self, input_paths: List[str], 
                       archive_path: str) -> bool:
        """Update an existing archive with new files.

        Args:
            input_paths (list): List of paths to add to the archive.
            archive_path (str): Path to the archive.

        Returns:
            bool: True if the archive path is valid, False otherwise.
        """
        result = self.remove_from_archive(
            input_paths=input_paths, archive_path=archive_path
        )
        if result == None:
            return False
        else:
            self.compress(directories=input_paths, remove_output=False)
            return True

    def check_validation(self, archive_paths: List[str]) -> Dict[str, str]:
        """Check the validation of archived files and directories.

        Args:
            archive_paths (list): List of paths to archived
            files and directories.

        Returns:
            dict: A dictionary containing non-valid archive paths
            and their corresponding error messages.
        """

        return self.decompress_files(
            directories=archive_paths, debug_mode=True
        )
