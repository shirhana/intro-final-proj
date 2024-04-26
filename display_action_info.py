import os
import time
from utility import print_colored, Colors
from action_types import ActionTypes


class DisplayActionInfo:
    """Class for displaying information about actions related to 
    file compression.

    This class provides methods to display information such as 
    elapsed time, compressed file size, added files size,
    removed files count, and alerts for various actions related 
    to file compression and archiving.

    Attributes:
        _action_type (str): The type of action being performed.
        _input_paths (list): List of input paths.
        _output_path (str): Output path for compressed or archived files.
        _start_clock (float): The start time of the action execution.
        _elapsed_time (float): The elapsed time since the start of the 
        action execution.
        _clrs (Colors): Instance of the Colors class for color formatting.

    Methods:
        __init__(self, action_type: str, input_paths: list, output_path: str)
         -> None:
            Initialize the DisplayActionInfo object.
        start_clock(self) -> None:
            Start the clock to measure execution time.
        stop_clock(self) -> None:
            Stop the clock and calculate elapsed time.
        get_folder_size(path: str) -> int:
            Calculate the size of a folder recursively.
        get_total_size_of_directories(directories: list) -> int:
            Calculate the total size of multiple directories.
        display_elapsed_time(self) -> None:
            Display the elapsed time for the action.
        show_compress_info(compression_algorithem: str, input_paths_size: int) -> None:
            Display compression information.
        show_remove_from_archive_info(result: int) -> None:
            Display information about removing files from the archive.
        show(self, result: str, compression_algorithem: str) -> None:
            Show information related to the action.
        alert(error_msg: dict | str) -> bool:
            Display alerts or error messages.
    """

    def __init__(self, action_type: str, 
                 input_paths: list, output_path: str) -> None:
        """Initialize the DisplayActionInfo object.

        Args:
            action_type (str): The type of action being performed.
            input_paths (list): List of input paths.
            output_path (str): Output path for compressed or archived files.

        """
        self._action_type = action_type
        self._input_paths = input_paths
        self._output_path = output_path
        self._start_clock = None
        self._elapsed_time = None
        self._clrs = Colors()

        self.start_clock()

    def start_clock(self):
        """Start the clock to measure execution time.
        """
        self._start_clock = time.time()

    def stop_clock(self):
        """Stop the clock and calculate elapsed time.
        """
        self._elapsed_time = float(time.time() - self._start_clock)

    @staticmethod
    def get_folder_size(path: str) -> int:
        """Calculate the size of a folder recursively.

        Args:
            path (str): Path to the folder.

        Returns:
            int: Total size of the folder in bytes.

        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def get_total_size_of_directories(self, directories: list) -> int:
        """Calculate the total size of multiple directories.

        Args:
            directories (list): List of directory paths.

        Returns:
            int: Total size of all directories combined in bytes.
        """
        total_size = 0
        for path in directories:
            if os.path.isdir(path):
                total_size += self.get_folder_size(path=path)
            elif os.path.isfile(path):
                total_size += int(os.path.getsize(path))

        return total_size
    
    def display_elapsed_time(self) -> None:
        """Display the elapsed time for the action.
        """
        clrs = Colors()
        time_str = f"{self._elapsed_time} seconds"
        clr_txt = print_colored(text=time_str,  color=clrs.purple)
        print(f'Time of {self._action_type}  --> {clr_txt}')
        
    def show_compress_info(self, compression_algorithem: str, 
                           input_paths_size: int) -> None:
        """Display compression information.

        Args:
            compression_algorithem (str): The compression algorithm used.
            input_paths_size (int): Total size of input paths.

        Prints information about the compression process, including 
        compressed size, delta size, and compressed ratio if applicable.
        """
        print(print_colored(
            f'Compress With {compression_algorithem} Algorithem Info:', 
            color=self._clrs.cyan))
        outpath_size = self.get_total_size_of_directories(
            directories=[self._output_path])
        clr_size = print_colored(text=outpath_size,  color=self._clrs.yellow)
        print(f"Compressed Size: {clr_size} bytes")
        clr_delta_size = print_colored(int(input_paths_size - outpath_size), 
                      color=self._clrs.cyan)
        print(f'Delta Size --> {clr_delta_size}')
        try:
            ratio = int(input_paths_size/outpath_size)
            ratio_color = print_colored(text=f"{ratio}%", 
                                         color=self._clrs.green)
            print(f"Compressed Ratio: {ratio_color}")
        except ZeroDivisionError:
            pass
        
    def show_remove_from_archive_info(self, result: int) -> None:
        """Display information about removing files from the archive.

        Args:
            result (int): Number of files successfully removed 
            (0 if no files removed).

        Returns:
            bool: True if removal was successful, False otherwise.

        Prints information about the removal process, indicating 
        success or failure based on the result.
        """
        if result == None:
            msg = f"Cannot remove {self._input_paths}!\n"
            msg += f"{self._output_path} is NOT VALID COMPRESS FILE!"
            print(print_colored(text=msg,  color=self._clrs.red))
            return False
        
        elif result == 0:
            msg = f"Cannot remove {self._input_paths}!\n"
            msg += f"Those files or directories do not exist "
            msg += f"inside {self._output_path}."
            print(print_colored(text=msg,  color=self._clrs.red))
            return False
        else:
            msg = f"{result} files were successfully removed from "
            msg += f"{self._output_path} archive file."
            print(print_colored(text=msg,  color=self._clrs.green))
            return True
        
    def show_update_archive_info(self, result: bool) -> None:
        """Display information about updating files in archive.

        Args:
            result (bool): indicates when the updating was succeeded.

        Returns:
            bool: True if updation was successful, False otherwise.

        Prints information about the updation process, indicating 
        success or failure based on the result.
        """
        if result == False:
            msg = f"Cannot handle with {self._input_paths}!\n"
            msg += f"{self._output_path} is NOT VALID COMPRESS FILE!"
            print(print_colored(text=msg,  color=self._clrs.red))

        return result
                
    def show(self, result: str | bool, compression_algorithem: str) -> None:
        """Show information related to the action.

        Args:
            result (str|bool): Result or output of the action.
            compression_algorithm (str): Name of the compression 
            algorithm used.
        """
        self.stop_clock()
        try:
            input_paths_size = self.get_total_size_of_directories(
                directories=self._input_paths)
        except FileNotFoundError:
            pass
        success = True

        if self._action_type == ActionTypes.COMPRESS.value:
            self.show_compress_info(
                compression_algorithem=compression_algorithem,
                input_paths_size=input_paths_size)            

        elif self._action_type == ActionTypes.REMOVE_FROM_ARCHIVE.value:
            success = self.show_remove_from_archive_info(result=result)

        elif self._action_type == ActionTypes.UPDATE_ARCHIVE.value or \
         self._action_type == ActionTypes.ADD_TO_ARCHIVE.value:
            success = self.show_update_archive_info(result=result)

        if success:
            self.display_elapsed_time()

    def alert(self, error_msg: dict | str) -> bool:
        """Display alerts or error messages.

        Args:
            error_msg (dict or str): Error message or dictionary 
            of invalid paths and error types.

        Returns:
            bool: True if no errors or alerts, False otherwise.
        """
        if error_msg == {}:
            if self._action_type == ActionTypes.CHECK_VALIDATION.value:
                print(print_colored(
                    text=f'{self._input_paths} PASSED VALIDATION!',  
                    color=self._clrs.green))
            return True
        elif isinstance(error_msg, dict):
            for ivalid_input_path, error_type in error_msg.items():
                print(print_colored(
                    text=f'* {ivalid_input_path} is NOT VALID COMPRESS FILE!', 
                    color=self._clrs.red))
                print(print_colored(text=error_type, color=self._clrs.red))
            return False
        return True
