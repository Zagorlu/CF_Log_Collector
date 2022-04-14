import json


class JsonUtil:

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

    @staticmethod
    def parseJsonForFile(jsonFile):
        """
        INFO: This static method parse to json dictionary
        :param jsonFile: json file source
        :return: DICTIONARY
        """
        with open(jsonFile) as e:
            myResult = json.load(e)

        return myResult


    @staticmethod
    def parseAndFindKey(jsonFile, key):
        return JsonUtil.parseJsonForFile(jsonFile).get(key)

