import os
from langchain.agents import Tool
import subprocess

class NexusNmap():
    def tool_factory(self):
        return [Tool(
            name="nmap",
            func=self.scan,
            description="""
            accepts a cidr like 192.168.69.0/24
            useful for running a network mapper nmap scan on a given cidr
            nmap scanner
            """
        )]

    def scan(self, cidr):
        nmap_command = "nmap -sT --top-ports 1000 -T4 -A -v {cidr}".format(cidr=cidr)
        result = subprocess.run(nmap_command, shell=True, stdout=subprocess.PIPE, text=True)

        for line in result.stdout.split("\n"):
            print(line)
        
        stdout_output = result.stdout

        return stdout_output
    
class NexusPing():
    def tool_factory(self):
        return [Tool(
            name="ping",
            func=self.ping,
            description="""
            accepts an IP or domain name
            used for pinging a server to check latency and packet loss
            uses icmp protocol
            """
        )]
    
    def ping(self, pingable):
        ping_command = "ping -4 -c 3 {pingable}".format(pingable=pingable)
        result = subprocess.run(ping_command, shell=True, stdout=subprocess.PIPE, text=True)

        stdout_output = result.stdout

        return stdout_output
    
class NexusTshark():
    def tool_factory(self):
        return [Tool(
            name="tshark",
            func=self.tshark,
            description="""
            accepts no arguments
            runs tshark for 1 second
            used for packet capture samples
            """
        )]
    def tshark(self, args):
        command = """
        tshark -a duration:1 -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport -e icmp.type -e icmp.code -E separator=, | head -n 10
        """
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

        stdout_output = result.stdout

        return stdout_output

class NexusDigIPtoDomain():
    def tool_factory(self):
        return [Tool(
            name="dig_ip_to_domain",
            func=self.dig_ip_to_domain,
            description="""
            accepts an IP
            used for looking up the domain name of an IP address with dig
            """
        )]

    def dig_ip_to_domain(self, ip):
        command = "dig -x {ip}".format(ip=ip)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

        stdout_output = result.stdout
        return stdout_output

class NexusDigDomainToIP():
    def tool_factory(self):
        return [Tool(
            name="dig_domain_to_ip",
            func=self.dig_domain_to_ip,
            description="""
            accepts a domain name
            used for looking up the IP address of a domain name with dig
            """
        )]

    def dig_domain_to_ip(self, domain):
        command = "dig {domain}".format(domain=domain)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

        stdout_output = result.stdout
        return stdout_output