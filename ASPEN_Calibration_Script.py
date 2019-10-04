import serial
import time
import pyfiglet
from colorama import Fore, Back, Style
import os
import sys

utfdata = []


def getdata(ser):
    data = ser.readline()[:-2]  # the last bit gets rid of the new-line chars
    utfdata = data.decode("utf-8")
    return utfdata


def processdata(comportlogging, baudratelogging, numbbitspressure, typ, i, ptnum, maxval):
    ser = establishserial(comportlogging, baudratelogging)
    v = 0
    v=float(v)
    print(typ)
    print(ptnum)
    if typ is 1:
        v = i*(5*(10**(-3))+1.25)
        print(v)
        refrenceval = (v/5)*(2**numbbitspressure)
        print(refrenceval)
        refrenceval = int(refrenceval)
    else:
        print("made it")
        if ptnum is 1:
            print("in loop 1")
            v = (.0016610 * i)+.0168571
            print(v)
        if ptnum == 2:
            v = (.0016628 * i) + .0024286
        if ptnum == 3:
            v = (.0016682 * i) + .0077143
        if ptnum == 4:
            v = (.0016675 * i) + .0055714
        refrenceval = ((v)*(2**16))/maxval
        refrenceval=int(refrenceval)

    #print(refrenceval)
    iterval = 0
    diffr=[]
    while True:
        try:
            time.sleep(.1)
            val = getdata(ser)
            time.sleep(.1)
            result = val.split(" ")
            if len(result) is 9:
                print (result)
                res = result[ptnum+3]
            #if int(result[iterval]) < (refrenceval-10):
            #    printoutsiderange("TURN RIGHT:{}, {}".format(result[iterval], refrenceval))
            #if int(result[iterval]) > (refrenceval + 10):
            #    printoutsiderange("TURN LEFT:{}, {}".format(result[iterval], refrenceval))
            #if (refrenceval - 10) < int(result[iterval]) < (refrenceval + 10):
            #    printinrange("CALIBRATED:{}".format(result[iterval]))
                printoutsiderange("{}".format(int(res)))
                diffr.append(int(res))
        except KeyboardInterrupt:
            avg = (sum(diffr)/len(diffr))
            print("complete")
            printinrange("Average diffrence: {}".format(avg))
            sys.exit()


def establishserial(comport, baud):
    try:
        ser = serial.Serial(comport, baudrate=baud, parity=serial.PARITY_NONE, stopbits=1, timeout=4)
        return ser
    except:
        printerror('Serial No Go OwO\n')
        sys.exit()


def getconfigfile():
    filepath = input("What Is The File Path Of The Configuration?: ")
    try:
        linelist = [line.rstrip('\n') for line in open(filepath)]
        configdata = [linelist[1], linelist[3], linelist[5], linelist[7], linelist[9], linelist[11], linelist[13],
                      linelist[15], linelist[17], linelist[19], linelist[21], linelist[23], linelist[25], linelist[27]]
        return configdata, filepath
    except:
        printerror("Config File Acquisition Failed")



def getreferencevoltage():
    type = input("What type of sensor for this test?: ")
    numb=0
    if type == 'Thermocouple':
        output = input("What temperature is being tested?: ")
        numb = 1
        ptnum = 0
        maxval = 5
    else:
        ptnum = input("What PT is being tested: ")
        output = input("What pressure is being tested: ")
        maxval = input("What is max voltage: ")
        numb = 0
    return numb, float(output), int(ptnum), float(maxval)


def printoutsiderange(val):
    print(Fore.RED + val)
    print(Fore.WHITE)


def printinrange(val):
    print(Fore.GREEN + val)
    print(Fore.WHITE)


def printerror(val):
    print(Fore.RED + val)
    print(Fore.WHITE)


def printdatarecorded(val):
    print(Fore.CYAN + val)
    print(Fore.WHITE)


def main():
    print('\n\n\n\n\n\n\n\n\n\n')
    try:
        os.system('color')
    except:
        print("No Color")
    try:
        ascii_banner = pyfiglet.figlet_format("ASPEN Calibration")
        print(Fore.YELLOW + ascii_banner)
        print(Fore.WHITE)
    except:
        printerror("Banner Did Not Print")
    configdata, filepath = getconfigfile()
    typ, val, ptnum, maxval = getreferencevoltage()
    comportlogging = configdata[3]
    baudratelogging = int(configdata[4])
    numbbitsthermocouple = int(configdata[7])
    numbbitspressure = int(configdata[8])
    tempsensorrange = int(configdata[9])
    pressuresensorrange = int(configdata[10])
    forcesensorrange = int(configdata[11])
    numbbitsforce = int(configdata[12])
    processdata(comportlogging, baudratelogging, numbbitspressure, typ, val, ptnum, maxval)


if __name__ == '__main__':
    main()
