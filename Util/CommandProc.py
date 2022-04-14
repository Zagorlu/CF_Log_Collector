from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import re
import subprocess


class CommandProc:
    """
    This class contain to regular functions for Command functions Class. It's only supporting to static instances.
    If it necessary for new features, this scope can specialize for features.
    """
    def __init__(self):
        """
        INFO: Default Constructure cannot be Creatable
        WARNING: If attand to create this object, it will raise NotImplementedError
        """
        assert NotImplementedError("This object using only library, cannot be creatable!!!")

    def __new__(cls):
        """
        INFO: This method was overrided only avoided to __new__ operator
        :return: NOISE_OBJECT
        """
        return object.__new__(cls)

    @staticmethod
    def sendCommandGetResponse(command):
        """
        This basic static method returns command output
        :param command: Direction of command
        :return: Command Result
        """
        result = ""
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            while True:
                output = p.stdout.readline()
                result += output
                p.stdin.write('\n\n')
        except Exception:
            pass

        return result

    @staticmethod
    def getSpaceState():
        """
        This method return to all applications names as a String.
        :return: Spaces names command result
        """
        return CommandProc.sendCommandGetResponse('cf a')

    @staticmethod
    def parseSpaces(text):
        """
        This method return to all space names as a List
        :param text: Source of Space text
        :return: List of Spaces
        """
        result = []
        tmpArray = re.split('[\n]+', text)
        for item in tmpArray:
            if item != '':
                if item.strip()[0].isdigit():
                    result.append(item.strip().split()[1])
        return result

    @staticmethod
    def parseAppNames(text):
        """
        This method return to all application names as a List
        :param text: Source of applications text
        :return: List of applications
        """
        result = []
        tmpArray = re.split('[\n]+', text)
        for item in tmpArray:
            if item != '' and not item.startswith('OK') and not item.startswith('name') and not item.startswith('Getting'):
                result.append(item.strip().split()[0])
        return result

    @staticmethod
    def getAppLogCommand(app):
        """
        This method prepare to cf logs streaming command for cf CLI
        :param app: application name
        :return: Command of Cf logs
        """
        return "cf logs {0}".format(app)
