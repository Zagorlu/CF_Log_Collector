from ConfigParser import ConfigParser
import requests
import json
import re

def getToken():
    r = requests.get(url=ConfigParser.TOKEN_URL, auth=(ConfigParser.TOKEN_USER_NAME, ConfigParser.TOKEN_PASSWORD))
    data = r.json()
    token = data['token']
    return token

def getFileList(assetId):
    fileList = []
    fileUrl = "{0}{1}/".format(ConfigParser.FILE_URL, assetId)
    headers = {"Authorization": "Bearer {0}".format(getToken())}
    r = requests.get(url=fileUrl, headers=headers)
    data = r.json()
    for fileInfo in data:
        fileList.append(fileInfo['name'])
    return fileList

def getFileContent(assetId, fileName):
    """
    :param assetId:
    :param fileName:
    :return: This file return Tuple List. Which tuple is [(APPNAME, REAL_TIME_STAMP, MESSAGE)]
    """
    fileUrl = "{0}{1}/{2}".format(ConfigParser.FILE_URL, assetId, fileName)
    headers = {"Authorization": "Bearer {0}".format(getToken())}
    r = requests.get(url=fileUrl, headers=headers)
    data = json.loads(r.text)
    fileContent = []
    for logObject in data:
        appName = logObject['GUID']
        entryObjects = []
        for entry in logObject['entries']:
            entryObjects.append((entry[0], entry[2]))
        for entryTuple in entryObjects:
            fileContent.append((appName, entryTuple[0], entryTuple[1]))
    return fileContent

def getAssetListMap():
    """
    :return: This function returns tuple list which tuple's size 2. First asset is name&type. Second item is Asset ID [(NAME, ID)]
    """
    fileUrl = ConfigParser.ASSET_LIST_URL
    headers = {"Authorization": "Bearer {0}".format(getToken())}
    r = requests.get(url=fileUrl, headers=headers)
    data = r.json()
    assetMap = []
    for asset in data['base_data']['assets']:
        assetMap.append(("{0} - {1}".format(asset['entity1'], asset['entity2']), asset['entity3']))
    return assetMap
