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
        self.__subnet = subnet

        if not Address.isValidIPv4(IP) or not Address.isMemberOfSubnet(IP, self.__subnet):
            self.error_callback("IP '{}' is not valid! Could not create Address object.".format(IP), False)
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

if __name__ == "__main__":
    print "This module can not be run as a standalone program. Please run Proteus.App instead."
