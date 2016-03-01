#******************************************************************************
#
#******************************************************************************
from datetime import datetime
from datetime import timedelta
import pytz

#******************************************************************************
class AsciiTimeSeries:
    
    file_name = None
    ascii_file = None
    number_of_records = 0
    current_record = 0
    latitude = 0
    longitude = 0
    interval = None
    startTime = None
    endTime = None


    #******************************************************************************
    def __init__(self, file_name):
        self.file_name = file_name
        
        #Open the file.
        self.ascii_file = open(self.file_name, 'r')
        
        #Skip the header
        self.read_header()


    #******************************************************************************        
    def read_header(self):

        rowCounter = 0

        while True:

            rowCounter += 1

            #Grab the current file location.
            currentLocation = self.ascii_file.tell()

            #Read a line of data
            data = self.ascii_file.readline().strip()

            #If this line does not end with a '||', then we must have hit the beginning of the real data.
            if data.endswith('||') == False:
                self.ascii_file.seek(currentLocation)
                break

            #If this is the 1st row, then lets decode the start date and time.
            if rowCounter == 1:
                
                components = data[:-2].split()

                dateIndex = len(components) - 1
                
                #TODO - find out what format the time is stored... so we can parse it too.
                #timeIndex = dateIndex - 1

                self.startTime = datetime.strptime(components[dateIndex], '%Y/%m/%d')

                #We assume that this is UTC time.
                self.startTime = self.startTime.replace(tzinfo=pytz.utc)

            #If this is the 2nd row, then lets decode the x and y positions.
            elif rowCounter == 2:

                components = data.split()

                if len(components) < 7:
                    raise Exception('Unable to decode position information from header.')

                self.latitude = float(components[1]) + (float(components[2]) * 0.01);
                if components[3] == 'S':
                    self.latitude *= -1.0

                self.longitude = float(components[4]) + (float(components[5]) * 0.01);
                if components[6] == 'W':
                    self.longitude *= -1.0
                
            #If this is the 3rd row, then lets decode the number of records in the file.
            elif rowCounter == 3:
                
                components = data.split()

                if len(components) < 6:
                    raise Exception('Unable to decode count information from header.')

                self.number_of_records = int(components[0])

                decodedTime = datetime.strptime(components[4], '%H%M:%S')
                self.interval = timedelta(hours = decodedTime.hour, minutes = decodedTime.minute,
                                          seconds = decodedTime.second, microseconds = decodedTime.microsecond)


        #With the start time, number of records, and interval... we can figure out the end time.
        self.endTime = self.startTime + (self.number_of_records - 1) * self.interval


    #******************************************************************************
    def done(self):

        if self.current_record < self.number_of_records:
            return False

        return True


    #******************************************************************************
    def read_next_row(self):

        #If we are done... throw an error.
        if self.done():
            raise Exception('AsciiTimeSeries is done!')

        self.current_record += 1
        asciiData = self.ascii_file.readline()

        dateAndTime = None
        direction = None
        speed = None

        #We expect the following: Date (YYYY/MM/DD), HourMinute (hhmm), Direction (deg T), Speed (m/s) 
        components = asciiData.split()
        if len(components) != 4:
            raise Exception('Record does not have the correct number of values.')

        dateAndTime = datetime.strptime(components[0] + components[1], '%Y/%m/%d%H:%M')
        direction = float(components[2])
        speed = float(components[3])

        #Return a tuple with dateAndTime, direction, and speed
        return (dateAndTime, direction, speed)
