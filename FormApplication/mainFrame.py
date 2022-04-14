
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

class processOrg(Thread):
    """
    This class extend and specialized for Thread Class. This extension improved to thread stop() method.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(processOrg, self).__init__(target=target, name=name, args=args)
        self._stopper = Event()

    def stop(self):
        self._stopper.set()

class MainFrame(wx.Frame):
    """
    This class create the main panel form UI
    """
    def __init__(self, title):
        #############################################################################################
        # PANEL INITIALIZATION
        #############################################################################################
        wx.Frame.__init__(self, None, title=title, size=(565, 400), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        #wx.Frame.__init__(self, None, title=title, size=(920, 680), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        panel = wx.Panel(self, wx.ID_ANY)

        #############################################################################################
        # ICON INITIALIZATION
        #############################################################################################
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(".\items\log.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        #############################################################################################
        #OBJECTS DEFINITIONS
        #############################################################################################
        #COMBOBOX
        self.cb = wx.ComboBox(panel, size=(115, 100), choices=[], pos=(1, 1), value="Select Prod")
        #LISTBOX
        self.lst = wx.ListBox(panel, size=(115, 100), style=wx.LB_SINGLE, pos=(5, 30))
        self.lstSpace = wx.ListBox(panel, size=(200, 127), style=wx.LB_SINGLE, pos=(227, 3), choices=["Waiting Process.."])
        self.lstApp = wx.ListBox(panel, size=(170, 140), style=wx.LB_SINGLE, pos=(560, 225))
        #TEXTBOX
        self.text = wx.TextCtrl(panel, size=(550, 220), style=wx.TE_MULTILINE, pos=(5, 147))
        self.textOfLogs = wx.TextCtrl(panel, size=(900, 250), style=wx.TE_MULTILINE, pos=(5, 387))
        self.textKeyword = wx.TextCtrl(panel, size=(170, 20), pos=(740, 3))
        #BUTTON
        self.connectButton = wx.Button(panel, size=(100, 127), pos=(125, 3), label="Connect")
        self.selectButton = wx.Button(panel, size=(127, 127), pos=(427, 3), label="Select")
        self.setKeywordButton = wx.Button(panel, size=(170, 44), pos=(740, 25), label="Set Keyword")
        self.captureStartButton = wx.Button(panel, size=(170, 65), pos=(560, 3), label="Capture Errors")
        self.captureAllButton = wx.Button(panel, size=(170, 65), pos=(560, 73), label="Capture All Logs")
        self.captureWithKeywordButton = wx.Button(panel, size=(170, 65), pos=(740, 73), label="Capture With Keyword")
        self.clearLogsButton = wx.Button(panel, size=(170, 65), pos=(740, 143), label="Clear Logs")
        self.saveLogFileButton = wx.Button(panel, size=(170, 65), pos=(560, 143), label="Save Logs")
        self.breakAllButton = wx.Button(panel, size=(170, 115), pos=(740, 250), label="Stop All")
        #CHECKBOX
        self.wideningSearch = wx.CheckBox(panel, label="Widening Search", pos=(740, 225))
        #LABEL
        wx.StaticText(panel, label="> Actions :", pos=(1, 130))
        wx.StaticText(panel, label="> Logs :", pos=(1, 370))
        wx.StaticText(panel, label="> Apps :", pos=(560, 208))

        #############################################################################################
        #OBJECT BINDING
        #############################################################################################
        #BUTTON BIND
        self.Bind(wx.EVT_BUTTON, self.captureErrorStartButtonFunc, self.captureStartButton)
        self.Bind(wx.EVT_BUTTON, self.captureAllLogsButtonFunc, self.captureAllButton)
        self.Bind(wx.EVT_BUTTON, self.saveLogFileButtonFunc, self.saveLogFileButton)
        self.Bind(wx.EVT_BUTTON, self.onBreakAll, self.breakAllButton)
        self.Bind(wx.EVT_BUTTON, self.onSetKeywordButton, self.setKeywordButton)
        self.Bind(wx.EVT_BUTTON, self.executeButton, self.connectButton)
        self.Bind(wx.EVT_BUTTON, self.onSelectButton, self.selectButton)
        self.Bind(wx.EVT_BUTTON, self.onClearLogsButton, self.clearLogsButton)
        self.Bind(wx.EVT_BUTTON, self.onCaptureKeywordButtonFunc, self.captureWithKeywordButton)
        #LISTBOX BIND
        self.Bind(wx.EVT_LISTBOX, self.onSpaceListBox, self.lstSpace)
        self.Bind(wx.EVT_LISTBOX, self.onAppListBox, self.lstApp)
        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lst)
        #CLOSE BIND
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        #############################################################################################
        #OBJECT PROCESS
        #############################################################################################
        self.lstSpace.Disable()
        self.text.SetEditable(False)
        self.textOfLogs.SetEditable(False)
        self.textKeyword.Value = "Keyword Entry..."
        self.selectButton.Disable()
        self.widgetMaker(self.cb, ConfigParser.PRODS)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.cb, 0, wx.ALL, 5)
        panel.SetSizer(sizer)

        #############################################################################################
        #CLASS PROPERTIES
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
        #wx.MessageBox(event.GetEventObject().GetStringSelection())
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
        self.text.AppendText("Connection URL > {0}".format(connectionUrl))
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
        self.Size = (920, 680)
        resultOfSpace = CommandProc.getSpaceState()
        self.text.AppendText(resultOfSpace)
        self.text.AppendText(Utility.LINE)
        self.lstApp.AppendItems(CommandProc.parseAppNames(resultOfSpace))

    def OnExitApp(self, event):
        """
        This method close button of form. It is destroy to pannel arguments and Frame process.
        :param event: Standart wx argument
        """
        self.Destroy()
