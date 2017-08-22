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
	# 
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
		
	def name(self):
		return self.__name

	def device_type(self):
		return self.__device_type

	def device_subtype(self):
		return self.__device_subtype

	def addresses(self):
		return self.__addresses.split(',')

	def mergeAddresses(self, address):
		self.__addresses += ',' + address.strip()