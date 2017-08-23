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
    def __init__(self, address, subnet, error_callback, FQDN=None):
        self.__error_callback = error_callback

        if not isValidSubnet(subnet):
            self.error_callback("Subnet '{}' is not valid! Could not create Address object")
        self.__subnet = subnet
        if not Address.isValidIPv4(address) or not Address.isMemberOfSubnet(address, self.__subnet):
            self.error_callback("IP '{}' is not valid! Could not create Address object".format(address), False)
        self.__address = address
        if not FQDN or not Address.isValidFQDN(FQDN):
            self.error_callback("FQDN '{}' is not valid! Could not create Address object".format(FQDN), False)
        self.__FQDN = FQDN


    # <summary>
    # Verifies the address provided is in fact a valid ipv4 or fqdn
    # </summary>
    # <param name="address" type="string">
    # Address to validate
    # </param>
    @staticmethod
    def validate(address):
        return (AddressValidator.isValidIPv4(address) or AddressValidator.isValidFQDN(address))

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
            socket.inet_pton(socket.AF_INET, address) # Verify ipv4 using pton
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address) # verify using aton
            except socket.error:
                return False
            return address.count('.') == 3 # Are there 3 '.' chars? (x.x.x.x)
        except socket.error:  # not a valid address
            return False
        return True

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
        return ipaddress.ip_address(address) in ipaddress.ip_network(subnet)

    @staticmethod 
    def isValidSubnet(subnet):
        subnet_split = subnet.split('/')
        return (Address.isValidIPv4(subnet_split[0]) or int(subnet_split) > 32)

if __name__ == "__main__":
    print "This module can not be run as a standalone program. Please run Proteus.App instead."
