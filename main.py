import serial
from datetime import datetime
import time
import pyodbc
import settings

con = pyodbc.connect(Trusted_Connection='no',
                     driver='{SQL Server}',
                     server=settings.database_ip,
                     database='Alpha_Live',
                     UID=settings.database_id,
                     PWD=settings.database_password)
cursor = con.cursor()

workstation = 'Sig 1'  # Identify workstation.
timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')

# Ensure baud rate, parity, stop bits, and byte size are congruent with the Ishida data transfer protocol.
ser = serial.Serial(port='/dev/ttyUSB0',
                    baudrate=2400,
                    parity=serial.PARITY_EVEN,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.SEVENBITS,
                    timeout=None)

# Interpret weight status output.
weight_status_dic = {'1': 'Proper', '2': 'Under', '3': 'Over', '4': 'Metal',
                     '5': 'Ext.1', '6': 'Ext.2', '7': 'Pitch Error',
                     '8': '0-Error', '9': 'Cont.NG', ':': 'No Metal',
                     ';': 'OK Under', '<': 'OK Over', '=': 'Under NG',
                     '>': 'Over NG', '@': 'Foreign Object',
                     'A': 'Short Item', 'B': 'Product Length Error',
                     'C': 'Ext.3', 'D': 'Ext.4'}

# Read status output for five seconds, which should account for various line speeds & utilization.
second = 0
while second <= 5:
    line = ser.readline()  # Read RS-232 output.
    line = str(line.decode('utf-8'))  # Decodes string output.
    if len(line) >= 12:  # If output is greater than 13 characters long.
        command = line[0:2]  # First two characters.
        weight = float(line[2:10].lstrip('0'))  # Removes zero padding and converts to a float.
        unit_of_measure = line[10:11]  # Unit of Measure.
        # Checksum: A digit representing the sum of the correct digits in a piece of stored or transmitted digital data.
        check_sum = line[11:13]
        second += 5  # Exit loop
        database_tuple = (timestamp, workstation, weight_status_dic[command[1]], weight, unit_of_measure, check_sum)  # Construct instance.
        cursor.execute('USE [Operations] INSERT INTO [dbo].[Ishida_Weights] VALUES ' + str(database_tuple))
        con.commit()
    else:
        time.sleep(1)  # Wait one second before trying again.
        second += 1  # Loop through to acquire an instance.
