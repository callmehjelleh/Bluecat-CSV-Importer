#!/usr/bin/python

import socket


class AddressValidator:

    # <summary>
    # Verifies the address provided is in fact a valid ipv4 or fqdn
    # </summary>
    # <param name="addr" type="string">
    # Address to validate
    # </param>
    @staticmethod
    def validate(addr):
        return (AddressValidator.isValidIPv4(addr) or AddressValidator.isValidFQDN(addr))

    # <summary>
    # Verifies that the provided string is a valid IPV4 address.
    # Returns a Boolean value
    # </summary>
    # <param name="addr" type="string">
    # IP address in string format to be verified
    # </param>
    @staticmethod
    def isValidIPv4(addr):
        try:
            socket.inet_pton(socket.AF_INET, addr) # Verify ipv4 using pton
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(addr) # verify using aton
            except socket.error:
                return False
            return addr.count('.') == 3 # Are there 3 '.' chars? (x.x.x.x)
        except socket.error:  # not a valid address
            return False
        return True

    # <summary>
    # Verifies that the provided FQDN is valid
    # </summary>
    # <param name="addr" type="string">
    # FQDN to be verified
    # </param>
    @staticmethod
    def isValidFQDN(addr):
        if addr.split(".").count < 3:
            return False
        return True

if __name__ == "__main__":
    print "This module can not be run as a standalone program. Please run Proteus.App instead."
