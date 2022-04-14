import wx
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class ApplicationStates(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)