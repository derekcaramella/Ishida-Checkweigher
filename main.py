import serial
import time

workstation = 'Sig 1'  # Identify workstation.

# Ensure baudrate, parity, stopbits, and byteszie are congruent with the Ishida data transfer protocool.
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
    line= ser.readline()  # Read RS-232 output.
    line = str(line.decode('utf-8'))  # Decodes string output.
    if len(line) >= 12:  # If ouput is greater than 13 characters long.
        command = line[0:2]  # First two characters.
        weight = float(line[2:10].lstrip('0'))  # Removes zero padding and converts to a float.
        unit_of_measure = line[10:11]  # Unit of Measure.
        checksum = line[11:13]  #IDK
        second += 5  # Exit loop
        database_tuple = (weight_status_dic[command[1]], weight, unit_of_measure, weight_status_dic[checksum[0]], weight_status_dic[checksum[1]])  # Construct instance.
        print(database_tuple)
    else:
        time.sleep(1)  # Wait one second before trying again.
        second += 1  # Loop through to acquire an instance.
