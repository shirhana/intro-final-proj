import os
import time
from utility import print_colored, Colors
from action_types import ActionTypes


class DisplayActionInfo():

    def __init__(self, action_type, input_paths, output_path) -> None:
        self._action_type = action_type
        self._input_paths = input_paths
        self._output_path = output_path
        self._start_clock = None
        self._elapsed_time = None
        self._clrs = Colors()

        self.start_clock()

    def start_clock(self):
        self._start_clock = time.time()

    def stop_clock(self):
        self._elapsed_time = float(time.time() - self._start_clock)

    @staticmethod
    def get_folder_size(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def get_total_size_of_directories(self, directories: list):
        total_size = 0
        for path in directories:
            if os.path.isdir(path):
                total_size += self.get_folder_size(path=path)
            elif os.path.isfile(path):
                total_size += int(os.path.getsize(path))

        return total_size
    
    def display_elapsed_time(self):
        clrs = Colors()
        time_str = f"{self._elapsed_time} seconds"
        print(f'Time of {self._action_type}  -->{print_colored(text=time_str,  color=clrs.purple)}')

    def show(self, result: str, compression_algorithem: str):
        self.stop_clock()
        try:
            input_paths_size = self.get_total_size_of_directories(directories=self._input_paths)
        except FileNotFoundError:
            pass
        success = True

        if self._action_type == ActionTypes.COMPRESS.value:
            print(print_colored(f'Compress With {compression_algorithem} Algorithem Info:', color=self._clrs.cyan))
            outpath_size = self.get_total_size_of_directories(directories=[self._output_path])
            print(f"Compressed Size: {print_colored(text=outpath_size,  color=self._clrs.yellow)} bytes")
            print(f'Delta Size --> {print_colored(int(input_paths_size - outpath_size), color=self._clrs.cyan)}')
            try:
                ratio = int(input_paths_size/outpath_size)
                ratio_color = print_colored(text=f"{ratio}%",  color=self._clrs.green)
                print(f"Compressed Ratio: {ratio_color}")
            except ZeroDivisionError:
                pass

        elif self._action_type == ActionTypes.ADD_TO_ARCHIVE.value:
            print(f'Added Files Size --> {print_colored(input_paths_size, color=self._clrs.cyan)}')

        elif self._action_type == ActionTypes.REMOVE_FROM_ARCHIVE.value:
            if result == 0:
                print(print_colored(text=f'Cannot remove {self._input_paths}!\nThose files or directories do not exist inside {self._output_path}.',  color=self._clrs.red))
                success = False
            else:
                print(print_colored(text=f'{result} files were successfully removed from {self._output_path} archive file.',  color=self._clrs.green))
                
        if success:
            self.display_elapsed_time()

    def alert(self, error_msg):
        if error_msg == {}:
            if self._action_type == ActionTypes.CHECK_VALIDATION.value:
                print(print_colored(text=f'{self._input_paths} PASSED VALIDATION!',  color=self._clrs.green))
            return True
        elif isinstance(error_msg, dict):
            for ivalid_input_path, error_type in error_msg.items():

                print(print_colored(text=f'* {ivalid_input_path} is NOT VALID COMPRESS FILE!\n{error_type}\n',  color=self._clrs.red))
            return False
        return True
