import serial
import time
import csv
from multiprocessing import Process, Queue
import sys
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

fulldatastrings = []
timedata = []
timevect = []
tc1list = []
tc2list = []
tc3list = []
tc4list = []
pt1list = []
pt2list = []
pt3list = []
pt4list = []
forcelist = []
avgs = []
newlist = []
num = 0
qmain=1
numbbitsthermocouple = 16
numbbitspt = 16
tempsensorrange = 2440
pressuresensorrange = 5000
q = Queue()


def establishserial(comport, baud):
    try:
        ser = serial.Serial(comport, baudrate=baud, parity=serial.PARITY_NONE, stopbits=1, timeout=4)
        return ser
    except:
        print(Fore.RED + "serial no go OwO")
        print(Fore.WHITE)


def makeFig(x_vec, y1_data, line1, identifier='', pause_time=0.01): #Create a function that makes our desired plot
    if line1 == []:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
        # update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()

        # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return line1


#def getdata(ser,testnumb, comportlogging, baudratecontrol,q):
#    num = 0
#    print(Fore.YELLOW + 'Data Gathering Start')
#    print(Fore.WHITE)
#    r = True
#
#    while r == True:
#        try:
#            data = ser.readline()[:-2]  # the last bit gets rid of the new-line chars
#            utfdata = str(time.time())+" "+data.decode("utf-8")
#            fulldatastrings.append(utfdata)
#
#        except KeyboardInterrupt:
#            print(Fore.YELLOW + num)
#            print(Fore.WHITE)
#            r = False
#            with open('AspenDaqdata.txt', 'w', newline='') as f:
#                writer = csv.writer(f, dialect='excel')
#                for row in fulldatastrings:
#                    newrow=row.split(' ')
#                    writer.writerow(newrow)


def liveplotting(ser, numbbitsthermocouple):
    num = 0
    print(Fore.YELLOW + 'Data Gathering Start')
    print(Fore.WHITE)
    r = True
    line1=[]
    fig = plt.figure()
    ax1 = fig.add_subplot(331)
    ax2 = fig.add_subplot(332)
    ax3 = fig.add_subplot(333)
    ax4 = fig.add_subplot(334)
    ax5 = fig.add_subplot(335)
    ax6 = fig.add_subplot(336)
    ax7 = fig.add_subplot(337)
    ax8 = fig.add_subplot(338)
    ax9 = fig.add_subplot(339)

    while r == True:
        try:
            data = ser.readline()[:-2]  # the last bit gets rid of the new-line chars
            utfdata = str(time.clock())+" "+str(data, 'utf-8', errors='ignore')
            fulldatastrings.append(utfdata)
            tim, tc1, tc2, tc3, tc4, pt1, pt2, pt3, pt4, forc = splitdata(utfdata, numbbitsthermocouple)
            timevect.append(tim)
            tc1list.append(tc1)
            tc2list.append(tc2)
            tc3list.append(tc3)
            tc4list.append(tc4)
            pt1list.append(pt1)
            pt2list.append(pt2)
            pt3list.append(pt3)
            pt4list.append(pt4)
            forcelist.append(forc)



        except KeyboardInterrupt:
            print(Fore.YELLOW + num)
            print(Fore.WHITE)
            r = False
            with open('AspenDaqdatagraphing.txt', 'w', newline='') as f:
                writer = csv.writer(f, dialect='excel')
                for row in fulldatastrings:
                    newrow = row.split(' ')
                    writer.writerow(newrow)


def animate(i, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9):
    xar = timevect
    tc1graph = tc1list
    tc2graph = tc2list
    tc3graph = tc3list
    tc4graph = tc4list
    pt1graph = pt1list
    pt2graph = pt2list
    pt3graph = pt3list
    pt4graph = pt4list
    forcegraph = forcelist
    ax1.clear()
    ax1.plot(xar, tc1graph)
    ax2.clear()
    ax2.plot(xar, tc2graph)
    ax3.clear()
    ax3.plot(xar, tc3graph)
    ax4.clear
    ax4.plot(xar, tc4graph)

def sendtest(ser, testpath):
    filepath = testpath
    try:
        comList = [line.rstrip('\n') for line in open(filepath)]
        numcommands = len(comList)
        print(Fore.YELLOW + comList)
        print(Fore.WHITE)
        try:
            for com in comList:
                ser.write((com+'\n'))
                time.sleep(20)  # waits so that board can catch up
            ser.write("00000000000")
        except:
            printerror("Commands Where Not Sent Please Exit Program")
    except:
        printerror("couldnt get commands from command file")

def splitdata(utfval,numbbitsthermocouple):
    val = utfval.split()
    time = float(val[0])
    tc1 = float(val[1])
    tc2 = float(val[2])
    tc3 = float(val[3])
    tc4 = float(val[4])
    pt1 = float(val[5])
    pt2 = float(val[6])
    pt3 = float(val[7])
    pt4 = float(val[8])
    forc = float(val[9])
    tc1new = processtemp(tc1, numbbitsthermocouple)
    tc2new = processtemp(tc2, numbbitsthermocouple)
    tc3new = processtemp(tc3, numbbitsthermocouple)
    tc4new = processtemp(tc4, numbbitsthermocouple)
    pt1new = processpressure1(pt1)
    pt2new = processpressure2(pt2)
    pt3new = processpressure3(pt3)
    pt4new = processpressure4(pt4)
    forcenew = processforce(forc)
    return time, tc1new, tc2new, tc3new, tc4new, pt1new, pt2new, pt3new, pt4new, forcenew


def processtemp(utfvaltemp, numbbitsthermocouple):
    v = (5*utfvaltemp)/(2^numbbitsthermocouple)
    newval= (v-1.25)/(5*(10**-3))
    return newval


def processpressure1(utfvalpressure):
    maxval = 4.996
    v = (maxval*utfvalpressure)/(2 ** numbbitspt)
    newval=((v-.016871)/.0016610)
    return newval


def processpressure2(utfvalpressure):
    maxval = 4.988
    v = (maxval * utfvalpressure) / (2 ** numbbitspt)
    newval = ((v - .016871) / .0016610)
    return newval

def processpressure3(utfvalpressure):
    maxval = 5.008
    v = (maxval * utfvalpressure) / (2 ** numbbitspt)
    newval = ((v - .016871) / .0016610)
    return newval

def processpressure4(utfvalpressure):
    maxval = 5.005
    v = (maxval * utfvalpressure) / (2 ** numbbitspt)
    newval = ((v - .016871) / .0016610)
    return newval


def processforce(utfvalforce):
    #newval = utfvalforce*(pressuresensorrange/(2 ^ numbbitspt))
    newval = 0
    return newval


def getconfigfile(filepath):
    #Is coming in as string figure out how to split back into list
    lineList = [line.rstrip('\n') for line in open(filepath)]
    configdata = [lineList[1], lineList[3], lineList[5], lineList[7], lineList[9], lineList[11], lineList[13],
                  lineList[15], lineList[17], lineList[19], lineList[21], lineList[23], lineList[25], lineList[27]]
    print(Fore.YELLOW + configdata[0])
    print(Fore.WHITE)
    return configdata


def printerror(val):
    print(Fore.RED + val)
    print(Fore.YELLOW)


def printdatarecorded(val):
    print(Fore.CYAN + val)
    print(Fore.YELLOW)


def main(configpath):

    print(Fore.YELLOW + "Starts\n")
    print(Fore.YELLOW + configpath)
    try:
        try:
            print(Fore.YELLOW + "Starting command and")
            configdata = getconfigfile(configpath)
            print(Fore.YELLOW + "Config Gotten By Display And Control")
            print(Fore.WHITE)
            comportcontrol = configdata[5]
            baudratecontrol = configdata[6]
            numbbitsthermocouple = configdata[7]
            numbbitspressure = configdata[8]
            tempsensorrange = configdata[9]
            pressuresensorrange = configdata[10]
            forcesensorrange = configdata[11]
            numbbitsforce = configdata[12]
            testpath = configdata[13]
        except:
            printerror("Config File Could Not Be Read By Display And Control")
        try:
            ser = establishserial(comportcontrol, baudratecontrol)
            print(Fore.YELLOW + "Serial Started")
            print(Fore.WHITE)
        except:
            printerror("Serial Did Not Start")
        try:
            sendtest(ser, testpath)
        except:
            printerror("Test Not Sent")
        liveplotting(q, ser, numbbitsthermocouple)
    except:
        printerror("Data Display And Control Did Not Function")


if __name__ == '__main__':
    main(sys.argv[1])
