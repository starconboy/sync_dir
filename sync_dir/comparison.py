from filecmp import dircmp
import filecmp
import shutil
import os

class difference:
    def __init__(self, source: str, destination: str, filename: str, copy: bool) -> None:
        self.copy = copy
        if self.copy:
            self.source = os.path.join(source, filename)
        else:
            self.source = os.path.join(destination, filename)
        self.destination = os.path.join(destination, filename)
        self.is_dir = os.path.isdir(self.source)
        if self.is_dir:
            self.size = 0
        else:
            self.size = os.path.getsize(self.source)

    def __str__(self) -> str:
        if self.copy:
            if self.is_dir:
                return "Create Folder " + self.destination
            else:
                return "Copy " + self.source + " -> " + self.destination
        return "Delete " + self.source
    


class directory_compare:
    def __init__(self) -> None:
        self.delete_differences = []
        self.copy_differences = []
        self.files_to_move_size = 0
        self.files_to_delete_size = 0

    def get_ending_diskspace_requirement(self) -> int:
        return self.files_to_move_size - self.files_to_delete_size
    
    def get_runtime_diskspace_requirement(self) -> int:
        return self.files_to_move_size

    def _add_differences(self,source, destination, list, copy: bool) -> None:
        for l in list:
            self._add_difference(difference(source, destination, l, copy), copy)

    def _add_difference(self, d: difference, copy: bool) -> None:
        if copy:
            self.copy_differences.append(d)
        else:
            self.delete_differences.append(d)

    def search_differences(self, source, destination, recursive:bool=True) -> None:
        if os.path.exists(source) and os.path.exists(destination):
            comparison = dircmp(source, destination)
            # add files to be copied
            self._add_differences(source, destination, comparison.left_only, True)
            self._add_differences(source, destination, comparison.right_only, False)
            #conduct a more in-depth compare on common files...looking for differences
            for f in comparison.common_files:
                if filecmp.cmp(os.path.join(source, f), os.path.join(destination, f)) == False:
                    self.differences.append(difference(source, destination, f, True))
        elif os.path.exists(source):
            # all items found here are additions
            self._add_differences(source, destination, os.listdir(source), True)
        else:
            # all items found here are deletions
            self._add_differences(source, destination, os.listdir(destination), False)

        if recursive:
            for folder in self.get_distinct_folder_list(source, destination):
                self.search_differences(os.path.join(source, folder), os.path.join(destination, folder), True)

    def get_distinct_folder_list(self, source, destination) -> [str]:
            folder = []
            if os.path.exists(source):
                folder += [ name for name in os.listdir(source) if os.path.isdir(os.path.join(source, name)) ]
            if os.path.exists(destination):
                folder += [ name for name in os.listdir(destination) if os.path.isdir(os.path.join(destination, name)) ]
            return list(set(folder))
        
    def report(self):
        self.files_to_move_size = 0
        self.files_to_delete_size = 0
        self._print_differences(self.copy_differences)
        self._print_differences(self.delete_differences)
        print("File size to be moved: " + str(self.files_to_move_size))
        print("Files to delete size: " + str(self.files_to_delete_size))

    def _print_differences(self, differences) -> None:
        for diff in differences:
            print(diff)
            if diff.copy:
                self.files_to_move_size += diff.size
            else:
                self.files_to_delete_size += diff.size

    def syncronize_directories(self):
        print("sycronization starting...")
        # delete files and folders first
        while len(self.delete_differences) > 0:
            item = self.delete_differences.pop()
            if item.is_dir:
                print("delete " + item.destination)
                os.rmdir(item.destination)
                print("deleted")
            else:
                print("deleting " + item.destination)
                os.remove(item.destination)
                print("deleted")

        # create folders and copy files
        while len(self.copy_differences) > 0:
            item = self.copy_differences.pop(0)
            if item.is_dir:
                print("creating directory " + item.destination)
                os.mkdir(item.destination)
            else:
                print("coping " + item.source)
                shutil.copy2(item.source, item.destination)
                print("copy " + item.source + " complete")

        # complete
        print("sycronization complete.")
