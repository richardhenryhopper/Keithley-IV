from keithley2400 import Keithley2400
from datetime import datetime
import numpy
import schedule
import time
import sys
import winsound
    
def save_data(data, file_name):
    tempo = datetime.today() # get timestamp
    data_str = str(tempo) # save to string
    
    i = 0
    while i < 2: # loop through data
        data_str = data_str + ',' + str(data[i]) # append string
        i += 1
    pwr = data[0] * data[1]
    res = data[0] / data[1]
    data_str = data_str + ',' + str(res) + ',' + str(pwr) # add resistance & power
    data_str = data_str + '\n' # add new line
    print(data_str) # print data string

    f = open(file_name,'a') # open file           
    f.write(data_str) # write data
    f.close() # close file

def save_header(header_str, file_name):
    f = open(file_name,'a')
    f.write(header_str)
    f.close()

def exit_handler():
    sourceMeter.output_enable('off') # disable output
    sourceMeter.close_com # close come
    sys.exit() # exit program
    sys.exit()

def capture(file_name, low_cur_limit):
    data = sourceMeter.measure() # measure
    if data[1] < low_cur_limit: # exit if current lower than limit
        winsound.Beep(1000, 1000)
        exit_handler()
    save_data(data, file_name) # save data
        
if __name__=="__main__" :
    file_name = 'logfile_CCS_83_F_H10133#06_East_Chip1-5.csv' # log file name
    
    low_voltage = 0.05 # low voltage.
    low_volt_source_range = 0.2 # low voltage range
    low_volt_limit = 0.2 # low voltage limit
    low_curr_limit = 0.01 # low current limit 
    low_curr_sense_range = 0.01 # low current range 
        
    high_volt_source_range = 10 # high voltage range
    high_volt_limit = 10 # high voltage limit
    high_curr_limit = 1 # high current limit 
    high_curr_sense_range = 1 # high current range
     
    low_voltage_limit = 2.8
    voltage_step = 0.05
    voltage_array = numpy.arange(low_voltage_limit,high_volt_limit,voltage_step) #voltage array

    low_curr_limit = 0.01 # low current limit
    open_curr_limit = 0.0001 # open circuit current limit
    
    header_str = 'Timestamp,V[V],I[A],R[Ohms],W[W]\n' # header string
    on_delay = 0.5 # on time delay
    off_delay = 0.5 # off time delay
                                     
    sourceMeter = Keithley2400() # create instance 
    sourceMeter.open_com() # open come

    save_header(header_str,file_name) # save header

    # Low voltage measurement
    sourceMeter.config_source_meter(low_volt_source_range,low_volt_limit,low_curr_sense_range,low_curr_limit) # configure source meter
    sourceMeter.remote_sensing('on') # remote sensing
    
    sourceMeter.setsource_volt(low_voltage) # set voltage
    sourceMeter.output_enable('on') # enable output
    time.sleep(1) # delay
    
    #data = sourceMeter.measure() # measure
    #save_data(data, file_name) # save data
    capture(file_name, open_curr_limit) # capture data
        
    # High voltage measurement
    sourceMeter.config_source_meter(high_volt_source_range,high_volt_limit,high_curr_sense_range,high_curr_limit) # configure source meter
                
    for set_voltage in voltage_array: # loop through voltages
        print('Setting voltage = ' + str(set_voltage)) # print voltage
        sourceMeter.setsource_volt(set_voltage) # set voltage
        sourceMeter.output_enable('on') # enable output
        time.sleep(on_delay) # delay
        capture(file_name, open_curr_limit) # capture data
        #sourceMeter.output_enable('off') # disable output
        #time.sleep(off_delay) # delay
        
    
