import xml.etree.ElementTree as ET


class ConfigParser:
    """
    This static class does not applicable for creeation. It's only supporting to static instances.
    In this class properties only gets the config.xml file from xml tags attributes.
    """
    def __init__(self):
        """
        INFO: Default Constructure cannot be Creatable
        WARNING: If attand to create this object, it will raise NotImplementedError
        """
        assert NotImplementedError("This object useing only library, cannot be creatable!!!")

    def __new__(cls):
        """
        INFO: This method was overrided only avoided to __new__ operator
        :return: NOISE_OBJECT
        """
        return object.__new__(cls)

    ####################################################################################################
    # STATIC INITILIAZER BLOCK
    ####################################################################################################
    tree = ET.parse('.\cfg\config.xml')
    root = tree.getroot()
    PRODS = []
    USERNAME = root.find('username').text
    PASSWORD = root.find('password').text
    LOGIN_URL = root.find('loginUrl').text
    PASSCODE_URL = root.find('passcodeUrl').text

    for item in root.find('prodList').findall('prod'):
        PRODS.append(item.attrib)
    ####################################################################################################
