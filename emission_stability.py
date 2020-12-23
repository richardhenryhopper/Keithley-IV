from keithley2400 import Keithley2400
from datetime import datetime
import numpy
import time
import math

keithley2400E = Keithley2400() # Create electrical instrument instance
keithley2400O = Keithley2400() # Create optical instrument instance

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

    def open_com(self, resource_name_elec, resource_name_opt):
        keithley2400E.open_com(resource_name_elec) # Electrical instrument
        keithley2400O.open_com(resource_name_opt) # Optical instrument
            
    def config(self, i_start, i_stop, i_step, remoteSense = True):
        self.i_array = numpy.arange(i_start, i_stop, i_step) # Create current array
                
        keithley2400E.config_sourcemeter_cur(volt_sense_prot = self.v_max, volt_sense_range = self.v_max, cur_source_range = i_stop * 0.001)
        if remoteSense == True:
            keithley2400E.remote_sensing('on') # Config remote sensing
        else:
            keithley2400E.remote_sensing('off') # Config remote sensing

        keithley2400O.config_voltmeter(volt_range = 5) # Config for optical sensing

    def run(self, file_name):
        header_str = 'Timestamp,Current[A],Voltage[V],Resistance[Ohms],Power[W],Temperature[°C],Emission[V]' # Create header string
        self.save_data(header_str, file_name) # Save header string
        
        # Ambient IV capture
        keithley2400E.setsource_cur(self.i_amb * 0.001) # Set ambient current
        keithley2400E.enable() # Enable output
        keithley2400O.enable() # Enable optical voltage sense
        time.sleep(self.on_delay) # Delay
        
        i_amb, v_amb = keithley2400E.measure_iv() # Capture ambient IV data
        v_opt_amb = keithley2400O.measure_v() # Capture ambient optical data
         
        for set_i in self.i_array: # Loop through current
            keithley2400E.setsource_cur(set_i * 0.001) # Set current
            print("Current = {:.1f} mA".format(set_i)) # Print setpoint
            time.sleep(self.on_delay) # Delay
            i, v = keithley2400E.measure_iv() # Capture data
            v_opt = keithley2400O.measure_v() - v_opt_amb # Capture optical data
            pwr = i * v # Calculate power 
            res = v / i # Calculate resistance
            t = self.calc_temp(i_amb, v_amb, i, v) # Calculate temperature
            tempo = datetime.today() # Get timestamp
            data_str = str(tempo) + ',' + str(i) + ',' + str(v) + ',' + str(res) + ',' + str(pwr)+ ',' + str(t) + ',' + str(v_opt) # Get data string
            self.save_data(data_str, file_name) # Save data string

        # Disable output & COM port
        keithley2400E.disable()
        keithley2400O.disable()
        keithley2400E.close_com()
        keithley2400O.close_com()
        
if __name__=="__main__" :
    
    heaterIv = HeaterIv()
    heaterIv.open_com('GPIB0::25::INSTR', 'GPIB0::26::INSTR') 
    heaterIv.config(i_start = 3, i_stop = 110, i_step = 1, remoteSense = True)
    heaterIv.run('Chip83_4260nm_180BW_110mA.csv')
     
    
    
    

    
        
    
    
