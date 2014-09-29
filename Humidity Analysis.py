__author__ = 'Matt'
import sys

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.dates as mdates
import pylab as pl

import numpy as np

from matplotlib.dates import DateFormatter

sys.path.insert(0, 'C:\\devel\\Ameoba\\version_0.4\\')
import datetime
import AmoebaSensor
import AmoebaSensorTab

import numpy as np


class ImportCSVExperiment():
    def __init__(self,file,instrument,parameter):
        """
        This method imports the humidity and temperature data from the file.
        """
        self.times = []
        self.readings = []

        file = open(file,'r')
        line = file.readline()
        print line
        line.replace(",","")
        print line
        while line!=(instrument+"\n"):
            line = file.readline()
            if line == (instrument+"\n"):
                print "Instrument found."
                subline = file.readline()
                print "Subline = |" + subline + "| Parameter = |" + parameter + "|"
                if subline == parameter+"\n":
                    timeStrings = file.readline()
                    dataStrings = file.readline()
                else:
                    while subline != (parameter+"\n"):
                        print "Parameter found"
                        subline = file.readline()
                        print "Subline = " + subline + " Parameter = " + parameter
                        if subline == (parameter+"\n"):
                            print "Time and data read in."
                            timeStrings = file.readline()
                            dataStrings = file.readline()
        file.close()
        try:
            timeTmp = timeStrings.split(",")
            dataTmp  = dataStrings.split(",")
        except:
            print "File most likely not read in properly."
            return
        for t,d in zip(timeTmp,dataTmp):
            if t!="Time":
                read = AmoebaSensor.Amoeba_reading()
                try:
                    reading = float(d)
                except:
                    print "Exception"
                #  If the last character in the string is a new line, then remove the new line character.
                try:
                    if t[-1] == "\n":
                        t = t[:-1]
                except:
                    print "Exception"
                try:
                    #print t
                    time = datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S.%f")
                    #print time
                    #time = datetime.time.strptime(t,"%H:%M:%S.%f")
                except:
                    try:
                        #  If no decimal after seconds value.
                        time = datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S")
                        #time = datetime.time.strptime(t,"%H:%M:%S")
                    except:
                        print "Exception"
                #print time
                self.times.append(time)
                self.readings.append(reading)

    def zeroTime(self):
        self.diffs = []
        self.diffSeconds = []
        startTime = self.times[0]
        for i in self.times:
            diff = i - startTime
            sec = diff.seconds + (float(diff.microseconds)/1000000)
            self.diffSeconds.append(sec)
            diff = datetime.time(hour= diff.seconds/3600,minute=(diff.seconds/60)-int(diff.seconds/3600)*60,second=diff.seconds%60, microsecond=diff.microseconds)
            self.diffs.append(diff)

    #  Times must be in seconds.
    def meanBetweenTwoTimes(self,startTime,endTime):
        relevantMeasurements = self.betweenTwoTimes(startTime,endTime)
        mean = np.trapz(relevantMeasurements[1],relevantMeasurements[0])/(endTime-startTime)
        return mean

    def betweenTwoTimes(self,startTime,endTime):
        relevantMeasurements = []
        self.zeroTime()
        #  Retrieve Data between those two times.
        measurements = zip(self.diffSeconds,self.readings)
        for i in measurements:
            if i[0] >= startTime and i[0] <= endTime:
                relevantMeasurements.append(i)
        relevantMeasurements = zip(*relevantMeasurements)
        return relevantMeasurements

    def statsBetweenTwoTimes(self,startTime,endTime):
        relevantMeasurements = self.betweenTwoTimes(startTime,endTime)
        mean = self.meanBetweenTwoTimes(startTime,endTime)
        min = np.amin(relevantMeasurements[1])
        max = np.amax(relevantMeasurements[1])
        var = np.var(relevantMeasurements[1])
        return mean, min, max, var


class ImportTimings():
    def __init__(self,timeFile):
        self.times = []
        self.timesSec = []
        print "Import timings."
        file = open(timeFile,'r')
        line = file.readline()
        times = line.split(";")
        #  Remove the line end character from the last data item.
        if times[-1][-1] == '\n':
            times[-1] = times[-1][:-1]
        for t in times:
            t = t.split(":")
            time = datetime.time(hour = int(t[0]), minute= int(t[1]), second=int(float(t[2])), microsecond =int((float(t[2])%1)*1000000))
            self.times.append(time)
            print time
            self.timesSec.append(time.hour*3600+time.minute*60+time.second+float(time.microsecond)/1000000)
            #print time.hour*3600+time.minute*60+time.second+float(time.microsecond)/1000000
        print "Timings imported."

####   Useful code for the main

    #instrument = "Humidity"
    #channelA =  "Humidity Sensor"
    #channelB = "Temperature Sensor"
    #analyse = AnalyseHumidityTempExperiment(file,timeFile,instrument,channelA,channelB)
    #plot = Plotter()
    #plot.add_plot(analyse.experimentA.diffSeconds,analyse.experimentA.readings,'b')
    #plot.add_plot(analyse.experimentB.diffSeconds,analyse.experimentB.readings,'r')
    #plot.plot()

class AnalyseHumidityTempExperiment():
    def __init__(self,experimentFile,timeFile,instrument,paramA,paramB):
        self.experimentA = ImportCSVExperiment(experimentFile,instrument,paramA)
        self.experimentB = ImportCSVExperiment(experimentFile,instrument,paramB)
        self.times = ImportTimings(timeFile)

        meanHumA = self.experimentA.meanBetweenTwoTimes(self.times.timesSec[0],self.times.timesSec[1])
        meanHumB = self.experimentA.meanBetweenTwoTimes(self.times.timesSec[2],self.times.timesSec[3])
        meanHumC = self.experimentA.meanBetweenTwoTimes(self.times.timesSec[3],self.times.timesSec[5])

        meanTmpA = self.experimentB.meanBetweenTwoTimes(self.times.timesSec[0],self.times.timesSec[1])
        meanTmpB = self.experimentB.meanBetweenTwoTimes(self.times.timesSec[2],self.times.timesSec[3])
        meanTmpC = self.experimentB.meanBetweenTwoTimes(self.times.timesSec[3],self.times.timesSec[5])

        print "Humidity: A = " + str(meanHumA) + " B = " + str(meanHumB) + " C = " + str(meanHumC)
        print "Temperature: A = " + str(meanTmpA) + " B = " + str(meanTmpB) + " C = " + str(meanTmpC)

        meanHum = [meanHumA,meanHumB,meanHumC]
        meanTmp = [meanTmpA,meanTmpB,meanTmpC]


    def separateout(self,data):
        curveA = []
        curveB = []
        curveC = []
        for i in data:
            if i[0] >= self.times.timesSec[0] and i[0] <= self.times.timesSec[1]:
                curveA.append(i)
            if i[0] >= self.times.timesSec[2] and i[0] <= self.times.timesSec[3]:
                curveB.append(i)
            if i[0] >= self.times.timesSec[4] and i[0] <= self.times.timesSec[5]:
                curveC.append(i)
        return curveA, curveB, curveC


#  Not working.
class Plotter():
    def __init__(self):
        self.times = []
        self.readings = []
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

    def add_plot(self,x,y,colour):
        self.ax.plot(x,y,c=colour)

    def plot(self):
        plt.show()

class AnalyseReadings():
    def __init__(self):
        print "Init"

    def plot3yAxis(self,fileA,instA,chanA,axisA,fileB,instB,chanB,axisB,fileC,instC,chanC,axisC):
        dataA = ImportCSVExperiment(fileA,instA,chanA)
        dataB = ImportCSVExperiment(fileB,instB,chanB)
        dataC = ImportCSVExperiment(fileC,instC,chanC)

        dataA.zeroTime()
        dataB.zeroTime()
        dataC.zeroTime()

        print min(dataC.readings)
        print max(dataC.readings)

        host = host_subplot(111, axes_class=AA.Axes)
        plt.subplots_adjust(right=0.75)

        par1 = host.twinx()
        par2 = host.twinx()

        offset = 60

        new_fixed_axis = par2.get_grid_helper().new_fixed_axis
        par2.axis["right"] = new_fixed_axis(loc="right",axes=par2,offset=(offset,0))

        par2.axis["right"].toggle(all=True)

        host.set_xlabel("Time")
        host.set_ylabel(axisA)
        par1.set_ylabel(axisB)
        par2.set_ylabel(axisC)

        p1, = host.plot(dataA.diffSeconds,dataA.readings, label=axisA)
        p2, = par1.plot(dataB.diffSeconds,dataB.readings, label=axisB)
        p3, = par2.plot(dataC.diffSeconds,dataC.readings, label=axisC)

        minA = min(dataA.readings) - ((max(dataA.readings)-min(dataA.readings))/10)
        maxA = max(dataA.readings) + ((max(dataA.readings)-min(dataA.readings))/2)

        minB = min(dataB.readings) - ((max(dataB.readings)-min(dataB.readings))/2)
        maxB = max(dataB.readings) + ((max(dataB.readings)-min(dataB.readings))/10)

        minC = min(dataC.readings) - ((max(dataC.readings)-min(dataC.readings))/10)
        maxC = max(dataC.readings) + ((max(dataC.readings)-min(dataC.readings))/10)

        host.set_ylim(minA,maxA)
        par1.set_ylim(minB,maxB)
        par2.set_ylim(minC,maxC)

        host.legend()

        host.axis["left"].label.set_color(p1.get_color())
        par1.axis["right"].label.set_color(p2.get_color())
        par2.axis["right"].label.set_color(p3.get_color())

        plt.draw()
        plt.show()

    def getAllFromThree(self,instrument,channel,file,timeFile):
        experiment = ImportCSVExperiment(file,instrument,channel)
        times = ImportTimings(timeFile)
        meanA, minA, maxA, varA = experiment.statsBetweenTwoTimes(times.timesSec[0],times.timesSec[1])
        meanB, minB, maxB, varB = experiment.statsBetweenTwoTimes(times.timesSec[2],times.timesSec[3])
        meanC, minC, maxC, varC = experiment.statsBetweenTwoTimes(times.timesSec[4],times.timesSec[5])
        print "Mean :pH 4 = " + str(meanA) + " pH 7 = " + str(meanB) + " pH 10 = " + str(meanC)
        print "Min :pH 4 = " + str(minA) + " pH 7 = " + str(minB) + " pH 10 = " + str(minC)
        print "Max :pH 4 = " + str(maxA) + " pH 7 = " + str(maxB) + " pH 10 = " + str(maxC)
        print "Variance :pH 4 = " + str(varA) + " pH 7 = " + str(varB) + " pH 10 = " + str(varC)

    def meanTemp(self,file,inst,chan):
        experiment = ImportCSVExperiment(file,inst,chan)
        experiment.zeroTime()
        mean, min, max, var = experiment.statsBetweenTwoTimes(experiment.diffSeconds[0],experiment.diffSeconds[-1])
        print mean
        print min
        print max
        print var

    def createPlot(self):
        self.plot = Plotter()

    def addPlot2D(self,inst,chan,colour,file):
        experiment = ImportCSVExperiment(file,inst,chan)
        experiment.zeroTime()
        self.plot.add_plot(experiment.times,experiment.readings,colour)

    def showPlot(self):
        self.plot.plot()

def main():
    print "Running."
    #file = "C:\\Users\\Matt\\Dropbox\\PhD\\AMOEBA 2\\pH\\Calibration with 10K.csv"
    #timeFile = "C:\\Users\\Matt\\Dropbox\\PhD\\AMOEBA 2\\pH\\Calibration with 10K_times.csv"
    #threePlot = "C:\\Users\\Matt\\Dropbox\\PhD\\AMOEBA 2\\pH\\7 regulated with humidity and temperature.csv"
    file = "C:\\Users\\Matt\\Dropbox\\PhD\\AMOEBA 2\\Over night runs\\2 9 14 run 3 point 1.csv"
    analy = AnalyseReadings()
    #analy.plot3yAxis(threePlot,"Ph Sensor","Ph Sensor","pH",threePlot,"Humidity","Humidity Sensor","Humidity",threePlot,"On Off Valves","Valve 1","CO2 Valve")
    #analy.meanTemp(file,"Ph Sensor","Ph Sensor")

    analy.createPlot()
    analy.plot3yAxis(file,"Ph Sensor","Ph Sensor","pH",file,"Humidity Sensor","Humidity Sensor","Humidity",file,"On Off Valves","Valve 1","CO2 Valve")
    #analy.addPlot2D("Ph Sensor","Ph Sensor","red",file)
    #analy.addPlot2D("Humidity Sensor","Humidity Sensor","red",file)
    #analy.addPlot2D("On Off Valves","Valve 1","blue",file)
    analy.showPlot()

if __name__ =="__main__":
    main()