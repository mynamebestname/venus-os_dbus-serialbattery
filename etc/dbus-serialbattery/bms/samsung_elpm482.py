# samsung_elpm482.py
# BMS class implementation for Samsung ELPM482-00005 battery

from .battery import Battery
from utils import read_modbus_register, read_can_value
import struct

class SamsungELPM482(Battery):
    def __init__(self, port, baudrate=9600, data_format="8N1"):
        super().__init__(port, baudrate, data_format)
        
        # Battery configuration and specs
        self.type = "Samsung_ELPM482"
        self.capacity = 14.52  # Total capacity in kWh for 3 batteries in parallel (4.84 kWh each)
        self.nominal_voltage = 51.52  # Based on nominal battery voltage per manual
        self.max_voltage = 58.1       # Max voltage from manual
        self.min_voltage = 44.8       # Min discharge voltage from manual

        # Battery current limits for 3 batteries in parallel
        self.max_charge_current = 141  # 47A per battery × 3
        self.max_discharge_current = 150  # Max discharge current for 3 batteries

        # Initialize battery parameters
        self.voltage = None
        self.current = None
        self.soc = None
        self.soh = None
        self.alarm_status = None
        self.protection_status = None

        # Modbus register mappings based on the manual
        self.modbus_parameters = {
            "voltage": (0x040002, "U16", 0.01),              # Register address, type, scale
            "current": (0x040003, "S16", 1),
            "soc": (0x040004, "U16", 1),
            "soh": (0x040005, "U16", 1),
            "alarm_status": (0x040006, "U16", 1),
            "protection_status": (0x040007, "U16", 1),
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
        """Reads a parameter value from Modbus."""
        if param in self.modbus_parameters:
            register, data_type, scale = self.modbus_parameters[param]
            return read_modbus_register(self.port, register, data_type, scale)
        else:
            print(f"Parameter {param} not found.")
            return None

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

    def get_alarm_status(self):
        """Returns the alarm status of the battery."""
        return self.read_value("alarm_status")

    def get_protection_status(self):
        """Returns the protection status of the battery."""
        return self.read_value("protection_status")

    def get_max_battery_voltage(self):
        """Returns maximum battery voltage for Samsung ELPM482."""
        return self.max_voltage

    def get_min_battery_voltage(self):
        """Returns minimum battery voltage for Samsung ELPM482."""
        return self.min_voltage

    def get_capacity(self):
        """Returns the capacity of the battery system in kWh."""
        return self.capacity

    def get_max_charge_current(self):
        """Returns maximum allowable charge current for the battery system."""
        return self.max_charge_current

    def get_max_discharge_current(self):
        """Returns maximum allowable discharge current for the battery system."""
        return self.max_discharge_current
