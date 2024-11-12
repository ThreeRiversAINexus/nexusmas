#!/bin/bash

# Wait for Prosody to start
sleep 5

# Create the test user if it doesn't exist
prosodyctl register nexusmas localhost nexusmas

# Keep container running
exec "$@"
