"""
| File: ardupilot_launch_tool.py
| Author: Eesh Vij (evij@uci.edu)
| Description: Defines an auxiliary tool to launch the Ardupilot process in the background
"""

# System tools used to launch the ardupilot process in the background
import os
import time
import tempfile
import subprocess


class ArdupilotLaunchTool:
    """
    A class that manages the start/stop of a Ardupilot process. It requires only the path to the Ardupilot installation, the vehicle id and the vehicle model. 
    """

    def __init__(self, enable_logs: bool = False, log_dir: str = None, wipe_eeprom: bool = False, vehicle_id: int = 1, ardupilot_model: str = None):
        """Construct the ArdupilotLaunchTool object

        Args:
            enable_logs (bool): A boolean that indicates whether to enable logs or not. Defaults to False.
            log_dir (str): A string with the path to the logs directory. Defaults to this directory/logs
            wipe_eeprom (bool): A boolean that indicates whether to wipe the eeprom or not. Defaults to False.
            vehicle_id (int): The ID of the vehicle. Defaults to 0.
            ardupilot_model (str): The vehicle model. Defaults to None. # Currently not supported
        """

        
        # Attribute that will hold the ardupilot process once it is running
        self.ardupilot_process = None

        # The vehicle id
        self.vehicle_id = vehicle_id

        # attr for eeprom
        self.wipe_eeprom = wipe_eeprom

        # Enable logs
        self.enable_logs = enable_logs

        # Log dir setup
        if log_dir != None:
            self.log_dir = log_dir
        else:
            # If log_dir is empty we will give it a dir
            self.log_dir = os.path.dirname(os.path.abspath(__file__)) # + "/logs" #/" + time.strftime("%Y%m%d-%H%M%S")
        
        # Create a temporary filesystem for ardupilot to write data to/from (and modify the origin rcS files)
        self.root_fs = tempfile.TemporaryDirectory()

    def launch_ardupilot(self):
        """
        Method that will launch a ardupilot instance with the specified configuration
        """
        parm_path = os.path.dirname(os.path.abspath(__file__)) + "/ardu.parm"
        eeprom = '-w' if self.wipe_eeprom else ''
        logs = f"--aircraft={self.log_dir}" if self.enable_logs else ''
        self.ardupilot_process = subprocess.Popen(
            [
                "sim_vehicle.py",
                "-v",
                "ArduCopter",
                f"--sysid={self.vehicle_id}",
                f"--add-param-file={parm_path}",
                #f"--use-dir={self.log_dir}", # we dont need this
                logs,
                eeprom,
            ],
            cwd=self.root_fs.name,
            shell=False,
        )

    def kill_ardupilot(self):
        """
        Method that will kill a ardupilot instance with the specified configuration
        """
        if self.ardupilot_process is not None:
            self.ardupilot_process.kill()
            self.ardupilot_process = None

    def __del__(self):
        """
        If the ardupilot process is still running when the ardupilot launch tool object is whiped from memory, then make sure
        we kill the ardupilot instance so we don't end up with hanged ardupilot instances
        """

        # Make sure the ardupilot process gets killed
        if self.ardupilot_process:
            self.kill_ardupilot()

        # Make sure we clean the temporary filesystem used for the simulation
        self.root_fs.cleanup()


# ---- Code used for debugging the ardupilot tool ----
def main():

    ardupilot_tool = ArdupilotLaunchTool(enable_logs=True)
    ardupilot_tool.launch_ardupilot()

    import time

    time.sleep(60)


if __name__ == "__main__":
    main()
