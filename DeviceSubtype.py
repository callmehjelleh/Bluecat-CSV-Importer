# <summary>
# BAM device subtype instance. Contains only basic info right now, that could change down the road however
# </summary>
class DeviceSubtype:
    def __init__(self, name, device_id):
        self.__name = name
        self.__device_id = device_id

    # <summary>
    # Accessor for device id
    # </summary>
    def id(self):
        return self.__device_id

	# <summary>
    # Accessor for device name
    # </summary>
    def name(self):
        return self.__name
