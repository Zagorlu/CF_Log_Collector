
class HealtState:
    def __init__(self, recordDate, stage, state, startDate, cpu, memoryUsage, memoryTotal, diskUsage, diskTotal):
        self.__recordDate = recordDate
        self.__stage = stage
        self.__state = state
        self.__startDate = startDate
        self.__cpu = cpu
        self.__memoryUsage = memoryUsage
        self.__memoryTotal = memoryTotal
        self.__diskUsage = diskUsage
        self.__diskTotal = diskTotal

    def getRecordDate(self):
        return self.__recordDate

    def getStage(self):
        return self.__stage

    def getState(self):
        return self.__state

    def getStartDate(self):
        return self.__startDate

    def getCpu(self):
        return self.__cpu

    def getMemoryUsage(self):
        """

        :return:
        """

