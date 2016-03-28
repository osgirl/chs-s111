#******************************************************************************
#
#******************************************************************************
import argparse
import h5py
import numpy
import csv

def clear_metadata_value(attributes, attribute_name):
    """ Clear the specified attribute value.

    :param attributes: The list of attributes containing the value to be cleared.
    :param attribute_name: The name of the attribute to be cleared.
    """

    if attribute_name in attributes:
        print("Information: The value for", attribute_name, "has been ignored.")
        del attributes[attribute_name]

#******************************************************************************
def get_metadata_type(attribute_name):
    """ Retrieve the specified attribute's type.

    :param attribute_name: The name of the attribute to retrive the type for.
    :returns: The attribute's type, None if not found.
    """

    typeMap = dict()
        
    typeMap['editionNumber'] = numpy.int64
    typeMap['updateNumber'] = numpy.int64 
    typeMap['horizontalDatumValue'] = numpy.int64
    typeMap['westBoundLongitude'] = numpy.float64
    typeMap['eastBoundLongitude'] = numpy.float64
    typeMap['southBoundLatitude'] = numpy.float64
    typeMap['northBoundLatitude'] = numpy.float64
    typeMap['timeRecordInterval'] = numpy.int64
    typeMap['numberOfTimes'] = numpy.int64
    typeMap['typeOfCurrentData'] = numpy.int64
    typeMap['dataCodingFormat'] = numpy.int64
    typeMap['numberOfStations'] = numpy.int64
    typeMap['depthTypeIndex'] = numpy.int64
    typeMap['surfaceCurrentDepth'] = numpy.float64
    typeMap['verticalDatum'] = numpy.int64
    typeMap['gridOriginLongitude'] = numpy.float64
    typeMap['gridOriginLatitude'] = numpy.float64
    typeMap['gridSpacingLongitudinal'] = numpy.float64
    typeMap['gridSpacingLatitudinal'] = numpy.float64
    typeMap['numberPointsLong'] = numpy.int64
    typeMap['numberPointsLat'] = numpy.int64
    typeMap['minimumGridPointLongitudinal'] = numpy.int64
    typeMap['minimumGridPointLatitudinal'] = numpy.int64
    typeMap['numberOfNodes'] = numpy.int64
    typeMap['gridLandMaskValue'] = numpy.float64
    typeMap['uncertaintyOfSpeed'] = numpy.float64
    typeMap['uncertaintyOfDirection'] = numpy.float64
    typeMap['uncertaintyOfHorizontalPosition'] = numpy.float64
    typeMap['uncertaintyOfVerticalPosition'] = numpy.float64
    typeMap['uncertaintyOfTime'] = numpy.float64
    
    typeMap['nationalOriginator'] = numpy.bytes_
    typeMap['producingAgency'] = numpy.bytes_
    typeMap['productSpecification'] = numpy.bytes_
    typeMap['dateOfIssue'] = numpy.bytes_
    typeMap['updateApplicationDate'] = numpy.bytes_
    typeMap['fileName'] = numpy.bytes_
    typeMap['dataType'] = numpy.bytes_
    typeMap['nameRegion'] = numpy.bytes_
    typeMap['nameSubregion'] = numpy.bytes_
    typeMap['horizontalDatumReference'] = numpy.bytes_
    typeMap['dateOfFirstRecord'] = numpy.bytes_
    typeMap['dateOfLastRecord'] = numpy.bytes_
    typeMap['methodOrSource'] = numpy.bytes_
    typeMap['dateTimeOfFirstRecord'] = numpy.bytes_ 
    typeMap['dateTimeOfLastRecord'] = numpy.bytes_ 
    typeMap['Filename'] = numpy.bytes_ 
    typeMap['Datatype'] = numpy.bytes_ 

    if attribute_name not in typeMap:
        return None
        
    return typeMap[attribute_name]
    
#******************************************************************************
def add_metadata(attributes, metadata_file):
    """ Add metadata values to the S-111 attributes.

    :param attributes: The S-111 attributes to be populated.
    :param metadata_file: The ASCII CSV file to retrieve the metadata values from.
    """

    with open(metadata_file) as csvfile:
        reader = csv.reader(csvfile)
        
        #Grab the header and data rows.
        header = next(reader)
        data = next(reader)
        
        colnum = 0
                
        #For each column in the data row...
        for col in data:
            attribute_name = header[colnum].strip()
            attribute_value = col.strip().encode()
            attribute_type = get_metadata_type(attribute_name)
            
            #If we don't know what this attribute is, just report it to the user.
            if attribute_type == None:
                print("Warning: Unknown metadata value", attribute_name)
            #Else if this is a string type...
            elif attribute_type == numpy.bytes_:
                attributes.create(attribute_name, attribute_value)
            #Else use the type returned.
            else:
                attributes.create(attribute_name, attribute_value, dtype=attribute_type)
                
            colnum += 1


    #We have a few pieces of metadata that may have been specified... but we want to ignore
    #They are computed attributes.
    clear_metadata_value(attributes, 'westBoundLongitude')
    clear_metadata_value(attributes, 'eastBoundLongitude')
    clear_metadata_value(attributes, 'southBoundLatitude')
    clear_metadata_value(attributes, 'northBoundLatitude')
    clear_metadata_value(attributes, 'dateTimeOfFirstRecord')
    clear_metadata_value(attributes, 'dateTimeOfLastRecord')
    clear_metadata_value(attributes, 'numberOfStations')
    clear_metadata_value(attributes, 'numberOfTimes')
    clear_metadata_value(attributes, 'dataCodingFormat')
    clear_metadata_value(attributes, 'timeRecordInterval')


    #Since this is a new file, we don't have any stations yet.
    attributes.create('numberOfStations', 0, dtype=numpy.int64)
    attributes.create('numberOfTimes', 0, dtype=numpy.int64)

#******************************************************************************    
def create_dataset(output_file, metadata_file):
    """ Create a new S-111 dataset.

    :param output_file: The name of the file to be created.
    :param metadata_file: The ASCII CSV file to retrieve the metadata values from.
    """

    #Make sure the output file has the correct extension.
    filename, file_extension = os.path.splitext(output_file)
    output_file_with_extension = filename + ".nc"

    #Create the new HDF5 file.
    f = h5py.File(output_file_with_extension, "w")
    
    #Add the metadata to the file.
    add_metadata(f.attrs, metadata_file)
    
    #We are done... so close the file.
    f.close()
    
#******************************************************************************        
def create_command_line():
    """Create and initialize the command line parser.
    
    :returns: The command line parser.
    """

    parser = argparse.ArgumentParser(description='Create S-111 File')

    parser.add_argument('-m', '--metadata-file', help='The text file containing the file metadata.', required=True)
    parser.add_argument("outputFile", nargs=1)

    return parser

#******************************************************************************        
def main():

    #Create the command line parser.
    parser = create_command_line()

    #Parse the command line.
    results = parser.parse_args()
    
    create_dataset(results.outputFile[0], results.metadata_file)



if __name__ == "__main__":
    main()
