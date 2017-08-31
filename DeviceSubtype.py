# <summary>
# BAM device subtype instance. Contains only basic info right now, that could change down the road however
# </summary>
# <todo priority="high">
# Escape name to avoid potential errors with certain special chars
# </todo>
class DeviceSubtype:
    def __init__(self, name, type_id, parent_id=None):
        self.__name = name
        self.__id = type_id
        if parent_id:
        	self.__parent_id = parent_id

    # <summary>
    # Accessor for device id
    # </summary>
    def id(self):
        return self.__id

	# <summary>
    # Accessor for device name
    # </summary>
    def name(self):
        return self.__name

if __name__ == "__main__":
    print "This module cannot be run as a standalone program. Please run __main__.py"