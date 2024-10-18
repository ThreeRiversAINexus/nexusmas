import subprocess
from langchain.tools import StructuredTool
import os
from shared.tools.shared import NexusTool

class NexusFileFind(NexusTool):
    def __init__(self):
        self.tool_function = "find_files"
        super().__init__(self.tool_function)

    def find_files(self, glob: str, directory: str) -> str:
        """
        Input: a glob for a file like '*.txt' or '*Nexus*' and a directory to search, defaults to the current directory.
        Searches for filenames recursively.
        Useful for finding full paths to files.
        Returns full file paths to the first 30 files that match the glob.
        """

        # directory = os.getenv("HOME")
        # directory = os.getcwd()
        if not directory:
            directory = os.getcwd()
        if not glob or not directory:
            raise ValueError("Both glob and directory should be specified.")

        print(directory)
        search_glob = f"{glob}"
        # Step 1: Run the find command.
        find_command = ["find", directory, "-name", search_glob, "-type", "f"]
        find_result = subprocess.Popen(find_command, stdout=subprocess.PIPE)

        # Step 2: Pipe the find command's output to head.
        head_command = ["head", "-n", "10"]
        result = subprocess.run(head_command, stdin=find_result.stdout, capture_output=True, text=True)

        # Ensure the first command is terminated after piping its output.
        find_result.stdout.close()
        from pprint import pprint
        pprint("result.stdout: " + result.stdout)
        pprint("result.stderr: " + result.stderr)
        if result.stdout == "":
            return "No files found."
        return f"{result.stdout}\n"