#!/usr/bin/python
from Address import Address
from argparse import ArgumentParser
from BAMClient import BAMClient
#from ColoredLogger import ColoredLogger
from CSVReader import CSVReader
import coloredlogs
from DeviceType import DeviceType
from DeviceSubtype import DeviceSubtype
from Device import Device
import getpass
import logging

logging.basicConfig()

# <summary>
# Main module of the program. also provides a debugging interface.
# </summary>
class App:

    # <summary>
    # Constructor for App class
    # </summary>
    # <param name="user_input" type="boolean">
    # Controls whether users have the ability to input their own info such as BAMClient server address, username, password, etc.
    # </param>
    # <param name="debug" type="boolean">
    # Controls how much information is given during errors or general runtime
    # </param>
    def __init__(self, filename, user_input, verbose, address, username, password, configuration, upload):
        self.user_input = user_input
        self.verbose = verbose
        self.bam_client = None
        self.logger = logging.getLogger(__name__)
        self.id_list = {}
        self.address = address
        self.username = username
        self.password = password
        self.configuration = configuration
        self.filename = filename
        self.upload = upload
        
        if self.verbose:
            coloredlogs.install(logger=self.logger, level='DEBUG', format="%(levelname)s:%(msg)s")
        else:
            coloredlogs.install(logger=self.logger, level='WARNING', format="%(levelname)s:%(msg)s")

    # <summary>
    # Main entry point for the program
    # </summary>
    # <param name="export" type="boolean">
    # Determines application execution path (e.g. whether to import or export data to/from the BAM service)
    def start(self, export):
        if not self.user_input:
            if not self.address:
                self.address = BAMClient.default_address
            if not self.username:
                self.username = BAMClient.default_username
            if not self.password: 
                self.password = BAMClient.default_password
        else:
            self.address = raw_input("IP Address: ")
            self.username = raw_input("Username: ")
            self.password = getpass.getpass("Password: ")

        self.bam_client = BAMClient(self.address, self.username, self.password, self.errorCallback)

        if self.user_input and not self.configuration:
                user_config = raw_input("Active configuration to use on BAMClient server: ")
        else:
            # TODO: Change this to perhaps accepting the first available configuration in the confirmed list.
            # This would future-proof the script in the event that configuration names change such that "Ontera Management" no longer exists/is renamed
            self.configuration = BAMClient.default_configuration

        self.bam_client.setConfiguration(self.configuration)

        # TODO: This section is ridiculously messy. Clean this up ASAP
        self.csv = CSVReader(self.filename, self.errorCallback)
        self.id_list = self.populateDeviceTypes(self.csv)
        self.devices, error = self.populateDevices(self.csv)
        for i in self.devices:
            self.bam_client.addDevice(i)
        self.dumpMemory()

    # <summary>
    # Replaces invalid values with 'Not Listed' and trims trailing whitespace. Intended to be used with csv cell values
    # </summary>
    # <param name="str_val" type="string">
    # The string to format
    # </param>
    def formatCell(self, str_val):
        if not str_val or str(str_val) == 'nan':   
            str_val = 'Not Listed'
        return str_val.strip()

    # <summary>
    # Populates the devices table from the csv
    # </summary>
    # <param name="csv" type="CSVReader">
    # The csv reader instance to read from
    # </param>
    def populateDevices(self, csv):
        devices = []
        error = []
        rows = csv.getRows()
        for idx in range(len(rows)):
            row = rows[idx][1] # We need the Series object, row itself is actually a Tuple containing an index and a Series

            row['IP'] = self.formatCell(row['IP'])
            row['Name'] = self.formatCell(row['Name'])
            row['Device Type'] = self.formatCell(row['Device Type'])
            row['Device Subtype'] = self.formatCell(row['Device Subtype'])

            present = False
            # TODO: There's definetly a better way to do this. Revisit this at some point
            for device in devices:
                if self.formatCell(row['Name']) == device.name():
                    device.mergeAddresses(Address(row['IP'], row['IP'].rsplit('.', 1)[0] + '.0/24', self.errorCallback))
                    present = True
                    break
            if not present:
                try:
                    devices.append(Device(name=self.formatCell(row['Name']), 
                                          addresses=[Address(i, i.rsplit('.', 1)[0] + '.0/24', self.errorCallback) for i in row['IP'].split(',')], 
                                          device_type=self.id_list[row['Device Type']], 
                                          device_subtype=self.id_list[row['Device Type']].subtypes()[row['Device Subtype']],
                                          error_callback=self.errorCallback))
                except ValueError:
                    error.append([row, idx])
        return [devices, error]

    # <summary>
    # Adds devices to the BAM Service from the csv
    # Populates id_list with Device objects, along with their child subtypes
    # </summary>
    # <param name="csv" type="CSVReader">
    # CSVReader instance with open csv containing values to add to the BAM Service
    # </param>
    def populateDeviceTypes(self, csv):
        cols = csv.getColumns(['Device Type', 'Device Subtype'])
        device_column = cols['Device Type']
        subdevice_column = cols['Device Subtype']
        id_list = {}
        # Loop through the amount of device types found in csv (note: can't have subtype without parent type)
        for idx in range(len(device_column)):

            device_column[idx] = self.formatCell(device_column[idx])
            self.logger.debug("Checking device \'{0}\'".format(device_column[idx]))

            try:
                # attempt to access the dict key for the current device type
                dev_obj = id_list[device_column[idx]]
                dev = [dev_obj.id(), dev_obj.name()]
                self.logger.debug("Device type \'{0}\' already present in id list with ID {1}".format(dev[1], dev[0]))
            except KeyError: # Device type doesn't exist yet!
                dev = self.bam_client.addDeviceType(device_column[idx])
                id_list[dev[1]] = DeviceType(dev[1], dev[0])
                self.logger.debug("Device type \'{0}\' has been added with ID {1}".format(dev[1], dev[0]))
            except Exception,e: # Something bad happened...
                self.errorCallback("Device type \'{0}\' failed to be added: {1}".format(device_column[idx], e), True)

            subdevice_column[idx] = self.formatCell(subdevice_column[idx])
            self.logger.debug("Checking device subtype \'{0}\'".format(subdevice_column[idx]))

            try:
                # attempt to access the dict key for the current device subtype
                # Accessing this looks kinda messy so lets break it down.
                # dev[1] is the name of the current device, which we got just above
                # id_list[dev[1]] gets you the current device type in the dict
                # With that in mind calling subtypes() on a DeviceType instance provides the list of subtypes of that device type currently available
                # [subdevice[idx]] is the current index in the table/csv, so we're trying to access a dict key with that name. If it fails we know its not there yet
                subdev_obj = id_list[dev[1]].subtypes()[subdevice_column[idx]]
                subdev = [subdev_obj.id(), subdev_obj.name()]
                self.logger.debug("Device subtype \'{0}\' already present in id list with ID {1}".format(subdev[1], subdev[0]))
            except KeyError:
                subdev = self.bam_client.addDeviceSubtype(dev[0], subdevice_column[idx])
                id_list[dev[1]].add(DeviceSubtype(subdev[1], subdev[0]))
                self.logger.debug("Device subtype \'{0}\' has been added to \'{1}\' with ID {2}".format(subdev[1], id_list[dev[1]], subdev[0]))
            except Exception,e:
                self.errorCallback("Device subtype \'{0}\' failed to be added to \'{1}\': {2}".format(subdevice_column[idx], id_list[dev[1]], e), True)
        return id_list

    # <summary>
    # Handles error messages sent by other classes like the BAMClient class
    # </summary>
    # <param name="msg" type="string">
    # Error message to display
    # </param>
    # <param name="fail" type="boolean">
    # Tells the function whether the error was critical. If so, it ends the program after printing the error message
    # </param>
    def errorCallback(self, msg, fail):
        if fail:
            self.logger.critical(msg)
            if self.verbose:
                self.dumpMemory()
            logging.shutdown()
            exit(-1)
        else:
            logging.warning(msg)

    # <summary>
    # Dumps important program memory in the event of critical failure
    # </summary>
    def dumpMemory(self):
        self.logger.debug("-----------------")
        self.logger.debug("Begin memory dump")
        self.logger.debug("-----------------")
        self.logger.debug("App:")
        # list all attributes/members of this App instance
        for k,v in vars(self).items():
            self.logger.debug('\t' + str([k,v]))
        self.logger.debug("Client:")
        try:
            if self.bam_client:
                # list all attributes/members of the App's bam_client instance
                for var in vars(self.bam_client):
                    if not var == 'client':
                        self.logger.debug('\t' + str([var, getattr(self.bam_client, var)]))
                    else:
                        # Shitty workaround because otherwise we can't see any info about the BAMClient client (throws an exception)
                        self.logger.debug('\t' + str([var, 'ProteusAPI.ProteusAPIPort doesn\'t have __repr__ >:(']))
            else:
                self.logger.error("\tNo BAM client was initialized!")

        except Exception, e:
            self.logger.critical("Error providing debug info for Client! %s" % e)

        self.logger.debug("ID List:")
        try:
            if self.id_list:
                # List all items in the device type id list
                for i in self.id_list:
                    self.logger.debug('\t' + i + ':')
                    # List all subkeys of the current device type object
                    for k,v in vars(self.id_list[i]).items():
                        if not k == '_Device_Type__children':
                            # List all subkeys of the sub device type objects associated with the current device type
                            self.logger.debug('\t\t' + str([k,v]))
                        else:
                            import code
                            code.InteractiveConsole(locals=locals()).interact()
                            print [v[j] for j in v]
            else:                
                self.logger.error("\tNo ID list was generated!")
        except Exception, e:
            self.logger.critical("Error providing debug info for id_list! %s" % e)

        self.logger.debug("---------------")
        self.logger.debug("End memory dump")
        self.logger.debug("---------------")

if __name__ == "__main__":
    # Argument list
    # <param name="verbose" type="boolean" default="False">
    # Controls whether to display debug information
    # </param>
    # <param name="filename" type="string">
    # The filepath to the csv
    # </param>
    # <param name="user_input" type="boolean" default="False">
    # Controls whether the user will be prompted for info at runtime
    # </param>
    # <param name="address" type="string">
    # The address of the server running the BAM Service
    # </param>
    # <param name="username" type="string">
    # The username used to auth to the BAMClient API
    # </param>
    # <param name="password" type="string">
    # The password used to auth to the BAMClient API
    # </param>
    # <param name="configuration" type="string">
    # The configuration to use on the BAMClient for storing the information
    # <param name="upload" type="boolean" default="True">
    # Controls whether the application will import data from the CSV to the BAM Service
    # </param>

    parser = ArgumentParser()
    parser.set_defaults(debug=False, filename="test.csv", interactive=True)
    parser.add_argument("-v", "--verbose", default=False, action="store_true", dest="verbose", help="Display debug information")
    parser.add_argument("-f", "--filename", default="test.csv", action="store", dest="filename", help="Read CSV data from FILE")
    parser.add_argument("-i", "--interactive", default=False, action="store_true", dest="user_input", help="Allow user interaction")
    parser.add_argument("-a", "--address", default=None, action="store", dest="address", help="The address of the BAMClient server")
    parser.add_argument("-u", "--username", default=None, action="store", dest="username", help="The username to use for authentication")
    parser.add_argument("-p", "--password", default=None, action="store", dest="password", help="The password to use for authentication")
    parser.add_argument("-c", "--configuration", default=None, action="store", dest="configuration", help="The BAMClient configuration to use")
    parser.add_argument("--export", default=False, action="store_true", dest="export", help="Export data from the server rather than import")
    parser.add_argument("-t", "--testing", default=False, action="store_true", dest="test", help="Enables unit testing mode")
    #parser.add_argument("-n", "--network", default=False, action="store_true", dest="network_mode", help="Controls whether the program will use network mode to import and tag whole networks")
    args = parser.parse_args()

    if args.test == True:
        import Tests
        # Suppress logging
        coloredlogs.set_level('CRITICAL')
        logger = logging.getLogger('__main__')
        logger.propagate = False
        Tests.tests(args.address, args.username, args.password, args.configuration)
        exit(0)

    app = App(filename=args.filename, 
              verbose=args.verbose,
              user_input=args.user_input, 
              address=args.address, 
              username=args.username, 
              password=args.password, 
              configuration=args.configuration, 
              upload=args.export)
    app.start(args.export)
    logging.shutdown()