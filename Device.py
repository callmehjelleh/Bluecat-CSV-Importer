from DeviceType import DeviceType
from DeviceSubtype import DeviceSubtype
from AddressValidator import AddressValidator

# <summary>
# Class which stores information about a device on the BAM service
# </summary>
class Device:
	# <summary>
	# Constructor for Device Object
	# </summary>
	# <param name="name" type="string">
	# The name of the device
	# </param>
	# <param name="addresses" type="string">
	# The addresses associated with the Device
	# </param>
	# <param name="device_type" type="DeviceType">
	# The device's type
	# </param>
	# <param name="device_subtype" type="DeviceSubtype">
	# The device's subtype
	# </param>
	# <param name="error_callback" type="function">
	# The callback function to use in the event of an error
	# </param>
	def __init__(self, name, addresses, device_type, device_subtype, error_callback):
		self.error_callback = error_callback
		self.__name = name

		# UNTESTED
		for address in addresses.split(','):
			if not AddressValidator.validate(address):
				self.error_callback("Address {} associated with Device is not a valid IP".format(address), False)
				addresses.replace(address, '')


		self.__addresses = addresses
		
		if not isinstance(device_type, DeviceType):
			self.error_callback("Device type must be a DeviceType instance!", True)
		self.__device_type = device_type

		if not isinstance(device_subtype, DeviceSubtype):
			try:
				device_type.subtypes()[device_subtype.name()]
			except KeyError:
				self.error_callback("Device Subtype {0} not a child type of Device type {1}!".format(device_subtype, device_type), True)
			self.error_callback("Device subtype must be a DeviceSubtype instance!", True)
		self.__device_subtype = device_subtype
	
	# <summary>
	# Accessor for device name
	# </summary>
	def name(self):
		return self.__name

	# <summary>
	# Accessor for device type
	# </summary>
	def device_type(self):
		return self.__device_type

	# <summary>
	# Accessor for device subtype
	# </summary>
	def device_subtype(self):
		return self.__device_subtype

	# <summary>
	# Accessor for device addresses
	# </summary>
	def addresses(self):
		return self.__addresses.split(',')

	# <summary>
	# Appends the provided address to the currently held addresses
	# </summary>
	# <param name="address" type="string">
	# The address to add to the existing addresses
	# </param>
	# <todo priority="low">
	# Pass lists of IP's instead to allow batch merging
	# </todo>
	def mergeAddresses(self, address):
		self.__addresses += ',' + address.strip()