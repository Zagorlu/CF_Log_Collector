import os
import wx
import subprocess
import time
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Util.ConfigParser import ConfigParser
from Util.UtilityClasses import Utility
from Util.CommandProc import CommandProc
from threading import *
from Data.processOrg import processOrg
from datetime import datetime


class MdspLogPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        wx.StaticText(self, label="> Productions :", pos=(10, 5))
        self.cb = wx.ComboBox(self, size=(140, 30), choices=[], pos=(10, 30), value="Select Production")
        wx.StaticText(self, label="> Organization Lists :", pos=(10, 60))
        # LISTBOX
        self.lst = wx.ListBox(self, size=(300, 100), style=wx.LB_SINGLE, pos=(10, 80))
        wx.StaticText(self, label="> Space Lists :", pos=(340, 10))
        self.lstSpace = wx.ListBox(self, size=(300, 170), style=wx.LB_SINGLE, pos=(420, 10), choices=["Waiting Process..." ])
        self.lstApp = wx.ListBox(self, size=(300, 170), style=wx.LB_SINGLE, pos=(950, 10))
        # TEXTBOX
        self.text = wx.TextCtrl(self, size=(1250, 200), style=wx.TE_MULTILINE, pos=(10, 220))
        self.textOfLogs = wx.TextCtrl(self, size=(1250, 250), style=wx.TE_MULTILINE, pos=(10, 460))
        self.textKeyword = wx.TextCtrl(self, size=(170, 25), pos=(1300, 10), value="Waiting Process...")
        # BUTTON
        self.setKeywordButton = wx.Button(self, size=(170, 50), pos=(1300, 80), label="Set Keyword")
        self.captureStartButton = wx.Button(self, size=(170, 50), pos=(1300, 150), label="Capture Errors")
        self.captureAllButton = wx.Button(self, size=(170, 50), pos=(1300, 220), label="Capture All Logs")
        self.captureWithKeywordButton = wx.Button(self, size=(170, 50), pos=(1300, 290), label="Capture With Keyword")
        self.clearLogsButton = wx.Button(self, size=(170, 50), pos=(1300, 360), label="Clear Logs")
        self.saveLogFileButton = wx.Button(self, size=(170, 50), pos=(1300, 430), label="Save Logs")
        self.breakAllButton = wx.Button(self, size=(170, 50), pos=(1300, 500), label="Stop All")
        self.connectButton = wx.Button(self, size=(150, 65), pos=(160, 10), label="Connect")
        self.selectButton = wx.Button(self, size=(150, 65), pos=(740, 10), label="Select")
        # CHECKBOX
        self.wideningSearch = wx.CheckBox(self, label="Widening Search", pos=(1300, 38))
        self.periodicSave = wx.CheckBox(self, label="Periodic Save", pos=(1300, 55))
        # LABEL
        wx.StaticText(self, label="> Actions :", pos=(10, 200))
        wx.StaticText(self, label="> Logs :", pos=(10, 440))
        wx.StaticText(self, label="> Apps :", pos=(900, 10))

        #############################################################################################
        # OBJECT BINDING
        #############################################################################################
        # BUTTON BIND
        self.Bind(wx.EVT_BUTTON, self.captureErrorStartButtonFunc, self.captureStartButton)
        self.Bind(wx.EVT_BUTTON, self.captureAllLogsButtonFunc, self.captureAllButton)
        self.Bind(wx.EVT_BUTTON, self.saveLogFileButtonFunc, self.saveLogFileButton)
        self.Bind(wx.EVT_BUTTON, self.onBreakAll, self.breakAllButton)
        self.Bind(wx.EVT_BUTTON, self.onSetKeywordButton, self.setKeywordButton)
        self.Bind(wx.EVT_BUTTON, self.executeButton, self.connectButton)
        self.Bind(wx.EVT_BUTTON, self.onSelectButton, self.selectButton)
        self.Bind(wx.EVT_BUTTON, self.onClearLogsButton, self.clearLogsButton)
        self.Bind(wx.EVT_BUTTON, self.onCaptureKeywordButtonFunc, self.captureWithKeywordButton)
        # LISTBOX BIND
        self.Bind(wx.EVT_LISTBOX, self.onSpaceListBox, self.lstSpace)
        self.Bind(wx.EVT_LISTBOX, self.onAppListBox, self.lstApp)
        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lst)
        # CLOSE BIND
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)
        # CHECKBOX BIND
        self.periodicSave.Bind(wx.EVT_CHECKBOX, self.onPeriodicSaveClicked)
        self.wideningSearch.Bind(wx.EVT_CHECKBOX, self.onWideningSearchClicked)

        #############################################################################################
        # OBJECT PROCESS
        #############################################################################################
        self.lstSpace.Disable()
        self.text.SetEditable(False)
        self.textOfLogs.SetEditable(False)
        self.selectButton.Disable()
        self.widgetMaker(self.cb, ConfigParser.PRODS)

        #############################################################################################
        # CLASS PROPERTIES
        #############################################################################################
        self.ORG_SELECTION = ""
        self.PROD_INFO = {}
        self.SPACES = []
        self.SELECTED_SPACE = ""
        self.SELECTED_APP = ""
        self.KEYWORD = ""
        self.CAPTURE_ALL_PROCESS_FLAG = False
        self.PROCESSES = []
        self.FLAG_KEYWORD = False
        self.FLAG_ERROR = False
        self.wideningSeconds = 21

        #############################################################################################
        # INIT FUNCTIONS
        #############################################################################################
        self.initilizeToken()

    def initilizeToken(self):
        dlg = wx.TextEntryDialog(self, 'Please Insert CF passcode', ' CF Passcode')
        if dlg.ShowModal() == wx.ID_OK:
            ConfigParser.TOKEN = dlg.GetValue()
        else:
            exit(1)
        dlg.Destroy()

    def timer(self, flag):
        """
        This timer method waiting set seconds.
        :param flag: Flag name
        """
        sec = 0
        while sec != self.wideningSeconds:
            self.text.AppendText("{0} Flag passing Time : {1}\n".format(flag, sec))
            time.sleep(1)
            sec += 1
        self.text.AppendText(Utility.LINE)

    def timerProcessKeyword(self):
        """
        This method only toggle keyword flag
        """
        self.FLAG_KEYWORD =True
        self.timer("Keyword Search")
        self.FLAG_KEYWORD = False

    def timerProcessError(self):
        "This method only toggle error flag"
        self.FLAG_ERROR = True
        self.timer("Error Search")
        self.FLAG_ERROR = False

    def onClearLogsButton(self, event):
        """
        This method clear log textbox on form
        :param event: Standart wx argument
        """
        self.textOfLogs.Clear()
        self.text.AppendText("Logs Cleared !!!\n")
        self.text.AppendText(Utility.LINE)

    def captureKeywordProcess(self, command, space):
        """
        This method create to onCaptureKeywordButtonFunc() sub process
        :param command: This argument will pass with releated thread
        """
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            while True:
                output = p.stdout.readline()
                if self.KEYWORD.strip().lower() in output.lower() or self.FLAG_KEYWORD:
                    self.textOfLogs.AppendText("{0} > {1}\n".format(space, output))
                    if self.periodicSave.IsChecked():
                        ConfigParser.PERIODIC_SAVE_FILE.write("{0}\n".format(output))
                    if self.wideningSearch.IsChecked():
                        if not self.FLAG_KEYWORD:
                            tmp = Thread(target=self.timerProcessKeyword, args=())
                            tmp.daemon = True
                            tmp.start()

                if self.CAPTURE_ALL_PROCESS_FLAG:
                    p.stdin.write('\x03')
        except Exception:
            self.text.AppendText("Capture of Keyword Process Terminated \n")
            self.text.AppendText(Utility.LINE)
        finally:
            p.terminate()

    def onCaptureKeywordButtonFunc(self, event):
        """
        This method starts with press to Capture with keyword button. It is searching keyword which is streaming
        logs result.
        :param event: Standart wx argument
        """
        if self.lstApp.GetSelection() == -1:
            wx.MessageBox("You must select App name !!!", caption="Warning...")
            return

        if self.KEYWORD == '':
            wx.MessageBox("You must set keyword !!!", caption="Warning...")
            return

        command = CommandProc.getAppLogCommand(self.SELECTED_APP)
        processName = "captureWithKeywordProcess_{0}_{1}".format(self.SELECTED_APP, self.KEYWORD)

        if self.checkThreadNames(processName):
            self.text.AppendText("This Process already Exist, you can stop all > {0}\n".format(processName))
            self.text.AppendText(Utility.LINE)
            return

        t = processOrg(name=processName, target=self.captureKeywordProcess, args=(command, self.SELECTED_APP,))
        t.daemon = True
        t.start()

        self.PROCESSES.append(t)
        self.text.AppendText("Process started For Keyword > {0}\n".format(processName))
        self.text.AppendText(Utility.LINE)

    def checkThreadNames(self, threadName):
        """
        This method returns to thread list existing state info
        :param threadName: Thread name
        :return: Existing Thread info
        """
        for t in self.PROCESSES:
            if t.getName() == threadName:
                return True
        return False

    def onSetKeywordButton(self, event):
        """
        This method set to Keyword textbox key. If that value not initiliaze before it is warning with message
        :param event: Standart wx argument
        """
        if self.textKeyword.Value == '':
            wx.MessageBox("Keyword is empty !!!", caption="Warning...")
            return

        self.KEYWORD = self.textKeyword.Value
        self.text.AppendText("Keyword set > {0}\n".format(self.textKeyword.Value))
        self.text.AppendText(Utility.LINE)

    def onBreakAll(self, event):
        """
        This method set threads flag which are the added thread list. Also method call stop() method from thread
        for setting to thread internal flag.
        WARNING: This method not guarantee to stop process. On this step only send STOP REQUEST. It can continue
        until isAlive() state.
        :param Standart wx argument
        """

        if not self.PROCESSES:
            self.text.AppendText("Not found any process !!!\n")

        self.CAPTURE_ALL_PROCESS_FLAG = True
        for p in self.PROCESSES:
            self.text.AppendText("Process terminated > {0}\n".format(p.name))
            p.stop()
            del p
        self.PROCESSES = []
        self.text.AppendText("-----------------------------------------------------\n")

    def captureStartErrorProcess(self, command, space):
        """
        This method create to captureErrorStartButtonFunc() sub process
        :param command: This argument will pass with releated thread
        """
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            while True:
                output = p.stdout.readline()
                if 'error' in output.lower() or self.FLAG_ERROR:
                    self.textOfLogs.AppendText("{0} > {1}\n".format(space, output))
                    if self.periodicSave.IsChecked():
                        ConfigParser.PERIODIC_SAVE_FILE.write("{0}\n".format(output))
                    if self.wideningSearch.IsChecked():
                        if not self.FLAG_ERROR:
                            tmp = Thread(target=self.timerProcessError, args=())
                            tmp.daemon = True
                            tmp.start()

                if self.CAPTURE_ALL_PROCESS_FLAG:
                    p.stdin.write('\x03')
        except Exception:
            self.text.AppendText("Capture of Error Process Terminated \n")
            self.text.AppendText(Utility.LINE)
        finally:
            p.terminate()

    def captureErrorStartButtonFunc(self, event):
        """
        This method starts with press to Capture for errors button. It is searching error which is streaming
        logs result.
        :param event: Standart wx argument
        """
        if self.lstApp.GetSelection() == -1:
            wx.MessageBox("You must select App name !!!", caption="Warning...")
            return

        command = CommandProc.getAppLogCommand(self.SELECTED_APP)
        processName = "captureErrorProcess_{0}".format(self.SELECTED_APP)

        if self.checkThreadNames(processName):
            self.text.AppendText("This Process already Exist, you can stop all > {0}\n".format(processName))
            self.text.AppendText(Utility.LINE)
            return

        t = processOrg(name=processName, target=self.captureStartErrorProcess, args=(command, self.SELECTED_APP,))
        t.daemon = True
        t.start()

        self.PROCESSES.append(t)
        self.text.AppendText("Process started  For Errors > {0}\n".format(processName))
        self.text.AppendText(Utility.LINE)

    def captureAllProcess(self, command, space):
        """
        This method create to captureAllLogsButtonFunc() sub process
        :param command: This argument will pass with releated thread
        """
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            while True:
                output = p.stdout.readline()
                self.textOfLogs.AppendText("{0} > {1}\n".format(space, output))
                if self.periodicSave.IsChecked():
                    ConfigParser.PERIODIC_SAVE_FILE.write("{0}\n".format(output))
                if self.CAPTURE_ALL_PROCESS_FLAG:
                    p.stdin.write('\x03')
        except Exception:
            self.text.AppendText("Capture of All Log Process Terminated \n")
            self.text.AppendText(Utility.LINE)
        finally:
            p.terminate()

    def captureAllLogsButtonFunc(self, event):
        """
        This method starts with press to Capture all logs button. It gets all logs which is streaming
        logs result.
        :param event: Standart wx argument
        """
        if self.lstApp.GetSelection() == -1:
            wx.MessageBox("You must select App name !!!", caption="Warning...")
            return

        command = CommandProc.getAppLogCommand(self.SELECTED_APP)
        processName = "captureAllProcess_{0}".format(self.SELECTED_APP)

        if self.checkThreadNames(processName):
            self.text.AppendText("This Process already Exist, you can stop all > {0}\n".format(processName))
            self.text.AppendText(Utility.LINE)
            return

        t = processOrg(name=processName, target=self.captureAllProcess, args=(command, self.SELECTED_APP,))
        t.daemon = True
        t.start()

        self.PROCESSES.append(t)
        self.text.AppendText("Process started > {0}\n".format(processName))
        self.text.AppendText(Utility.LINE)

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

    def onListBox(self, event):
        """
        This method set selected org to propertyy.
        :param event: Standart wx argument
        """
        self.text.write("Orgs Selected : {0} \n".format(event.GetEventObject().GetStringSelection()))
        self.ORG_SELECTION = event.GetEventObject().GetStringSelection()
        self.text.AppendText(Utility.LINE)

    def onSpaceListBox(self, event):
        """
        This method set selected space to propertyy.
        :param event: Standart wx argument
        """
        self.text.write("Space Selected : {0} \n".format(event.GetEventObject().GetStringSelection()))
        self.SELECTED_SPACE = event.GetEventObject().GetStringSelection()
        self.text.AppendText(Utility.LINE)

    def onAppListBox(self, event):
        """
        This method set selected value to propertyy.
        :param event: Standart wx argument
        """
        self.text.write("App Selected : {0} \n".format(event.GetEventObject().GetStringSelection()))
        self.SELECTED_APP = event.GetEventObject().GetStringSelection()
        self.text.AppendText(Utility.LINE)


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
        if self.SPACES.__len__() != 0:
            self.selectButton.Enable()
        self.text.AppendText(Utility.LINE)

    def onSelectButton(self, event):
        """
        This method set the space from list of selected space name.
        :param event: Standart wx argument
        """
        if self.lstSpace.GetSelection() == -1:
            wx.MessageBox("You must select Space !!!", caption="Warning...")
            return

        self.lstApp.Clear()
        command = Utility.getSpaceSetCommand(self.SELECTED_SPACE)
        result = CommandProc.sendCommandGetResponse(command)
        self.text.AppendText(result)
        self.text.AppendText(Utility.LINE)
        self.selectButton.Label = "Selected"
        resultOfSpace = CommandProc.getSpaceState()
        self.text.AppendText(resultOfSpace)
        self.text.AppendText(Utility.LINE)
        self.lstApp.AppendItems(CommandProc.parseAppNames(resultOfSpace))

    def onPeriodicSaveClicked(self, dummy):
        if self.periodicSave.IsChecked():
            fileName = "{0}log_persis{1}_.log".format(ConfigParser.LOG_SAVE_PATH, datetime.today().strftime("%Y_%m_%d_%H_%M_%S"))
            ConfigParser.PERIODIC_SAVE_FILE = open(fileName, 'w')
            self.text.write("Persistence logs write this file > {0}\n".format(fileName))
        else:
            ConfigParser.PERIODIC_SAVE_FILE.close()
            self.text.write("Persistence logs terminated...\n")
        self.text.AppendText(Utility.LINE)

    def onWideningSearchClicked(self, dummy):
        if self.wideningSearch.IsChecked():
            self.text.write("Widening Search has been started... \n")
        else:
            self.text.write("Widening Search has been terminated... \n")
        self.text.AppendText(Utility.LINE)

    def OnExitApp(self, event):
        """
        This method close button of form. It is destroy to pannel arguments and Frame process.
        :param event: Standart wx argument
        """
        self.Destroy()