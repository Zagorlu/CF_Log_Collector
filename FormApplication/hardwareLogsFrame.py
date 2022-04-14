import os
import wx
import subprocess
import sqlite3
import time

from os import sys, path

from FormApplication.mainFrame import processOrg

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Util.ConfigParser import ConfigParser
from Util.UtilityClasses import Utility
from Util.CommandProc import CommandProc
from Data.boolObjectClass import boolObjectClass
from Data.processOrg import processOrg
from threading import *

"""
class processOrg(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(processOrg, self).__init__(target=target, name=name, args=args)
        self._stopper = Event()

    def stop(self):
        self._stopper.set()
"""

class HardwareLogsFrame(wx.Frame):
    """
    This class create the main panel form UI
    """
    def __init__(self, title):
        #############################################################################################
        # PANEL INITIALIZATION
        #############################################################################################
        wx.Frame.__init__(self, None, title=title, size=(920, 680), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        panel = wx.Panel(self, wx.ID_ANY)

        #############################################################################################
        # ICON INITIALIZATION
        #############################################################################################
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("..\items\log.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        # BUTTON
        self.connectButton = wx.Button(panel, size=(100, 127), pos=(125, 3), label="Connect")
        self.getAllButton = wx.Button(panel, size=(127, 127), pos=(430, 3), label="Get All Apps States")
        self.stopTaskButton = wx.Button(panel, size=(127, 127), pos=(560, 3), label="Stop Task")
        self.saveLogFileButton = wx.Button(panel, size=(127, 127), pos=(690, 3), label="Save Logs")

        # COMBOBOX
        self.cb = wx.ComboBox(panel, size=(115, 100), choices=[], pos=(1, 1), value="Select Prod")

        # LISTBOX
        self.lst = wx.ListBox(panel, size=(115, 100), style=wx.LB_SINGLE, pos=(5, 30))
        self.lstSpace = wx.ListBox(panel, size=(200, 127), style=wx.LB_SINGLE, pos=(227, 3), choices=["Waiting Process.."])

        # TEXTBOX
        self.text = wx.TextCtrl(panel, size=(900, 220), style=wx.TE_MULTILINE, pos=(5, 147))
        self.textOfLogs = wx.TextCtrl(panel, size=(900, 250), style=wx.TE_MULTILINE, pos=(5, 387))


        # LABEL
        wx.StaticText(panel, label="> Actions :", pos=(1, 130))
        wx.StaticText(panel, label="> Logs :", pos=(1, 370))

        #############################################################################################
        # OBJECT PROCESS
        #############################################################################################
        self.widgetMaker(self.cb, ConfigParser.PRODS)
        self.textOfLogs.SetEditable(False)
        self.text.SetEditable(False)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.cb, 0, wx.ALL, 5)
        self.stopTaskButton.Disable()
        panel.SetSizer(sizer)

        #############################################################################################
        # OBJECT BINDING
        #############################################################################################
        # BUTTON BIND
        self.Bind(wx.EVT_BUTTON, self.executeButton, self.connectButton)
        self.Bind(wx.EVT_BUTTON, self.onGetAllButton, self.getAllButton)
        self.Bind(wx.EVT_BUTTON, self.saveLogFileButtonFunc, self.saveLogFileButton)
        self.Bind(wx.EVT_BUTTON, self.onStopTask, self.stopTaskButton)

        # LISTBOX BIND
        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lst)

        # CLOSE BIND
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        #############################################################################################
        # CLASS PROPERTIES
        #############################################################################################
        self.ORG_SELECTION = ""
        self.PROD_INFO = {}
        self.SPACES = []
        self.APPLICATIONS = {}
        self.CAPTURE_ALL_PROCESS_FLAG = False
        self.PROCESSES = []
        self.STOP_FLAG = True
        self.MAIN_THREAD = None

    def processOfAppStatus(self, spaceName, appName):
        p = subprocess.Popen(CommandProc.getAppStateCommand(appName), shell=True, stdout=subprocess.PIPE)
        processFlag = boolObjectClass()
        try:
            while processFlag.FLAG:
                output = p.stdout.readline().strip()
                if output.startswith('#'):
                    self.textOfLogs.AppendText("{0} : {1} > {2}\n".format(spaceName, appName, output.strip()))
                    # TODO : LOG PROCESS

        except Exception:
            self.text.AppendText("TERMINATED THREAD > SPACE : {0} APPNAME : {1}\n".format(spaceName, appName))
            self.text.AppendText(Utility.LINE)
        finally:
            p.stdout.flush()
            p.stdout.close()
            p.terminate()
            p.kill()

        self.text.AppendText("COMPLETED THREAD > SPACE : {0} APPNAME : {1}\n".format(spaceName, appName))

    def startHealtCheck(self, event):
        self.STOP_FLAG = False
        while True:
            processCounter = 0
            for space in self.APPLICATIONS:
                apps = self.APPLICATIONS.get(space)
                for app in apps:
                    result = CommandProc.sendCommandGetResponseWithoutException(Utility.getSpaceSetCommand(space))
                    self.text.AppendText(result)
                    processName = "healtState_{0}_{1}_{2}".format(space, app, processCounter)
                    t = processOrg(name=processName, target=self.processOfAppStatus, args=(space, app,))
                    t.daemon = True
                    t.start()
                    t.join(0.8)
                    processCounter += 1

                    self.PROCESSES.append(t)
                    self.text.AppendText("Process started > {0}\n".format(processName))
                    self.text.AppendText(Utility.LINE)

                    if self.STOP_FLAG:
                        break
                if self.STOP_FLAG:
                    break
            if self.STOP_FLAG:
                break


    def setAllApplications(self):
        for space in self.SPACES:
            command = Utility.getSpaceSetCommand(space)
            result = CommandProc.sendCommandGetResponse(command)
            self.text.AppendText(result)
            self.text.AppendText(Utility.LINE)
            self.APPLICATIONS[space] = CommandProc.parseAppNames(CommandProc.getSpaceState())



    def widgetMaker(self, widget, objects):
        """
        This method initiliaze to Prod names to combobox.
        :param widget: combobox decleration
        :param objects: object of frame
        """
        for obj in objects:
            widget.Append(obj.get('name'), obj)
        widget.Bind(wx.EVT_COMBOBOX, self.onSelect)

    def onSelect(self, event):
        """
        This method list to orgs name on listbox.
        :param event: Standart wx argument
        """
        self.lst.Clear()
        self.text.write("You selected: {0} \n " .format(self.cb.GetStringSelection()))
        obj = self.cb.GetClientData(self.cb.GetSelection())
        orgs = obj.get("orgs").split(';')
        for item in orgs:
            self.lst.AppendItems(item)
        print obj
        self.PROD_INFO = obj


    def executeButton(self, event):
        """
        This method connect to cf side and set orgs names to list
        :param event: Standart wx argument
        """
        if self.cb.GetSelection() == -1 or self.lst.GetSelection() == -1:
            wx.MessageBox("You must select from Prod and Org !!!", caption="Warning...")
            return

        self.connectButton.SetLabel("Trying...")
        self.text.AppendText("ORG > " + self.ORG_SELECTION + "\n")
        self.text.AppendText("PROD > " + str(self.PROD_INFO) + "\n")
        connectionUrl = Utility.getConnetionUrl(self.PROD_INFO.get('url'), self.ORG_SELECTION)
        self.text.AppendText("Connection URL > {0}\n".format(connectionUrl))
        result = CommandProc.sendCommandGetResponse(connectionUrl)
        self.connectButton.SetLabel("Connected")
        self.text.AppendText(result)
        self.SPACES = CommandProc.parseSpaces(result)
        self.lstSpace.Clear()
        self.lstSpace.Enable()
        self.lstSpace.AppendItems(self.SPACES)
        self.text.AppendText(Utility.LINE)
        print self.SPACES
        self.setAllApplications()


    def onListBox(self, event):
        """
        This method set selected org to propertyy.
        :param event: Standart wx argument
        """
        self.text.write("Orgs Selected : {0} \n".format(event.GetEventObject().GetStringSelection()))
        self.ORG_SELECTION = event.GetEventObject().GetStringSelection()
        self.text.AppendText(Utility.LINE)

    def onGetAllButton(self, event):
        self.STOP_FLAG = False
        t = processOrg(name="Main_Test", target=self.startHealtCheck, args=(None,))
        t.daemon = True
        t.start()
        self.getAllButton.Disable()
        self.getAllButton.Label = "Running..."
        self.stopTaskButton.Enable()

    def onStopTask(self, event):
        for t in self.PROCESSES:
            t.stop()
        self.STOP_FLAG = True
        self.text.AppendText("Stop flag was set !!!\n")
        self.text.AppendText(Utility.LINE)
        self.getAllButton.Enable()
        self.stopTaskButton.Disable()
        self.getAllButton.Label = "Get All Apps States"

    def saveLogFileButtonFunc(self, event):
        """
        This method save the results of logs. It navigate to user which is selected path and
        :param event: Standart wx argument
        """
        selectedPath = ""
        try:
            dlg = wx.FileDialog(
                self, message="Save Log File",
                defaultDir=os.getcwd(),
                defaultFile="",
                wildcard=".log",
                style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
                )
            if dlg.ShowModal() == wx.ID_OK:
                selectedPath = dlg.GetPaths()

            dlg.Destroy()

            fOpen = open(selectedPath[0], 'w')
            fOpen.write(self.textOfLogs.Value)
            fOpen.close()
            self.textOfLogs.AppendText("{0} is created !!!\n".format(selectedPath))

        except Exception:
            self.text.AppendText("File was not created !!!\n")

    def OnExitApp(self, event):
        """
        This method close button of form. It is destroy to pannel arguments and Frame process.
        :param event: Standart wx argument
        """
        self.Destroy()
        sys.exit(0)
