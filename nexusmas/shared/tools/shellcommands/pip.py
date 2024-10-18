import pexpect

class Pip():
    def __init__(self):
        pass

    def upgrade(self):
        # Install or Upgrade the required packages
        # using pip command
        command = 'pip install -U -r requirements.txt'

        # Use pexpect library to run the command
        # and wait for the command to complete
        pexpect.run(command)
