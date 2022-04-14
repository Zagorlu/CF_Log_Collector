import os
import wx
import wx.adv
import subprocess
import time
import wx.grid as gridlib
from Util import EdgeLogProc
from os import sys, path
from datetime import datetime
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Util.ConfigParser import ConfigParser
from Util.UtilityClasses import Utility
from Util.CommandProc import CommandProc
from threading import *
from Data.processOrg import processOrg



def convertStringToTime(text):
    return datetime.strptime(text, '%Y-%m-%dT%H:%M:%S.%fUTC')

class EdgeLogPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        wx.StaticText(self, label="> Asset List :", pos=(20, 20))
        wx.StaticText(self, label="> File List :", pos=(350, 20))
        wx.StaticText(self, label="> Application Name :", pos=(20, 260))
        wx.StaticText(self, label="> Start Date Time :", pos=(350, 260))
        wx.StaticText(self, label="> End Date Time :", pos=(350, 320))
        wx.StaticText(self, label="> Log Condition :", pos=(700, 260))

        self.assetList = wx.ListBox(self, size=(300, 200), style=wx.LB_SINGLE, pos=(20, 40))
        self.logFileList = wx.ListBox(self, size=(1000, 200), style=wx.LB_MULTIPLE, pos=(350, 40))
        self.loadButton = wx.Button(self, size=(100, 75), pos=(1380, 40), label="Load")
        self.unloadButton = wx.Button(self, size=(100, 75), pos=(1380, 160), label="Unload")
        self.setApplicationName = wx.TextCtrl(self, size=(300, 20), pos=(20, 280))
        self.startTime = wx.adv.TimePickerCtrl(self, size=(120, 20), pos=(350, 280))
        self.startDate = wx.adv.DatePickerCtrl(self, size=(120, 20), pos=(480, 280))
        self.endTime = wx.adv.TimePickerCtrl(self, size=(120, 20), pos=(350, 340))
        self.endDate = wx.adv.DatePickerCtrl(self, size=(120, 20), pos=(480, 340))
        self.containKeyword = wx.TextCtrl(self, size=(650, 20), pos=(700, 280))
        self.filterButton = wx.Button(self, size=(80, 50), pos=(1270, 320), label="Filter")

        self.Bind(wx.EVT_LISTBOX, self.onAssetListBox, self.assetList)
        self.Bind(wx.EVT_LISTBOX, self.onLogFileListBox, self.logFileList)
        self.Bind(wx.EVT_BUTTON, self.onLoadButton, self.loadButton)
        self.Bind(wx.EVT_BUTTON, self.onUnloadButton, self.unloadButton)
        self.Bind(wx.EVT_BUTTON, self.onFilterButton, self.filterButton)

        self.myGrid = gridlib.Grid(self, size=(1500, 300), pos=(1, 400))
        self.myGrid.CreateGrid(15, 3)

        self.myGrid.SetCellFont(0, 0, wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        print self.myGrid.GetCellValue(0, 0)

        self.myGrid.SetColLabelValue(0, "Application Name")
        self.myGrid.SetColSize(0, 200)
        self.myGrid.SetColLabelValue(1, "Time")
        self.myGrid.SetColSize(1, 600)
        self.myGrid.SetColLabelValue(2, "Message")
        self.myGrid.SetColSize(2, 600)


        self.ASSET_NAME_ID_MAP = []
        self.SELECTED_LOG_FILES = []
        self.LIST_OF_GRID_LIST_VIEW_ITEMS = []
        self.ASSET_ID = ""
        self.generateAssetList()

    def convertStringToTime(self, text):
        return datetime.strptime(text, '%Y-%m-%dT%H:%M:%S.%fUTC')

    def generateAssetList(self):
        self.ASSET_NAME_ID_MAP = EdgeLogProc.getAssetListMap()
        for assetItem in self.ASSET_NAME_ID_MAP:
            self.assetList.Append(assetItem[0])


    def onAssetListBox(self, event):
        assetKey = event.GetEventObject().GetStringSelection()
        for key in self.ASSET_NAME_ID_MAP:
            if key[0] in assetKey:
                self.logFileList.Clear()
                self.ASSET_ID = key[1]
                for logFileName in EdgeLogProc.getFileList(self.ASSET_ID):
                    self.logFileList.Append(logFileName)
                break

    def onLogFileListBox(self, event):
        self.SELECTED_LOG_FILES = []
        for index in event.GetEventObject().GetSelections():
            self.SELECTED_LOG_FILES.append(self.logFileList.GetString(index))


    def onLoadButton(self, event):
        self.LIST_OF_GRID_LIST_VIEW_ITEMS = []
        for fileName in self.SELECTED_LOG_FILES:
            self.LIST_OF_GRID_LIST_VIEW_ITEMS += EdgeLogProc.getFileContent(self.ASSET_ID, fileName)

        self.createDataGrid(len(self.LIST_OF_GRID_LIST_VIEW_ITEMS))
        self.setListViewBufferItems()

    def createDataGrid(self, rowCount):
        self.myGrid.Destroy()
        self.myGrid = gridlib.Grid(self, size=(1500, 300), pos=(1, 400))
        self.myGrid.CreateGrid(rowCount, 3)
        self.myGrid.SetCellFont(0, 0, wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        self.myGrid.SetColLabelValue(0, "Application Name")
        self.myGrid.SetColSize(0, 200)
        self.myGrid.SetColLabelValue(1, "Time")
        self.myGrid.SetColSize(1, 600)
        self.myGrid.SetColLabelValue(2, "Message")
        self.myGrid.SetColSize(2, 600)

    def onFilterButton(self, event):
        tempraryList = []
        for row in self.LIST_OF_GRID_LIST_VIEW_ITEMS:

            base = convertStringToTime(row[1])
            start = datetime(self.startDate.GetValue().year, self.startDate.GetValue().month+1, self.startDate.GetValue().day,
                             self.startTime.GetTime()[0], self.startTime.GetTime()[1], self.startTime.GetTime()[2])

            end = datetime(self.endDate.GetValue().year, self.endDate.GetValue().month+1, self.endDate.GetValue().day,
                             self.endTime.GetTime()[0], self.endTime.GetTime()[1], self.endTime.GetTime()[2])

            if self.setApplicationName.Value.strip() in row[0] and \
                    self.containKeyword.Value.strip() in row[2] and end > base > start:
                tempraryList.append(row)

        self.LIST_OF_GRID_LIST_VIEW_ITEMS = tempraryList
        self.createDataGrid(len(self.LIST_OF_GRID_LIST_VIEW_ITEMS))
        self.setListViewBufferItems()


    def setListViewBufferItems(self):
        for i in range(0, len(self.LIST_OF_GRID_LIST_VIEW_ITEMS)):
            self.myGrid.SetCellValue(i, 0, self.LIST_OF_GRID_LIST_VIEW_ITEMS[i][0])
            self.myGrid.SetReadOnly(i, 0, True)
            self.myGrid.SetCellValue(i, 1, self.LIST_OF_GRID_LIST_VIEW_ITEMS[i][1])
            self.myGrid.SetReadOnly(i, 1, True)
            self.myGrid.SetCellValue(i, 2, self.LIST_OF_GRID_LIST_VIEW_ITEMS[i][2])
            self.myGrid.SetReadOnly(i, 2, True)


    def onUnloadButton(self):
        pass