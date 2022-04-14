from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from selenium import webdriver
from Util.ConfigParser import ConfigParser


class Utility:
    """
    This class contain to regular functions for frame Class. It's only supporting to static instances.
    If it necessary for new features, this scope can specialize for features.
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

    #############################################################################################
    # STATIC PROPERTIES
    #############################################################################################
    LINE = "-----------------------------------------------------\n"

    @staticmethod
    def getPasscode():
        """
        This method returns to passcode from defined xml login url and passcode direction url.
        Also it use selenium and chrome web driver. If that options not avaiable, it must be modify
        and declerate on class.

        NOTE: PLEASE PAY ATTENTION
        THIS PART USAGE FOR AUTHENTICATION PART, DEPENCE ON PLATFORM
        :return:
        """
        driver = webdriver.Chrome(executable_path='.\items\chromedriver.exe')
        driver.get(ConfigParser.LOGIN_URL)
        elem = driver.find_elements_by_xpath(r"/html/body/div[1]/div[2]/div/div/div/a")
        elem[0].click()
        try:
            email = driver.find_element_by_xpath(r'//*[@id="emailAddress"]'.encode())
            password = driver.find_element_by_xpath(r'//*[@id="passLogin"]'.encode())
            signIn = driver.find_element_by_xpath(r'//*[@id="login-button"]/span'.encode())
        except Exception as e:
            print "EXCEPTION > {0}".format(str(e))
            email = driver.find_element_by_id("emailAddress")
            password = driver.find_element_by_id("passLogin")
            signIn = driver.find_element_by_id("login-button")
        email.send_keys(ConfigParser.USERNAME)
        password.send_keys(ConfigParser.PASSWORD)
        signIn.click()
        driver.get(ConfigParser.PASSCODE_URL)
        passCode = driver.find_element_by_xpath(r'/html/body/div[1]/div[2]/h2')
        result = str(passCode.text)
        driver.close()
        return result

    @staticmethod
    def getConnetionUrl(prodUrl, org):
        """
        This method prepare to connection url for Cloud Foundry CLI screen.
        :param prodUrl: Prod type URL
        :param org: Organization info
        :return: Connection URL
        """
        return "cf login -a {0} --sso-passcode {1} -o {2}".format(prodUrl, Utility.getPasscode(), org)

    @staticmethod
    def getSpaceSetCommand(space):
        """
        This method prepare to space bind command for Cloud Foundry CLI screen.
        :param space: Space Info
        :return: Binding to Space command
        """
        return "cf target -s {0}".format(space)
