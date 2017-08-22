from DeviceSubtype import DeviceSubtype

# <summary>
# BAM device type instance. Contains only basic info right now, that could change down the road however
# </summary>
# <todo priority="low">
# Rename children to subtypes maybe?
# </todo>
class DeviceType:

    # <summary>
    # Constructor for DeviceType
    # </summary>
    # <param name="name" type="string">
    # The name of the Device Type
    # </param>
    # <param name="device_id" type="string">
    # The device id associated with the device type, provided by the BAM service
    # </param>
    # <param name="children" type="dict">
    # Optional, allows passing of a pre-created dict of DeviceSubtype objects to be passed in
    # </param>
    def __init__(self, name, device_id, children=None):
        self.__name = name
        self.__device_id = device_id
        if children:
            # Parameter validation of children. Verify that all children passed in are in fact DeviceSubtype objects
            for child in children:
                if not isinstance(child, DeviceSubtype):
                    children = None
                    break
            self.children = children
        else:
            self.children = {}

    # <summary>
    # Adds a new DeviceSubtype to children
    # </summary>
    # <param name="child" type="DeviceSubtype">
    # The subtype to add
    # </param>
    def add(self, child):
        if not isinstance(child, DeviceSubtype):
            return False
        self.children[child.name()] = child
        return True

    # <summary>
    # Accessor for device subtypes
    # </summary>
    def subtypes(self):
        return self.children

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
        