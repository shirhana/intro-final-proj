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

    def get_folder_size(self, path):
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

    def show(self):
        self.stop_clock()
        input_paths_size = self.get_total_size_of_directories(directories=self._input_paths)
        
        if self._action_type == ActionTypes.COMPRESS.value:
            outpath_size = self.get_total_size_of_directories(directories=[self._output_path])
            print(f"Compressed Size: {print_colored(text=outpath_size,  color=self._clrs.yellow)} bytes")
            print(f'Delta Size --> {print_colored(int(input_paths_size - outpath_size), color=self._clrs.cyan)}')
            ratio = int(input_paths_size/outpath_size)
            ratio_color = print_colored(text=f"{ratio}%",  color=self._clrs.green)
            print(f"Compressed Ratio: {ratio_color}")
        elif self._action_type == ActionTypes.ADD_TO_ARCHIVE.value:
            print(f'Added Files Size --> {print_colored(input_paths_size, color=self._clrs.cyan)}')

        self.display_elapsed_time()
