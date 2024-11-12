#!/bin/bash
set -e

# Create directories if they don't exist
mkdir -p certs

# Generate self-signed certificate for Prosody
openssl req -new -x509 -days 365 -nodes \
    -out certs/localhost.crt \
    -keyout certs/localhost.key \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=prosody"

# Set permissions
chmod 644 certs/localhost.crt
chmod 600 certs/localhost.key

echo "Certificates generated successfully"
