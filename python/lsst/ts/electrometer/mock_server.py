import argparse
import logging
import re
import threading
import queue

import serial


class ElectrometerSimulator:
    def __init__(self, port):
        self.port = port
        self.log = logging.Logger(__name__)
        self.buffer = queue.Queue(maxsize=50000)
        self.command_calls = {"*IDN?": self.get_identification}
        self.commands_regexes = [re.compile(r"^(?P<cmd>\*IDN\?)$")]

    def cmd_loop(self):
        while True:
            self.log.debug("reading message")
            rec = self.serial.read_until(b"\r")
            decoded_rec = rec.decode().strip()
            self.log.debug(f"{decoded_rec}")
            for command in self.commands_regexes:
                self.log.debug(f"{command}")
                matched_command = command.match(decoded_rec)
                self.log.debug(f"{matched_command}")
                if matched_command:
                    self.log.debug(f"Matched {decoded_rec}")
                    command_group = matched_command.group("cmd")
                    if command_group in self.command_calls:
                        called_command = self.command_calls[command_group]
                        self.commander.write(called_command().encode())

    def start(self):
        self.log.debug(f"Starting simulator on {self.port}")
        self.commander = serial.Serial(self.port)
        self.log.debug(f"real port is {self.serial.portstr}")
        thread = threading.Thread(target=self.cmd_loop)
        thread.start()

    def stop(self):
        pass

    def get_identification(self):
        return "KEITHLEY INSRUMENTS INC.,MODEL 6517B,4096271,A13/700X\n"


# TODO Make main a classmethod and call it in a script.
def main():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(description="Run the electrometer simulator")
    parser.add_argument("port", type=str, nargs=1, help="The master serial port")
    args = parser.parse_args()
    electrometer_simulator = ElectrometerSimulator(args.port[0])
    electrometer_simulator.log.addHandler(ch)
    electrometer_simulator.start()


if __name__ == "__main__":
    main()
