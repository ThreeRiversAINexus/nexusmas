import subprocess
import pexpect
import aioxmpp

class AgentManager:
    def __init__(self, hostname='prosody.example.com'):
        self.hostname = hostname

    def create_user(self, jid, password):
        from pprint import pprint
        pprint(jid + " " + password)
        jid += "@" + self.hostname

        child = pexpect.spawn('prosodyctl adduser ' + jid)

        # Wait for the password prompt.
        i = child.expect(['Enter new password:', pexpect.EOF, pexpect.TIMEOUT])

        if i == 0:  # We got the expected password prompt
            child.sendline(password)
            i = child.expect(['Retype new password:', pexpect.EOF, pexpect.TIMEOUT])
            if i == 0:  # We got the expected retype password prompt
                child.sendline(password)
            else:
                raise RuntimeError("Unexpected response when retyping password")
        else:
            raise RuntimeError("Unexpected response when entering password")

        child.close()
        if child.exitstatus != 0:
            raise RuntimeError(f"Failed to create user: {child.before.decode('utf-8')}")

    async def send_iq_request(self, iq_content_file, jid, password):
        with open(iq_content_file, 'r') as file:
            iq_content = file.read()

        client = aioxmpp.Client(
            aioxmpp.JID.fromstr(jid),
            aioxmpp.make_security_layer(password, no_verify=True)
        )

        iq = aioxmpp.IQ(
            type_=aioxmpp.IQType.SET,
            payload=iq_content
        )

        try:
            async with client.connected() as stream:
                response = await stream.send(iq)
                return response
        except Exception as e:
            raise RuntimeError(f"Failed to send IQ request: {str(e)}")