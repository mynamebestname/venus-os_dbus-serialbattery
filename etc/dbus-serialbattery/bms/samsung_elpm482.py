# samsung_elpm482.py
# BMS class implementation for Samsung ELPM482-00005 battery in a 3-battery parallel setup

from .battery import Battery
from utils import read_modbus_register, read_can_value
import struct

class SamsungELPM482(Battery):
    def __init__(self, port, baudrate=9600, data_format="8N1"):
        super().__init__(port, baudrate, data_format)
        
        self.type = "Samsung_ELPM482"
        self.capacity = 14.52  # Total capacity in kWh for 3 batteries in parallel (4.84 kWh each)
        self.voltage = None
        self.current = None
        self.soc = None
        self.soh = None
        self.alarm_status = None
        self.protection_status = None

        # Modbus register mappings for key parameters
        self.modbus_parameters = {
            "voltage": (0x040002, "U16", 0.01),
            "current": (0x040003, "S16", 1),
            "soc": (0x040004, "U16", 1),
            "soh": (0x040005, "U16", 1),
            "alarm_status": (0x040006, "U16", 1),
            "protection_status": (0x040007, "U16", 1),
        }
        
        # Optional CAN frame mappings (if needed)
        self.can_parameters = {
            "voltage": (0x500, 0, "U16", 0.01),
            "current": (0x500, 2, "S16", 1),
            "soc": (0x500, 4, "U8", 1),
            "soh": (0x500, 5, "U8", 1),
            "alarm_status": (0x501, 0, "U16", 1),
            "protection_status": (0x501, 2, "U16", 1),
        }

    def test_connection(self):
        """Tests connectivity to the battery by reading the voltage parameter."""
        try:
            voltage = self.get_voltage()
            if voltage is not None:
                print(f"Connection successful. Voltage: {voltage} V")
                return True
            else:
                print("Failed to read voltage. Connection may not be established.")
                return False
        except Exception as e:
            print(f"Connection test failed with error: {e}")
            return False
    
    def refresh_data(self):
        """Reads and updates all key battery parameters."""
        self.voltage = self.get_voltage()
        self.current = self.get_current()
        self.soc = self.get_soc()
        self.soh = self.get_soh()
        self.alarm_status = self.get_alarm_status()
        self.protection_status = self.get_protection_status()

    def read_value(self, param):
        """Reads a parameter value by Modbus or CAN, based on configuration."""
        if param in self.modbus_parameters:
            register, data_type, scale = self.modbus_parameters[param]
            return read_modbus_register(self.port, register, data_type, scale)
        elif param in self.can_parameters:
            frame_id, byte_offset, data_type, scale = self.can_parameters[param]
            return read_can_value(self.port, frame_id, byte_offset, data_type, scale)
        else:
            print(f"Parameter {param} not found.")
            return None

    def get_max_battery_voltage(self):
        """Returns maximum battery voltage for Samsung ELPM482."""
        return 58.1  # Maximum charge voltage for the battery system

    def get_min_battery_voltage(self):
        """Returns minimum battery voltage for Samsung ELPM482."""
        return 44.8  # Minimum safe discharge voltage for the battery system

    def get_capacity(self):
        """Returns the capacity of the battery system in kWh."""
        return self.capacity

    def get_voltage(self):
        """Returns the current voltage of the battery."""
        return self.read_value("voltage")
    
    def get_current(self):
        """Returns the current flowing in/out of the battery."""
        return self.read_value("current")

    def get_soc(self):
        """Returns the State of Charge (SOC) of the battery."""
        return self.read_value("soc")

    def get_soh(self):
        """Returns the State of Health (SOH) of the battery."""
        return self.read_value("soh")

    def get_temperature(self):
        """Returns the average cell temperature of the battery."""
        return self.read_value("temperature")  # Replace "temperature" with actual parameter if needed

    def get_charge_voltage(self):
        """Returns the recommended charge voltage of the battery."""
        return 54.6  # Nominal charge voltage per battery (assumed; replace if specified differently)

    def get_discharge_voltage(self):
        """Returns the minimum discharge voltage of the battery."""
        return 44.8  # Discharge cutoff voltage for the battery system

    def get_alarm_status(self):
        """Returns the alarm status of the battery."""
        return self.read_value("alarm_status")

    def get_protection_status(self):
        """Returns the protection status of the battery."""
        return self.read_value("protection_status")
    
    def get_max_charge_current(self):
        """Returns maximum allowable charge current for the battery system."""
        return 141  # Approx. max charge current for 3 batteries in parallel at optimal temperature

    def get_max_discharge_current(self):
        """Returns maximum allowable discharge current for the battery system."""
        return 150  # Max discharge current for 3 batteries in parallel

    def to_percentage(self, value, max_value):
        """Utility method to convert a raw value to a percentage of max value."""
        if max_value > 0:
            return (value / max_value) * 100
        else:
            return 0
