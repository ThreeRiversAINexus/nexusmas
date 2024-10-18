import subprocess
from typing import Optional
from langchain.tools import StructuredTool
import os
from shared.tools.shared import NexusTool
class NexusGrepFilesystem(NexusTool):
    def __init__(self, *args, **kwargs):
        self.pattern = kwargs.pop("pattern", None)
        super().__init__(tool_function="grep_all_files")

    def grep_all_files(self, pattern: str) -> str:
        """Dangerously greps the contents of the entire filesystem given a regex pattern. Useful for finding ALL files that contain a certain string."""
        cwd = os.getcwd()
        cwd = cwd + "/nexus-multi-agent-system"
        if not pattern or not cwd:
            raise ValueError("Both pattern and directory should be specified.")
        result = subprocess.run(["grep", "-ri", pattern, cwd], capture_output=True, text=True)
        output = f"{result.stdout}"
        if output == "":
            output = "No matches found."
        return output

class NexusGrepFile(NexusTool):
    def __init__(self, *args, **kwargs):
        super().__init__(tool_function="grep_specific_file")

    def grep_specific_file(self, pattern: str, file: str) -> str:
        """
        Search a specific file for a regex pattern. 
        Parameters:
        - pattern: The regex to search for.
        - file: Full path to the target file.
        Returns up to 10 matches with 3 lines of context each.
        """
        
        # Check if the file exists
        if not os.path.isfile(file):
            return "The specified file does not exist. Specify a full real path."
        
        if pattern == "":
            pattern = ".*"
        
        if not pattern or not file:
            return "Invalid arguments. Specify a regex pattern and a full real path to the file to search."
        
        # Using --max-count to limit the grep output to 30 matched lines
        result = subprocess.run(["grep", "-ri", "-C3", "--max-count=10", pattern, file], capture_output=True, text=True)
        output = f"{result.stdout}"
        
        if output == "":
            output = "No matches found."
        return output
