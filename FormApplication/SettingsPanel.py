import os
import wx
import subprocess
import time
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from ConfigParser import ConfigParser
from Util.ConfigParser import ConfigParser
from Util.UtilityClasses import Utility
from Util.CommandProc import CommandProc
from threading import *
from Data.processOrg import processOrg



class SettingsPanel(wx.Panel):
    """
    This class create the main panel form UI
    """

    def __init__(self, parent):
        #############################################################################################
        # PANEL INITIALIZATION
        #############################################################################################
        wx.Panel.__init__(self, parent)
        self.panel = None

        wx.StaticText(self, label="Widening Time :", pos=(1, 1))
        self.wideningText = wx.TextCtrl(self, size=(180, 20), pos=(120, 1))
        self.wideningText.write(ConfigParser.WIDENING_SEARCH_SECOND)

        wx.StaticText(self, label="Save log Path :", pos=(1, 30))
        self.logSavePeriodPath = wx.TextCtrl(self, size=(180, 20), pos=(120, 30))
        self.logSavePeriodPath.write(ConfigParser.LOG_SAVE_PATH)

        wx.StaticText(self, label="MDSP File Url :", pos=(1, 60))
        self.mdspFileUrl = wx.TextCtrl(self, size=(180, 20), pos=(120, 60))
        self.mdspFileUrl.write(ConfigParser.MDSP_FILE_URL)

        wx.StaticText(self, label="MDSP Asset List Url :", pos=(1, 90))
        self.mdspAssetUrlList = wx.TextCtrl(self, size=(180, 20), pos=(120, 90))
        self.mdspAssetUrlList.write(ConfigParser.MDSP_ASSET_LIST_URL)

        wx.StaticText(self, label="MDSP Token Url :", pos=(1, 120))
        self.mdspTokenUrl = wx.TextCtrl(self, size=(180, 20), pos=(120, 120))
        self.mdspTokenUrl.write(ConfigParser.MDSP_TOKEN_URL)

        wx.StaticText(self, label="MDSP Token :", pos=(1, 150))
        self.mdspToken = wx.TextCtrl(self, size=(180, 20), pos=(120, 150))
        self.mdspToken.write(ConfigParser.TOKEN)

        self.saveButton = wx.Button(self, size=(300, 40), pos=(1, 180), label="Save")
        self.Bind(wx.EVT_BUTTON, self.saveButtonFunc, self.saveButton)

    def saveButtonFunc(self, event):
        ConfigParser.setWideningSearch(self.wideningText.Value)
        ConfigParser.setLogSavePeriodPath(self.logSavePeriodPath.Value)
