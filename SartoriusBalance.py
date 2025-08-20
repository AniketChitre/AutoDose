import serial

class Sartorius(serial.Serial):
    def __init__(self, com_port):
        """
        Initialise Sartorius device.

            Example:
            scale = Sartorius('COM1')
        """
        serial.Serial.__init__(self, com_port)
        self.baudrate = 9600
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = 7
        self.parity = serial.PARITY_ODD
        self.xonxoff=False
        self.rtscts=False 
        self.dsrdtr=False
        self.timeout = 0.5


    def test_connection(self):
        try:
            print(f"Bytes waiting: {self.inWaiting()}")
            self.write(b'\033Q\r')
            raw = self.readline()
            print(f"Raw response: {raw}")
            print(f"Decoded: {raw.decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"Error: {e}")

    def value(self):
        """
        Return displayed scale value.
        """
        try:
            if self.inWaiting() == 0:
                self.write(b'\033P\n')
            answer = self.readline().decode('utf-8')
            if len(answer) == 16: # menu code 7.1.1
                answer = float(answer[0:11].replace(' ', ''))
            else: # menu code 7.1.2
                answer = float(answer[6:17].replace(' ',''))
            return answer
        except:
            return "NA"

    def display_unit(self):
        """
        Return unit.
        """
        self.write(b'\033P\n')
        answer = self.readline()
        try:
            answer = answer[11].strip()
        except:
            answer = ""
        return answer

    def tara_zero(self):
        """
        Tara and zeroing combined.
        """
        self.write(b'\033T\n')

    def tara(self):
        """
        Tara.
        """
        self.write(b'\033U\n')

    def zero(self):
        """
        Zero.
        """
        self.write(b'\033V\n')