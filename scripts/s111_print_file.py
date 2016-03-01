#******************************************************************************
#
#******************************************************************************
import argparse
import h5py
import numpy


#******************************************************************************        
def create_command_line():

    parser = argparse.ArgumentParser(description='Print the contents of an S-111 File.')

    parser.add_argument("inputFile", nargs=1)

    return parser


#******************************************************************************        
def main():

    #Create the command line parser.
    parser = create_command_line()

    #Parse the command line.
    results = parser.parse_args()
    
    f = h5py.File(results.inputFile[0], 'r')
    
    print("Product Metadata")
    for name, value in f.attrs.items():
        print(name, value, type(value))
    
    print("\n\nGroups")
    for key in f:
        
        print("\nGroup", key)
        dset = f[key]
        #print(dset)
        
        print("    Metadata")
        for name, value in dset.attrs.items():
            print("    ", name, value)
            
        print("    Datasets")    
        for datasetName in dset.keys():
            print("    ", datasetName)
            
            dataset = dset[datasetName]
            #print(dataset)

            print("        Type", dataset.dtype)
            print("        Shape", dataset.shape)
            print("        Size", dataset.size)
            
            #print(dataset[:])
            
main()
