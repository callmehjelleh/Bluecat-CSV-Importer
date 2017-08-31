from __main__ import App
from Address import Address
from BAMClient import BAMClient
from CSVReader import CSVReader
from Device import Device
from DeviceType import DeviceType
from DeviceSubtype import DeviceSubtype

def ignore_callback(msg, fail):
    return

# <summary>
# Unit tests go here. There should be a function for each module, called within this one. 
# </summary>
# <todo priority="high">
# Implement unit testing and fuzzing here
# </todo>
def tests(address, username, password, configuration):
    if not address:
        address = BAMClient.default_address
    if not username:
        username = BAMClient.default_username
    if not password:
        password = BAMClient.default_password
    if not configuration:
        configuration = BAMClient.default_configuration

    App_tests(address, username, password, configuration)
    print "[+] App Tests Succeeded!"
    Address_tests()
    print "[+] Address Tests Succeeded!"
    BAMClient_tests()
    print "[+] BAMClient Tests Succeeded!"
    Device_tests(BAMClient(address, username, password, ignore_callback), configuration)
    print "[+] Device Tests Succeeded!"

def Address_tests():
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

    print "Address Tests Succeeded!"

def App_tests(address, username, password, configuration):
    print "+-----------------------------+"
    print "|          App Tests          |"
    print "+-----------------------------+"

    csv_path = "./test.csv"
    app = App(filename=csv_path,
              verbose=False,
              user_input=False,
              address=address,
              username=username,
              password=password,
              configuration=configuration,
              upload=False)
    app.bam_client = BAMClient(app.address, app.username, app.password, app.errorCallback)
    csv = CSVReader(csv_path, app.errorCallback)

    # Completely pointless test....
    assert(isinstance(app, App))
    print "[+] App type is correct"

    # Verify that formatCell works as intended
    assert(app.formatCell(" Words go here ") == "Words go here")
    print "[+] Format cell works on strings"
    assert(app.formatCell(float('nan')) == "Not Listed")
    print "[+] Format cell works on 'nan'"
    assert(app.formatCell(None) == "Not Listed")
    print "[+] Format cell works on null object"

    # Test out populating device types. Verify no type confusion occurs, etc.
    device_types = app.populateDeviceTypes(csv)

    app.id_list = device_types

    # Test out populating devices. Verify no type confusion occurs, etc.
    devices = app.populateDevices(csv)
    assert(isinstance(devices, list))
    print "[+] Devices are correct type"
    for i in devices[0]:
        assert(isinstance(i, Device))
        print "[+] Device {} is correct type".format(i.name())

def BAMClient_tests():
    print "+-----------------------------+"
    print "|       BAMClient Tests       |"
    print "+-----------------------------+"

# <summary>
# Unit tests for CSVReader
# </summary>
# <todo priority="low">
# Not using them for anything right now, but unit tests still need to be written for removeRows and modifyValue
def CSVReader_tests():
    def callback(msg, fail):
        return
    print "+-----------------------------+"
    print "|       CSVReader Tests       |"
    print "+-----------------------------+"
    csv = CSVReader('testdevice.csv', callback)

    assert(csv.getColumn('Not existing') == None)
    print "[+] Successfully handled unexisting column name for getColumn"
    assert(csv.getColumn('Name'))
    print "[+] Successfully fetches column"
    assert(type(csv.getColumn('Name')) == list)
    print "[+] Correct return type for getColumn"
    assert(csv.getColumns(['Not existing']) == None)
    print "[+] Successfully handled unexisting column for getColumns"
    assert(csv.getColumns(['Name', 'IP']))
    print "[+] Successfully fetches columns"
    assert(type(csv.getColumns(['Name', 'IP'])) == dict)
    print "[+] Correct return type for getColumns"
    assert(type(csv.getRows()) == list)
    print "[+] Correct return type for getRows"
    for row in csv.getRows():
        assert(type(row[1]) == pd.core.series.Series)
        print "[+] Successfully found Series object in row"


def Device_tests(BAM, config):
    print "+-----------------------------+"
    print "|        Device Tests         |"
    print "+-----------------------------+"
    BAM.setConfiguration(config)
    device_type = BAM.addDeviceType("Unit_test_type")
    device_subtype = BAM.addDeviceSubtype(device_type[1], "Unit_test_subtype")
    device = Device("Unit_test_device", [Address("1.1.1.1", "1.1.1.0/24", ignore_callback)], DeviceType("Unit_test_type", device_type[1]), DeviceSubtype("Unit_test_subtype", device_subtype[1], device_type[1]), ignore_callback)
    assert(isinstance(device, Device))
    print "[+] Device instance is correct type"
    assert(device.mergeAddresses("1.1.1.2"))
    assert(device.addresses()[1].IP() == "1.1.1.2")
    print "[+] Successfully merged IP"
    assert(not device.mergeAddresses("256.1.1.1"))
    assert(len(addresses) == 2)
    print "[+] Successfully ignored incorrect address"

def DeviceType_tests():
    print "+-----------------------------+"
    print "|      Device Type Tests      |"
    print "+-----------------------------+"

def DeviceSubtype_tests():
    print "+-----------------------------+"
    print "|     Device Subtype Tests    |"
    print "+-----------------------------+"