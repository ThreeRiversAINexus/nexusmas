class AgentLogin:
    def __init__(self, config_file=None, passphrase=None):
        self.config_file = config_file
        self.passphrase = passphrase
        self.gpg = gnupg.GPG()

    def read_config(self):
        with open(self.config_file, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.gpg.decrypt(encrypted_data, passphrase=self.passphrase)

        if not decrypted_data.ok:
            raise ValueError("Failed to decrypt configuration file")

        config_data = json.loads(str(decrypted_data))
        return config_data

    def write_config(self, config_data=None):
        if config_data is None:
            config_data = self.config_data

        json_data = json.dumps(config_data)
        encrypted_data = self.gpg.encrypt(json_data, recipients=None, passphrase=self.passphrase, symmetric=True)

        if not encrypted_data.ok:
            raise ValueError("Failed to encrypt configuration data")

        with open(self.config_file, 'wb') as f:
            f.write(str(encrypted_data).encode())