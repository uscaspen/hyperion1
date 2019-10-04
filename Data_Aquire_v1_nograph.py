import serial
from multiprocessing import Process, Queue
import time
import csv
import xlsxwriter
import subprocess
import pyfiglet
from colorama import Fore, Back, Style
import os
import signal

fulldatastrings = []
timedata = []
avgs = []
newlist = []
num = 0
qmain = 1


def establishserial(comport, baud):
    try:
        ser = serial.Serial(comport, baudrate=baud, parity=serial.PARITY_NONE, stopbits=1, timeout=4)
        return ser
    except:
        printerror('Serial No Go OwO\n')


def getconfigfile():
    filepath = input("What Is The File Path Of The Configuration?: ")
    lineList = [line.rstrip('\n') for line in open(filepath)]
    configdata = [lineList[1], lineList[3], lineList[5], lineList[7], lineList[9], lineList[11], lineList[13],
                  lineList[15], lineList[17], lineList[19], lineList[21], lineList[23], lineList[25], lineList[27]]

    return configdata, filepath


def getcsvlist(csvfile):
    #print(csvfile)
    data = []
    try:
        with open(csvfile, newline='') as cs:
            readCSV = csv.reader(cs, delimiter=',')
            for row in readCSV:
                data.append(row)
        return data
    except:
        print("CSV did not load")


def gettestnumber():
    testnumber = input("What is the number of this test?: ")
    return testnumber


def getdata(testnumb, comportlogging, baudratecontrol,q):
    ser = establishserial(comportlogging, int(baudratecontrol))
    num = 0
    r = True
    try:
        while r is True:
            if q.empty() is True:
                data = ser.readline()[:-2]  # the last bit gets rid of the new-line chars
                utfdata = str(time.clock())+" "+str(data, 'utf-8', errors='ignore')
                fulldatastrings.append(utfdata)
            else:
                r = False
                with open('AspenDaqData_raw_{}.txt'.format(testnumb), 'w', newline='') as f:
                    writer = csv.writer(f, dialect='excel')
                    for row in fulldatastrings:
                        newrow = row.split(' ')
                        writer.writerow(newrow)
    except:
        printerror("multiprocessing broke")


def threaddata(testnumber, comportlogging, baudratelogging, q):
    process = Process(target=getdata, args=(testnumber, comportlogging, baudratelogging, q))
    process.daemon = True
    process.start()
    return process


def startcontrol(configdata):
    controlpath = str(configdata[0])
    proc = subprocess.Popen(['python', '{}'.format(controlpath), '{}'.format(configdata)], shell=True)
    return proc


def processalldata(csvfile, tempsensorrange, numbbitsthermocouple, forcesensorrange, numbbitsforce,
                   numbbitspressure, pressuresensorrange):
    tempsensorrange = int(tempsensorrange)
    numbbitsthermocouple = int(numbbitsthermocouple)
    forcesensorrange = int(forcesensorrange)
    numbbitsforce = int(numbbitsforce)
    numbbitspressure = int(numbbitspressure)
    pressuresensorrange = int(pressuresensorrange)
    timelist = []
    adc1alist = []
    adc1blist = []
    adc2alist = []
    adc2blist = []
    adc3alist = []
    adc3blist = []
    adc4alist = []
    adc4blist = []
    adc4clist = []
    try:
        vallist = getcsvlist((csvfile+".txt"))
    except:
        printerror("Couldnt Get Vals From Value List")

    for i in vallist:
        try:
            timeval = i[0]
            timelist.append(timeval)
            adc1a = int(i[1])
            adc1alist.append(processtemp(adc1a, tempsensorrange, numbbitsthermocouple))
            adc1b = int(i[2])
            adc1blist.append(processtemp(adc1b, tempsensorrange, numbbitsthermocouple))
            adc2a = int(i[3])
            adc2alist.append(processtemp(adc2a, tempsensorrange, numbbitsthermocouple))
            adc2b = int(i[4])
            adc2blist.append(processtemp(adc2b, tempsensorrange, numbbitsthermocouple))
            adc3a = int(i[5])
            adc3alist.append(processpressure1(adc3a, pressuresensorrange, numbbitspressure))
            adc3b = int(i[6])
            adc3blist.append(processpressure2(adc3b, pressuresensorrange, numbbitspressure))
            adc4a = int(i[7])
            adc4alist.append(processpressure3(adc4a, pressuresensorrange, numbbitspressure))
            adc4b = int(i[8])
            adc4blist.append(processpressure4(adc4b, pressuresensorrange, numbbitspressure))
            adc4c = int(i[9])
            adc4clist.append(processforce(adc4c, forcesensorrange, numbbitsforce))
        except:
            printerror("Process Data Broke:{}".format(i))
    try:
        createexcelsheet(csvfile, timelist, adc1alist, adc1blist, adc2alist, adc2blist, adc3alist, adc3blist,
                     adc4alist, adc4blist, adc4clist)
    except:
        printerror("Excel Sheet Killed")


def processtemp(utfvaltemp, tempsensorrange, numbbitsthermocouple):
    try:
        newval = (((utfvaltemp*5)/(2 ^ numbbitsthermocouple))-1.25)/.005
        return newval
    except:
        printerror("Process Temp Failed")


def processpressure1(utfvalpressure, pressuresensorrange, numbbitspt):
    try:
        maxval= 4.996
        v = (maxval * utfvalpressure) / (2 ** numbbitspt)
        newval = ((v - .016871) / .0016610)
        return newval
    except:
        printerror("Process Pressure Failed")

def processpressure2(utfvalpressure, pressuresensorrange, numbbitspt):
    try:
        maxval = 4.988
        v = (maxval * utfvalpressure) / (2 ** numbbitspt)
        newval = ((v - .0024286) / .0016628)
        return newval
    except:
        printerror("Process Pressure Failed")

def processpressure3(utfvalpressure, pressuresensorrange, numbbitspt):
    try:
        maxval = 5.008
        v = (maxval * utfvalpressure) / (2 ** numbbitspt)
        newval = ((v - .0077143) / .0016682)
        return newval
    except:
        printerror("Process Pressure Failed")

def processpressure4(utfvalpressure, pressuresensorrange, numbbitspt):
    try:
        maxval = 5.005
        v = (maxval * utfvalpressure) / (2 ** numbbitspt)
        newval = ((v - .0055714) / .0016675)
        return newval
    except:
        printerror("Process Pressure Failed")


def processforce(utfvalforce, forcesensorrange, numbbitspt):
    try:
        newval = utfvalforce*(forcesensorrange/(2 ^ numbbitspt))
        return newval
    except:
        printerror("Process Force Failed")


def createexcelsheet(csvfile, timelist, adc1alist, adc1blist, adc2alist, adc2blist, adc3alist, adc3blist,
                     adc4alist, adc4blist, adc4clist):
    print("Started Creation Of Excel Sheet")
    wb = xlsxwriter.Workbook(('{}.xlsx'.format(csvfile)))
    worksheet = wb.add_worksheet('DataSheet')
    worksheetthermo = wb.add_worksheet('Thermocouples')
    worksheetpressure = wb.add_worksheet('PressureSensors')
    worksheetforce = wb.add_worksheet('ForceSensors')
    worksheet.write(0, 0, 'Time Stamp')
    worksheet.write(0, 1, 'Thermocouple 1')
    worksheet.write(0, 2, 'Thermocouple 2')
    worksheet.write(0, 3, 'Thermocouple 3')
    worksheet.write(0, 4, 'Thermocouple 4')
    worksheet.write(0, 5, 'Pressure Transducer 1')
    worksheet.write(0, 6, 'Pressure Transducer 2')
    worksheet.write(0, 7, 'Pressure Transducer 3')
    worksheet.write(0, 8, 'Pressure Transducer 4')
    worksheet.write(0, 9, 'Force Sensor')
    #print(len(timelist))
    #print("Titles are written")
    numrows = len(timelist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 0, (float(timelist[numbrow])-float(timelist[1])))
            printdatarecorded("Time Write Successful")
        except:
            printerror("Time Write Broke")

    numrows = len(adc1alist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 1, str(adc1alist[numbrow]))
            printdatarecorded("Column One Write Successful")
        except:
            printerror("List 1 Write Broke")

    numrows = len(adc1blist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 2, adc1blist[numbrow])
            printdatarecorded("Column Two Write Successful")
        except:
            printerror("List 2 Write Broke")

    numrows = len(adc2alist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 3, adc2alist[numbrow])
            printdatarecorded("Column Three Write Successful")
        except:
            printerror("List 3 Write Broke")

    numrows = len(adc2blist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 4, adc2blist[numbrow])
            printdatarecorded("Column Four Write Successful")
        except:
            printerror("List 4 Write Broke")

    numrows = len(adc3alist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 5, adc3alist[numbrow])
            printdatarecorded("Column five write successful")
        except:
            printerror("List 5 Write Broke")

    numrows = len(adc3blist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 6, adc3blist[numbrow])
            printdatarecorded("Column six write successful")
        except:
            printerror("List 6 Write Broke")

    numrows = len(adc4alist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 7, adc4alist[numbrow])
            printdatarecorded("Column seven write successful")
        except:
            printerror("List 7 Write Broke")

    numrows = len(adc4blist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 8, adc4blist[numbrow])
            printdatarecorded("Column eight write successful")
        except:
            printerror("List 8 Write Broke")

    numrows = len(adc4clist)
    for numbrow in range(1, numrows):
        try:
            worksheet.write(numbrow, 9, adc4clist[numbrow])
            printdatarecorded("Column Nine Write Successful")
        except:
            printerror("List 9 Write Broke")

    try:
        chart1 = wb.add_chart({'type': 'line'})
        chart1.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc1alist)),
            'values': '=DataSheet!$B$2:$B${}'.format(len(adc1alist)),
            'line': {'width': .25},
        })
        chart1.set_title({'name': 'Thermocouple One'})
        chart1.set_x_axis({'name': 'Time(s)', 'num_font':  {'name': 'Arial', 'size': 6}})
        chart1.set_y_axis({'name': 'Temperature(C)'})
        chart1.set_style(10)
        worksheetthermo.insert_chart('C4', chart1, {'x_offset': 0, 'y_offset': 0},)
    except:
        printerror("Graph One Was Not Created")

    try:
        chart2 = wb.add_chart({'type': 'line'})
        chart2.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc1blist)),
            'values': '=DataSheet!$C$2:$C${}'.format(len(adc1blist)),
            'line': {'width': .25},
        })
        chart2.set_title({'name': 'Thermocouple Two'})
        chart2.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart2.set_y_axis({'name': 'Temperature(C)'})
        chart2.set_style(10)
        worksheetthermo.insert_chart('K4', chart2, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Two Was Not Created")

    try:
        chart3 = wb.add_chart({'type': 'line'})
        chart3.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc2alist)),
            'values': '=DataSheet!$D$2:$D${}'.format(len(adc2alist)),
            'line': {'width': .25},
        })
        chart3.set_title({'name': 'Thermocouple Three'})
        chart3.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart3.set_y_axis({'name': 'Temperature(C)'})
        chart3.set_style(10)
        worksheetthermo.insert_chart('C19', chart3, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Three Was Not Created")

    try:
        chart4 = wb.add_chart({'type': 'line'})
        chart4.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc2blist)),
            'values': '=DataSheet!$E$2:$E${}'.format(len(adc2blist)),
            'line': {'width': .25},
        })
        chart4.set_title({'name': 'Thermocouple Four'})
        chart4.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart4.set_y_axis({'name': 'Temperature(C)'})
        chart4.set_style(10)
        worksheetthermo.insert_chart('K19', chart4, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Four Was Not Created")

    # Pressure Sensor Charts
    try:
        chart5 = wb.add_chart({'type': 'line'})
        chart5.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc3alist)),
            'values': '=DataSheet!$F$2:$F${}'.format(len(adc3alist)),
            'line': {'width': .25},
        })
        chart5.set_title({'name': 'Pressure Sensor One'})
        chart5.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart5.set_y_axis({'name': 'Pressure(PSI)'})
        chart5.set_style(10)
        worksheetpressure.insert_chart('C4', chart5, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Five Was Not Created")

    try:
        chart6 = wb.add_chart({'type': 'line'})
        chart6.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc3blist)),
            'values': '=DataSheet!$G$2:$G${}'.format(len(adc3blist)),
            'line': {'width': .25},
        })
        chart6.set_title({'name': 'Pressure Sensor Two'})
        chart6.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart6.set_y_axis({'name': 'Pressure(PSI)'})
        chart6.set_style(10)
        worksheetpressure.insert_chart('K4', chart6, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Six Was Not Created")

    try:
        chart7 = wb.add_chart({'type': 'line'})
        chart7.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc4alist)),
            'values': '=DataSheet!$H$2:$H${}'.format(len(adc4alist)),
            'line': {'width': .25},
        })
        chart7.set_title({'name': 'Pressure Sensor Three'})
        chart7.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart7.set_y_axis({'name': 'Pressure(PSI)'})
        chart7.set_style(10)
        worksheetpressure.insert_chart('C19', chart7, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Seven Was Not Created")


    try:
        chart8 = wb.add_chart({'type': 'line'})
        chart8.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc4blist)),
            'values': '=DataSheet!$I$2:$I${}'.format(len(adc4blist)),
            'line': {'width': .25},
        })
        chart8.set_title({'name': 'Pressure Sensor Four'})
        chart8.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart8.set_y_axis({'name': 'Pressure(PSI)'})
        chart8.set_style(10)
        worksheetpressure.insert_chart('K19', chart8, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Eight Was Not Created")

    try:
        chart9 = wb.add_chart({'type': 'line'})
        chart9.add_series({
            'categories': '=DataSheet!$A$2:$A${}'.format(len(adc4clist)),
            'values': '=DataSheet!$J$2:$J${}'.format(len(adc4clist)),
            'line': {'width': .25},
        })
        chart9.set_title({'name': 'Force Sensor One'})
        chart9.set_x_axis({'name': 'Time(s)', 'num_font': {'name': 'Arial', 'size': 6}})
        chart9.set_y_axis({'name': 'Force(N)'})
        chart9.set_style(10)
        worksheetforce.insert_chart('A4', chart9, {'x_offset': 0, 'y_offset': 0}, )
    except:
        printerror("Graph Nine Was Not Created")
    wb.close()


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
        ascii_banner = pyfiglet.figlet_format("ASPEN")
        print(Fore.YELLOW + ascii_banner)
        print(Fore.WHITE)
        print("White == Logging Read out")
        print(Fore.YELLOW + "Gold == Control Read out")
        print(Fore.WHITE)
    except:
        printerror("Banner Did Not Print")
    testnumber = gettestnumber()
    configdata, filepath = getconfigfile()
    testnumber = testnumber
    comportlogging = configdata[3]
    baudratelogging = configdata[4]
    numbbitsthermocouple = configdata[7]
    numbbitspressure = configdata[8]
    tempsensorrange = configdata[9]
    pressuresensorrange = configdata[10]
    forcesensorrange = configdata[11]
    numbbitsforce = configdata[12]
    print("Data Gathering Running")
    q = Queue()
    try:
        process = threaddata(testnumber, comportlogging, baudratelogging, q)
    except:
        printerror("Threading Didnt Work")
    try:
        time.sleep(1)
        proc = startcontrol(filepath)
    except:
        printerror("Control Script Has Not Started")
    val = input("Enter Exit Code: \n")
    if int(val) is 1:
        q.put(1)
    try:
        time.sleep(2)
        processalldata(('AspenDaqData_raw_{}'.format(testnumber)), tempsensorrange, numbbitsthermocouple,
                       forcesensorrange, numbbitsforce, numbbitspressure, pressuresensorrange)
    except:
        printerror("Writing To Excel Broke")
        print(Fore.WHITE)
    try:
        proc.kill()
    except:
        printerror("Couldn't Close Control Program")



if __name__ == '__main__':
    main()
