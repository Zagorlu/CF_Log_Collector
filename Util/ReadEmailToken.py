import win32com.client


class ReadEmailToken:
    """
    This class created for reading which token sent on email.
    It based for only read token and insert mdsp side
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

    @staticmethod
    def readTokenFromOutlook():
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6)
        messages = inbox.Items
        message = messages.GetLast()
        for line in [line.strip() for line in str(message.body).splitlines()]:
            if "following login token:" in line:
                return line.split(' ')[-1].strip()
