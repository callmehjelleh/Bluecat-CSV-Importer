#!/usr/bin/python

from CSVReader import CSVReader
from AddressValidator import AddressValidator
from suds.client import Client
import logging
import coloredlogs

# Prevents flooding of output from the suds client
# remove at your own risk
suds_log = logging.getLogger('suds').setLevel(logging.CRITICAL)

# <summary>
# Class for interacting with BAM API
# </summary>
class BAMClient:

    # Default configuration information
    default_address = "10.255.255.50"
    default_user = "eriktest"
    default_password = "C0k3z3r0!"
    default_configuration = "Test"

    # <summary>
    # Constructor for BAM
    # </summary>
    # <param name="address" type="string">
    # Address of BAM server (default = 10.255.255.50)
    # </param>
    # <param name="user" type="string">
    # Username for authentication with BAM service
    # </param>
    # <param name="password" type="string">
    # Password for authentication with BAM service
    # </param>
    # <param name="callback" type="function" args="string, Boolean">
    # Callback function for error reporting
    # </param>
    def __init__(self, address, user, password, callback=None):
        self.callback = callback

        try:
            if AddressValidator.validate(address):
                self.client = Client(url="http://" + address + "/Services/API?wsdl", faults=True).service
                self.client.login(user, password)
            else:
                self.callback("Invalid Address supplied", True)
        except Exception, e:
            self.callback("%s" % e, False)
            self.callback("Could not initialize BAM client, check service is running and credentials are correct.", True)

    # <summary>
    # Tests to verify validity of BAM configuration name.
    # If it is valid, sets the current active configuration to the one provided.
    # If not valid, sends a critical failure to callback
    # </summary>
    # <param name="name" type="string">
    # the name of the BAM configuration to test/set
    # </param>
    def setConfiguration(self, name=None):
        configurations = self.getConfigurations()
        configuration_id = None
        for configuration in configurations:
            if configuration["name"] == name:
                self.configuration_id = configuration["id"]
        if not self.configuration_id:
            self.callback("Configuration %s not found on BAM service" % name, True)
        return self.configuration_id

    # <summary>
    # Returns a list of configurations from the BAM service.
    # if unable, sends a critical failure to callback
    # </summary>
    def getConfigurations(self):
        try:
            configurations = self.client.getEntities(0, "Configuration", 0, 1000)[0]
            if not configurations:
                self.callback("No configurations present on the BAM service.", True)
            return configurations
        except:
            self.callback("Could not retrieve configurations from BAM service.", True)

    # <summary>
    # Dumps some basic configuration info from the BAM server
    # </summary>
    def getInfo(self):
        self.client.getSystemInfo();

    # <summary>
    # Adds a new Device type to the BAM service.
    # If it fails, it simply means it likely already exists, and so is not a critical failure
    # returns a list containing [device ID, device name]
    # TODO: check to ensure that device ID is a number, not a string. If it is a string, convert it to a number before returning
    # </summary>
    # <param name="name" type="string">
    # The name of the new device type to be added
    def addDeviceType(self, name=None):
        try:
            if name == None or str(name) == 'nan':
                name = "Not Listed"
            return [self.client.addDeviceType(name.strip()), name.strip()]
        except:
            device = self.client.getEntityByName(0, name.strip(), "DeviceType")
            if device:
                logging.debug("Server says: Device type {0} already exists with ID {1}".format(name.strip(), device["id"]))
                return [device["id"], name.strip()]
            self.callback("Error adding device type %s" % name, False)

    # <summary>
    # Adds a new Device subtype to the BAM service.
    # If it fails, it simply means it likely already exists, and so is not a critical failure
    # returns a list containing [subdevice ID, subdevice name]
    # TODO: check to ensure that subdevice ID is a number, not a string. If it is a string, convert it to a number before returning
    # </summary>
    # <param name="name" type="string">
    # The name of the new device subtype to be added
    # </param>
    def addDeviceSubtype(self, device_id, name=None):
        try:
            if name == None or str(name) == "nan":
                name = "Not Listed"
            return [self.client.addDeviceSubtype(device_id, name.strip(), None), name.strip()]
        except:
            device = self.client.getEntityByName(device_id, name.strip(), "DeviceSubtype")
            if device:
                logging.debug("Device subtype {0} already exists with ID {1} and parent ID {2}".format(name.strip(), device["id"], device_id))
                return [device["id"], name.strip()]
            self.callback("Error adding device type %s" % name.strip(), False)

    # <summary>
    # Gets a list of device types on the BAM service
    # </summary>
    def getDeviceTypes(self):
        return self.client.getEntities(0, "DeviceType", 0, 5000)

    # <summary>
    # Adds a new Device entity to the BAM service based on a local Device instance
    # </summary>
    # <param name="device" type="Device">
    # The device to add to the BAM service
    # </param name="device" type="Device">
    # The device object to add to the server
    # </param>
    def addDevice(self, device):
        device_entity = self.getDevice(device.name())
        if not device_entity['id'] == 0:
            logging.warning("Device {0} already exists with ID {1}. Skipping...".format(device.name(), device_entity['id']))
            return device_entity
        try:
            print device.name()
            for IP in device.addresses():
                self.addNetwork(IP)
                
            self.client.addDevice(self.configuration_id,
                                  device.name(), 
                                  device.device_type().id(), 
                                  device.device_subtype().id(), 
                                  ','.join(device.addresses()),
                                  None, None)    
        except Exception, e:
            self.callback("Error creating device: {}".format(e), False)

    # <summary>
    # Returns a device with the provided device object's name if one exists on the BAM service
    # </summary>
    # <param name="device" type="string">
    # The device name to query the server for
    # </param>
    def getDevice(self, device):
        return self.client.getEntityByName(self.configuration_id, device.name(), "Device")
    
    # <summary>
    # Creates a new network entity and adds it to the network block with the same CIDR
    # Currently creates only networks with the CIDR /24 of the IP
    # If the specified block does not exist, a new one is created 
    # </summary>
    # <param name="IP" type="string">
    # An IP contained in the network
    # </param>
    # <todo priority="moderate">
    # Allow creation of networks with different CIDR notations.
    # </todo>
    def addNetwork(self, IP):
        network_entity = self.getNetwork(IP)
        if not network_entity['id'] == 0:
            logging.debug("Network for IP {0} already exists with ID {1}".format(IP, network_entity['id']))
            return network_entity
        
        block_id = self.getBlock(IP)['id']
        if block_id == 0:
            logging.debug("No block entity found for IP {0}. Creating it now.".format(IP))
            block_id = self.addBlock(IP)

        CIDR = IP.rsplit('.', 1)[0] + '.0/24'
        logging.debug("Adding a new network for CIDR {0}".format(CIDR))
        return self.client.addIP4Network(block_id, CIDR, None)        

    # <summary>
    # Queries the server for a Network based on an IP contained within it
    # </summary>
    # <param name="IP" type="string">
    # The IP contained within the network to query for
    # </param>
    def getNetwork(self, IP):
        network_entity = self.client.getIPRangedByIP(self.configuration_id, "IP4Network", IP)
        if network_entity['id'] == 0:
            logging.debug('No network entity found for CIDR {0}'.format(IP))
        return network_entity

    # <summary>
    # Adds a new network block entity, if one does not already exist
    # Currently only creates blocks with the CIDR /24 of the IP provided
    # </summary>
    # <param name="IP" type="string">
    # The IP contained within the block to create
    # </param>
    # <todo priority="moderate">
    # Allow creation of blocks by CIDR notation (not just /24)
    # </todo>
    def addBlock(self, IP):
        block_entity = self.getBlock(IP)
        if not block_entity['id'] == 0:
            return block_entity

        CIDR = IP.rsplit('.', 1)[0] + '.0/24'
        return self.client.addIP4BlockByCIDR(self.configuration_id, CIDR, None)

    # <summary>
    # Queries the server for a network block based on an IP contained within it
    # </summary>
    # <param name="IP" type="string">
    # The IP contained within the block to check for
    # </param>
    def getBlock(self, IP):
        return self.client.getIPRangedByIP(self.configuration_id, "IP4Block", IP)

# TODO: replace with unit testing
if __name__ == "__main__":
    def callback(msg, fail):
        print msg

    csv = CSVReader('testdevice.csv', callback)
    bam = BAM(BAM.default_address, BAM.default_user, BAM.default_password)

    bam._BAM__merge_IP(csv)
