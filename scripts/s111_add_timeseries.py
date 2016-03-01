#******************************************************************************
#
#******************************************************************************
import argparse
import h5py
import numpy
import iso8601
import pytz
from s111 import ascii_time_series


#******************************************************************************
def update_area_coverage(hdf_file, latitude, longitude):

    if 'westBoundLongitude' in hdf_file.attrs:
        westBoundLongitude = hdf_file.attrs['westBoundLongitude']
        westBoundLongitude = min(westBoundLongitude, longitude)
    else:
        westBoundLongitude = longitude

    if 'eastBoundLongitude' in hdf_file.attrs:
        eastBoundLongitude = hdf_file.attrs['eastBoundLongitude']
        eastBoundLongitude = max(eastBoundLongitude, longitude)
    else:
        eastBoundLongitude = longitude

    if 'southBoundLatitude' in hdf_file.attrs:
        southBoundLatitude = hdf_file.attrs['southBoundLatitude']
        southBoundLatitude = min(southBoundLatitude, latitude)
    else:
        southBoundLatitude = latitude

    if 'northBoundLatitude' in hdf_file.attrs:
        northBoundLatitude = hdf_file.attrs['northBoundLatitude']
        northBoundLatitude = max(northBoundLatitude, latitude)
    else:
        northBoundLatitude = latitude

    hdf_file.attrs.create('westBoundLongitude', westBoundLongitude, dtype=numpy.float64)
    hdf_file.attrs.create('eastBoundLongitude', eastBoundLongitude, dtype=numpy.float64)
    hdf_file.attrs.create('southBoundLatitude', southBoundLatitude, dtype=numpy.float64)
    hdf_file.attrs.create('northBoundLatitude', northBoundLatitude, dtype=numpy.float64)


#******************************************************************************
def update_temporal_coverage(hdf_file, start_time, end_time):

    if 'dateTimeOfFirstRecord' in hdf_file.attrs:
        dateTimeOfFirstRecord = iso8601.parse_date(hdf_file.attrs['dateTimeOfFirstRecord'].decode())
        dateTimeOfFirstRecord = min(dateTimeOfFirstRecord, start_time)
    else:
        dateTimeOfFirstRecord = start_time

    if 'dateTimeOfLastRecord' in hdf_file.attrs:
        dateTimeOfLastRecord = iso8601.parse_date(hdf_file.attrs['dateTimeOfLastRecord'].decode())
        dateTimeOfLastRecord = max(dateTimeOfLastRecord, end_time)
    else:
        dateTimeOfLastRecord = end_time

    dateTimeOfFirstRecord = dateTimeOfFirstRecord.astimezone(pytz.utc)
    strVal = dateTimeOfFirstRecord.strftime("%Y%m%dT%H%M%SZ")
    hdf_file.attrs.create('dateTimeOfFirstRecord', strVal.encode())

    dateTimeOfLastRecord = dateTimeOfLastRecord.astimezone(pytz.utc)
    strVal = dateTimeOfLastRecord.strftime("%Y%m%dT%H%M%SZ")
    hdf_file.attrs.create('dateTimeOfLastRecord', strVal.encode())


#******************************************************************************
def add_series_group(hdf_file, time_file):
    
    #Read the file metadata to find out how many time stations we currently have.
    numCurrentStations = hdf_file.attrs['numberOfStations']
    
    #If this is the first station, then we need to initialize a few things.
    if numCurrentStations == 0:

        #Set the number of times.
        hdf_file.attrs.create('numberOfTimes', time_file.number_of_records, dtype=numpy.int64)

        #Set the correct coding format.
        hdf_file.attrs.create('dataCodingFormat', 1, dtype=numpy.int64)

        #Set the correct record interval.
        intervalInSeconds = time_file.interval.total_seconds()
        hdf_file.attrs.create('timeRecordInterval', intervalInSeconds, dtype=numpy.int64)

        #Add the 'Group XY' to store the position information.
        xy_group = hdf_file.create_group('Group XY')

        #Add the x and y datasets to the xy group.
        x_dataset = xy_group.create_dataset('X', (1, 1), maxshape=(1, None), dtype=numpy.float64)
        x_dataset[0][0] = time_file.longitude

        y_dataset = xy_group.create_dataset('Y', (1, 1), maxshape=(1, None), dtype=numpy.float64)       
        y_dataset[0][0] = time_file.latitude

    #Else this is not a new file, so lets verify a few things.
    else:

        #Make sure this file contains the correct number of times.
        numTimesInFile = hdf_file.attrs['numberOfTimes']
        if numTimesInFile != time_file.number_of_records:
            raise Exception('Number of times in file does not match file header.')

        #Make sure the given file contains the correct type of data.
        dataCodingFormat = hdf_file.attrs['dataCodingFormat']
        if dataCodingFormat != 1:
            raise Exception('The specified S-111 file does not contain time series data.')

        #Make sure the given file has the correct record interval.
        timeRecordInterval = hdf_file.attrs['timeRecordInterval']
        intervalInSeconds = time_file.interval.total_seconds()
        if intervalInSeconds != timeRecordInterval:
            raise Exception('The specified S-111 file does not match the input time interval.')

        #Update the XY group with the position information of this time series file.
        xy_group = hdf_file['Group XY']

        x_dataset = xy_group['X']
        x_dataset.resize((1, numCurrentStations+1))
        x_dataset[0][numCurrentStations] = time_file.longitude

        y_dataset = xy_group['Y']
        y_dataset.resize((1, numCurrentStations+1))
        y_dataset[0][numCurrentStations] = time_file.latitude

    
            
    #Update the area coverage information.
    update_area_coverage(hdf_file, time_file.latitude, time_file.longitude)

    #Update the temporal information.
    update_temporal_coverage(hdf_file, time_file.startTime, time_file.endTime)

    #Increment the number of time stations and store it back in the file.
    numCurrentStations += 1
    hdf_file.attrs.create('numberOfStations', numCurrentStations, dtype=numpy.int64)
        
    #Create the new group
    newGroupName = 'Group ' + str(numCurrentStations)
    newGroup = hdf_file.create_group(newGroupName)
    
    #TODO - where does the title come from?
    newGroup.attrs.create('Title', b'Station No. 1')

    #Store the start time.
    strVal = time_file.startTime.strftime("%Y%m%dT%H%M%SZ")
    newGroup.attrs.create('DateTime', strVal.encode())

    print("Created tide station group #", str(numCurrentStations))

    return newGroup


#******************************************************************************    
def add_series_datasets(group, ascii_file):
        
    #Create a new dataset.
    directions = group.create_dataset('Direction', (1, ascii_file.number_of_records), dtype=numpy.float64)
    speeds = group.create_dataset('Speed', (1, ascii_file.number_of_records), dtype=numpy.float64)

    print("Adding direction and speed information...")

    #For each row of data in the ascii file...
    for row_counter in range(0, ascii_file.number_of_records):

        #Read the data from the ascii file and store it in the HDF5 dataset.
        data_values = ascii_file.read_next_row()
        directions[0][row_counter] = data_values[1]
        speeds[0][row_counter] = data_values[2]
    

#******************************************************************************        
def create_command_line():

    parser = argparse.ArgumentParser(description='Add S-111 time series Dataset')

    parser.add_argument('-t', '--time-series-file', help='The ASCII file containing the time series.', required=True)
    parser.add_argument("inOutFile", nargs=1)

    return parser


#******************************************************************************        
def main():

    #Create the command line parser.
    parser = create_command_line()

    #Parse the command line.
    results = parser.parse_args()
    
    #open the HDF5 file.
    hdf_file = h5py.File(results.inOutFile[0], "r+")
    
    #Open the direction and speed files.
    time_file = ascii_time_series.AsciiTimeSeries(results.time_series_file)
    print("Successfully opened time series file containing", str(time_file.number_of_records), "records.")

    #Add a new group for the series.
    new_group = add_series_group(hdf_file, time_file)

    #Add the direction and speed
    add_series_datasets(new_group, time_file)
    
    #We are done, so lets close the file.
    hdf_file.close()

main()