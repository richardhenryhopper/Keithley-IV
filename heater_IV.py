from keithley2400 import Keithley2400
from datetime import datetime
import numpy
import time
import math

keithley2400 = Keithley2400() # Create instrument instance

class HeaterIv:
    v_max = 3 # Voltage limit
    i_amb = 3 # Ambient current (mA)
    i_array = [] # Current array
    t_amb = 25 # Ambient temperature
    on_delay = 0.5 # Warmup delay
        
    #TCR values - 113C CVD
    tcr1 = 2.05e-3
    tcr2 = 3.00e-7
    trh = 0.766
    trm = 0.928
    
    def __init__(self):
        pass
                        
    def save_data(self, data_str, file_name):      
        f = open(file_name, 'a') # Open file           
        f.write(data_str + '\n') # Write data
        f.close() # Close file

    # Method to calculate temperature of TC sensor
    def temp_tc_sensor(self, R_heated, res_heater=36, res_track_on=9, res_track_off=3+2.5):
        res_heat = res_heater + res_track_on/3
        res_non_heat = res_track_on*2/3 + res_track_off
        R_heated = R_heated - res_non_heat
        TCR1 = -4.478e-3 * res_heat/340 + 3.7765e-3
        TCR2 = 0.4e-6
        T_heat = (-TCR1 + math.sqrt(TCR1**2 - 4*TCR2*(1-R_heated/res_heat)))/(2*TCR2)+25
        return T_heat

    # Method to calculate temperature of microheater 
    def calc_temp(self, iamb, vamb, i, v):
        self.t_amb = 25
        Rm0 = vamb / iamb
        Rh0 = Rm0 * self.trh
        vcalc = i * ( Rh0 + ( v / i - Rm0 ) * self.trm ) 
        c = 1 - ( ( vcalc / i ) / Rh0 )
        t = ( ( -self.tcr1 + math.sqrt ( self.tcr1 * self.tcr1 - 4 * self.tcr2 * c ) ) / 2 / self.tcr2 ) + self.t_amb
        return t

    def open_com(self, resource_name):
        # Open COM
        keithley2400.open_com(resource_name) 
            
    def config(self, i_start, i_stop, i_step, remoteSense = True):
        self.i_array = numpy.arange(i_start, i_stop, i_step) # Create current array
                
        keithley2400.config_sourcemeter_cur(volt_sense_prot = self.v_max, volt_sense_range = self.v_max, cur_source_range = i_stop)
        if remoteSense == True:
            keithley2400.remote_sensing('on') # Config remote sensing
        else:
            keithley2400.remote_sensing('off') # Config remote sensing

    def run(self, file_name):
        header_str = 'Timestamp,Current[A],Voltage[V],Resistance[Ohms],Power[W],Temperature[°C]' # Create header string
        self.save_data(header_str, file_name) # Save header string
        
        # Ambient IV capture
        keithley2400.setsource_cur(self.i_amb/1000) # Set ambient current
        keithley2400.output_enable('on') # Enable output
        time.sleep(self.on_delay) # Delay
        i_amb, v_amb = keithley2400.measure_iv() # Capture ambient data
         
        for set_i in self.i_array: # Loop through current
            keithley2400.setsource_cur(set_i/1000) # Set current
            print("Current = {:.1f} mA".format(set_i)) # Print setpoint
            time.sleep(self.on_delay) # Delay
            i, v = keithley2400.measure_iv() # Capture data
            pwr = i * v # Calculate power 
            res = v / i # Calculate resistance
            t = self.calc_temp(i_amb, v_amb, i, v) # Calculate temperature
            tempo = datetime.today() # Get timestamp
            data_str = str(tempo) + ',' + str(i) + ',' + str(v) + ',' + str(res) + ',' + str(pwr)+ ',' + str(t) # Get data string
            self.save_data(data_str, file_name) # Save data string

        # Disable output & COM port
        keithley2400.output_enable('off')
        keithley2400.close_com()
        
if __name__=="__main__" :
    
    heaterIv = HeaterIv()
    heaterIv.open_com('GPIB0::25::INSTR') 
    heaterIv.config(i_start = 3, i_stop = 100, i_step = 10, remoteSense = True)
    heaterIv.run('test.csv')
     
    
    
    

    
        
    
    
