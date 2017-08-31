#!/usr/bin/python

import socket
from ipaddress import ip_address, ip_network
class Address:

    # <summary>
    # Constructor for Address object
    # </summary>
    # <param name="address" type="string">
    # The IP/FQDN associated with the object
    # </param>
    # <param name="subnet" type="string">
    # The subnet of which it is a member
    # </param>
    # <param name="error_callback" type="function">
    # The callback function in the event of errors
    # </param>
    def __init__(self, IP, subnet, error_callback, FQDN=None):
        self.error_callback = error_callback

        if not Address.isValidSubnet(subnet):
            self.error_callback("Subnet '{}' is not valid! Could not create Address object".format(subnet), False)
            raise ValueError
        self.__subnet = subnet

        if not Address.isValidIPv4(IP) or not Address.isMemberOfSubnet(IP, self.__subnet):
            self.error_callback("IP '{}' is not valid! Could not create Address object.".format(IP), False)
            raise ValueError
        self.__IP = IP

        if FQDN and not Address.isValidFQDN(FQDN):
            self.error_callback("FQDN {} is not valid! Could not create Address object".format(IP), False)
        self.__FQDN = FQDN

    # <summary>
    # Accessor for IP
    # </summary>
    def IP(self):
        return self.__IP

    # <summary>
    # Accessor for subnet
    # </summary>
    def subnet(self):
        return self.__subnet

    # <summary>
    # accessor for FQDN
    # </summary>
    def FQDN(self):
        return self.__FQDN

    # <summary>
    # Verifies the address provided is in fact a valid ipv4 or fqdn
    # </summary>
    # <param name="address" type="string">
    # Address to validate
    # </param>
    @staticmethod
    def validate(address):
        return (Address.isValidIPv4(address) or Address.isValidFQDN(address))

    # <summary>
    # Verifies that the provided string is a valid IPV4 address.
    # Returns a Boolean value
    # </summary>
    # <param name="address" type="string">
    # IP address in string format to be verified
    # </param>
    @staticmethod
    def isValidIPv4(address):
        try:
            ip_address(unicode(address))
            return True
        except Exception, e:
            return False

    # <summary>
    # Verifies that the provided FQDN is valid
    # </summary>
    # <param name="address" type="string">
    # FQDN to be verified
    # </param>
    @staticmethod
    def isValidFQDN(address):
        if address.split(".").count < 3:
            return False
        return True

    @staticmethod
    def isMemberOfSubnet(address, subnet):
        return ip_address(unicode(address)) in ip_network(unicode(subnet))

    @staticmethod 
    def isValidSubnet(subnet):
        subnet_split = subnet.split('/')
        return (Address.isValidIPv4(subnet_split[0]) or int(subnet_split[1]) > 32)

def tests():
    print "+-----------------------------+"
    print "|        Address Tests        |"
    print "+-----------------------------+"
    # There should be a valid subnet for each valid ip. They should share the same index. If you add more then make sure you add a subnet that works with the ip AT THE SAME INDEX AS EACHOTHER.
    valid_ip = ["255.255.255.255", "1.1.1.1", "30.25.255.10", "0.0.0.0"]
    valid_subnets = ["255.255.255.0/24", "1.1.1.0/31", "30.25.255.0/28", "0.0.0.0/32"]
    invalid_ip = ["0.0.0.256", "-1.1.1.1", "1.1.1.1.1", "1000.80.10.2"]
    invalid_subnets = []
    for idx in range(len(valid_ip)):
        assert(Address.isValidIPv4(valid_ip[idx]))
        print "[+] Successfully validated IP '{}'".format(valid_ip[idx])
        assert(Address.isValidSubnet(valid_subnets[idx]))
        print "[+] Successfully validated subnet '{}'".format(valid_subnets[idx])
        assert(Address.isMemberOfSubnet(valid_ip[idx], valid_subnets[idx]))
        print "[+] Successfully verified that '{0}' is a member of '{1}'".format(valid_ip[idx], valid_subnets[idx])

    for ip in invalid_ip:
        assert(not Address.isValidIPv4(ip))
        print "[+] Successfully caught invalid IP '{}'".format(ip)

if __name__ == "__main__":
    print "This module cannot be run as a standalone program. Please run __main__.py"