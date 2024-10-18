import os
import subprocess

class OCRMyPDF():
    def __init__(self):
        pass

# Need to handle decrypting PDFs, or signed PDFs
# qpdf --decrypt --password='abc123' input.pdf no_password.pdf
    def ocr_directory(self, directory):
        if not os.path.isdir(directory):
            print("Error: directory does not exist.")
            return

        # Iterate through every file in the directory
        MAX_LENGTH = 1000 # Set your desired maximum length

        output = ""
        for filename in os.listdir(directory):
            if filename.endswith(".pdf"):
                new_content = "Output for " + filename + ":\n"
                new_content += self.ocr_file(os.path.join(directory, filename)).decode("utf-8")
                
                # Check if adding new_content will exceed the MAX_LENGTH
                if len(output) + len(new_content) > MAX_LENGTH:
                    # Calculate how much of new_content we can fit
                    available_space = MAX_LENGTH - len(output)
                    output += new_content[:available_space]  # Truncate new_content to fit
                    break  # Stop processing further files, as output is now at its max
                else:
                    output += new_content

        print("Finished processing all PDFs.")
        print(output)
        return "Finished"

    def ocr_file(self, file_path):
        if not os.path.isfile(file_path):
            print("Error: file does not exist.")
            return

        # Extract name without extension
        base_name = os.path.splitext(file_path)[0]
        
        # Formulate the command
        print("file_path", file_path)
        print("base_name", base_name)
        cmd = [
            'ocrmypdf', 
            '--sidecar', f'{base_name}.txt', 
            '--clean', 
            '--deskew',
            '--force-ocr',
            '--output-type=none', 
            file_path, 
            '-'
        ]
        
        # Run the command and suppress its output
        output = ""
        with open(os.devnull, 'w') as fnull:
            output = subprocess.run(cmd, capture_output=True)

        return output.stdout
