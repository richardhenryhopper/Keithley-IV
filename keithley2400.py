#Keithley 2400
#This script enables to communicate with the keithley 2400 and 2401 instruments
#Configurations as voltmeter only and as a voltage current source/current sensing available
#Measurement function also provided
#gpib/rs232 com possible


import pyvisa
import time
import numpy

class Keithley2400:
    data_entry = 5
    trigger_count = 1
    delay = 5
    nplc = 1
    rm = None
    inst = None

    def __init__(self):
        pass
          
    def open_com(self, resourceName):
        self.rm = pyvisa.ResourceManager()
        #print(self.rm.list_resources())
        self.inst = self.rm.open_resource(resourceName) 
        print(self.inst.query('*IDN?'))
                
    def close_com(self):
        #Set instrument in local mode
        res = self.send_cmd("SYST:LOC")
        time.sleep(1)
        #Close instrument connection
        self.inst.close()
        #Close visa session
        res = self.rm.close()
        return res

    def return_command_result(self,command):
        self.inst.write(command)
        result = self.inst.read()
        return result
    
    def send_query(self, command):
        out = self.return_command_result(command)
        #out = self.inst.query(command, self.delay)
        #res = self.inst.query("SYSTem:ERRor?")
        res = self.return_command_result("SYSTem:ERRor?")
        return out

    def send_cmd(self, command):
        res = self.inst.write(command)
        return res

    def config_voltmeter(self):
        res = self.send_cmd("*RST")
        res = self.send_cmd(":SOUR:FUNC CURR")
        res = self.send_cmd(":SOUR:CURR:MODE FIX")
        res = self.send_cmd(":SOUR:CURR:RANGE:AUTO ON")
        res = self.send_cmd(":SOUR:CURR:LEV 0")
        res = self.send_cmd(":SENS:FUNC \"VOLT\"")
        res = self.send_cmd(":SENS:VOLT:PROT 10")
        res = self.send_cmd(":SENS:VOLT:RANG 10")
        res = self.send_cmd(":SENS:VOLT:NPLC " + str(self.nplc))
        res = self.send_cmd(":TRIG:COUN " + str(self.trigger_count))
        return res

    def config_source_meter(self,volt_source_range,volt_limit,curr_sense_range,curr_limit):
        res = self.send_cmd("*RST")
        res = self.send_cmd(":SOUR:FUNC VOLT")
        res = self.send_cmd(":SOUR:VOLT:MODE FIX")
        res = self.send_cmd(":SENS:VOLT:PROT 10")
        res = self.send_cmd(":SOUR:VOLT:RANG " + str(volt_source_range))
        res = self.send_cmd(":SOUR:VOLT:LEV 0")
        res = self.send_cmd(":SENS:FUNC \"CURR\"")
        res = self.send_cmd(":SENS:CURR:PROT " + str(curr_limit))
        res = self.send_cmd(":SENS:CURR:RANG " + str(curr_sense_range))
        res = self.send_cmd(":TRIG:COUN "+str(self.trigger_count))
        return res

    def setsource_volt(self, voltage):
        res = self.send_cmd(":SOUR:VOLT:LEV " + str(voltage))
        return res

    def remote_sensing(self, mode):
        if mode=='on':
            res = self.send_cmd(":SYST:RSEN ON")
        else:
            res = self.send_cmd(":SYST:RSEN OFF")
        return res

    def config_sourcemeter_cur(self, volt_sense_prot,volt_sense_range, cur_source_range ):
        res = self.send_cmd("*RST")
        res = self.send_cmd(":SOUR:FUNC CURR")
        res = self.send_cmd(":SOUR:CURR:MODE FIX")
        res = self.send_cmd(":SOUR:CURR:RANG " + str(cur_source_range))
        res = self.send_cmd(":SOUR:CURR:LEV 0")
        res = self.send_cmd(":SENS:FUNC \"VOLT\"")
        res = self.send_cmd(":SENS:VOLT:PROT " + str(volt_sense_prot))
        res = self.send_cmd(":SENS:VOLT:RANG " + str(volt_sense_range))
        res = self.send_cmd(":TRIG:COUN "+str(self.trigger_count))
        return res

    def setsource_cur(self, current):
        res = self.send_cmd(":SOUR:CURR:LEV " + str(current))
        return res

    def output_enable(self, state):
        if state=='on':
            mes = ':OUTP ON'
            print('Source ON')
        else:
            mes = ':OUTP OFF'
            print('Source OFF')
        res = self.send_cmd(mes)
        return res

    def measure(self):
        try:
            out = self.send_query("READ?")
        except pyvisa.VisaIOError:
            print('The keithley instrument could not complete the read command')
            
        rawdata = numpy.array(out.split(','))
        float_arr = numpy.vectorize(float)
        data = float_arr(rawdata)
        #The assumption here is that the volt and current  are the first 2 columns
        #returned string format
        #volt,curr,res,time,status
        #You can amend it using :FORM:DATA: and :FORM:ELEM See Ch18-48
        #+2.000812E+00,+9.910000E+37,+9.910000E+37,+7.408841E+03,+1.946000E+04
        return data

    def measure_iv(self):
        data = self.measure() # measure
        v, i = data[0], data[1]
        return(i, v)

if __name__ == "__main__":
    keithley2400 = Keithley2400()
    keithley2400.open_com('GPIB0::25::INSTR') 
    keithley2400.close_com()



    
    
