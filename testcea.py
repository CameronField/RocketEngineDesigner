#input into terminal: python3.8 -m venv .venv
#followed by source .venv/bin/activate

from rocketcea.cea_obj import CEA_Obj
import re
import math

def engine_design():
    #Design Parameters
    print("Converging/Diverging Engine Design Parameters")
    print("")
    mass_flow_rate = float(input("Enter Mass Flow Rate (kg/s): "))
    of_ratio = float(input("Enter O/F Ratio: "))
    chamber_pressure = float(input("Enter Chamber Pressure (psia):"))
    exit_pressure = float(input("Enter Exit Pressure (Mpa): "))
    l_star = float(input("Enter Characteristic Length (m): "))
    cone_half_angle = float(input("Enter Nozzle Cone Half Angle (deg): "))
    print("")

    #NASA CEA Calculations
    ispObj = CEA_Obj(oxName='O2(G)', fuelName='RP1_NASA')
    s = ispObj.get_full_cea_output(Pc=[chamber_pressure], MR=[of_ratio], short_output=0, pc_units='psia', output='siunits', fac_CR=None)

    # Use regular expressions to find the required values in the output string
    stagnation_temp_pattern = r"T, K\s*([\d.]+)"
    molar_mass_pattern = r"M, \(1/n\)\s*([\d.]+)"
    gamma_pattern = r"GAMMAs\s*([\d.]+)"

    # Find and print the values
    stagnation_temp = re.search(stagnation_temp_pattern, s)
    molar_mass = re.search(molar_mass_pattern, s)
    gamma = re.search(gamma_pattern, s)

    print("NASA CEA Calculations: ")
    if stagnation_temp and molar_mass and gamma:
        print(f"Stagnation Temperature (K): {stagnation_temp.group(1)}")
        print(f"Molar Mass (kg/kmol): {molar_mass.group(1)}")
        print(f"Specific Heat Ratio (Gamma): {gamma.group(1)}")
        stagnation_temp = float(re.search(stagnation_temp_pattern, s).group(1))
        molar_mass = float(re.search(molar_mass_pattern, s).group(1))
        gamma = float(re.search(gamma_pattern, s).group(1))
    else:
        print("Could not find all the required values in the output. Analysis Failed")
        return

    #Constants
    gas_constant = 8314 #Universal Gas Constant (J/(kmol*K))
    earth_acc = 9.81 #Earth Gravity Constant (m/s^2)
    p_amb = 101325 #Ambient Pressure @ sea level (Pa)

    #Conversions
    chamber_pressure = chamber_pressure/145.038 #convert psia to Mpa

    #Engine Desgin Calculations
    ox_mass_flow_rate = (mass_flow_rate*of_ratio)/(1+of_ratio) #kg/s
    fuel_mass_flow_rate = mass_flow_rate - ox_mass_flow_rate  #kg/s
    throat_area = (mass_flow_rate/chamber_pressure)*math.sqrt((stagnation_temp*gas_constant/molar_mass)/gamma)*(1+((gamma-1)/2))**((gamma+1)/(2*(gamma-1))) #throat area in mm^2
    throat_dia = 2*((throat_area/(10**6))/math.pi)**0.5  #m
    exit_mach = math.sqrt((2*((exit_pressure/chamber_pressure)**-((gamma-1)/gamma)-1))/(gamma-1))
    exit_throat_area_ratio = (1/exit_mach)*((2/(gamma+1))*(1+((gamma-1)/2)*(exit_mach**2)))**((gamma+1)/(2*(gamma-1)))
    exit_area = (throat_area/(10**6))*exit_throat_area_ratio #m^2
    exit_dia = 2*math.sqrt(exit_area/math.pi) #m
    exit_velocity = math.sqrt((2*gas_constant*gamma/(gamma-1))*(stagnation_temp/molar_mass)*(1-((exit_pressure/chamber_pressure))**((gamma-1)/gamma))) #m/s
    isp = exit_velocity/9.8 #sec
    thrust = (mass_flow_rate*exit_velocity+exit_area*((exit_pressure*(10**6))-p_amb))/1000 #kN
    chamber_volume = throat_area*l_star/(10**6) #m^3
    chamber_to_throat_ratio = 8*((throat_dia*100)**-0.6)+1.25
    chamber_area = (throat_area/(10**6))*chamber_to_throat_ratio #m^2
    chamber_length = chamber_volume/chamber_area  #m
    nozzle_length = (exit_dia-throat_dia)/(2*math.tan(cone_half_angle*math.pi/180))  #m

    print("")
    print("Fuel Mass Flow Rate (kg/s): ",fuel_mass_flow_rate)
    print("Oxidizer Mass Flow Rate (kg/s): ",ox_mass_flow_rate)
    print("Throat Area (mm^2): ",throat_area)
    print("Throat Diameter (m): ",throat_dia)
    print("Exit Mach Number: ",exit_mach)
    print("Exit to Throat Area Ratio: ",exit_throat_area_ratio)
    print("Exit Area (M^2): ",exit_area)
    print("Exit Diameter (m): ", exit_dia)
    print("Exit Velocity (m/s): ",exit_velocity)
    print("ISP (sec): ",isp)
    print("Thrust (kN): ",thrust)
    print("Chamber Volume (m^3): ",chamber_volume)
    print("Chamber to Throat Area Ratio: ",chamber_to_throat_ratio)
    print("Chamber Area (m^2): ",chamber_area)
    print("Chamber Length (m): ", chamber_length)
    print("Nozzle Length (m): ",nozzle_length)

    return

engine_design()