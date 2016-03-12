"""
This file contains the jackknifer class that extends object. The class is
initiated with a path to a file and a filename, and possibly a number of jackknife regions
which can be changed later. It contains a class method that set up
jackknife regions according to the locations of the particles in the
file provided, as well as a method to scan for the minimum and maximum of
the regions.

The only dependency is the os modeule, used to make a directory that holds the jackknifes.

This will only give equal volume jkregions for rectangular regions. It can
operate on non rectangualr regions, but the jkregions will not be equal in volume.
"""

import os

class Jackknifer(object):
    def __init__(self,path,filename,columns=[0,1,2],N=2):
        self.path = path #Path to the file
        self.filename = filename #Filename to be jackknifed
        self.columns = columns #Which columns in the file contain the position information
        self.N = N #Number of jackknife regions
        self.measured = False #A flag to tell if the file has been scanned yet

    """
    Measure the particles in the file to find the extents 
    in each dimension (e.g. xmin and xmax).
    """
    def measure(self):
        xc,yc,zc = self.columns
        infile = open(self.path+"/"+self.filename,"r")
        xmin=ymin=zmin = 1e99 # a big number
        xmax=ymax=zmax = -1e99 # a small number
        for line in infile:
            if line[0]=='#':
                continue
            parts = line.split()
            x,y,z = float(parts[xc]),float(parts[yc]),float(parts[zc])
            if x < xmin:
                xmin = x
            if x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            if y > ymax:
                ymax = y
            if z < zmin:
                zmin = z
            if z > zmax:
                zmax = z
        infile.close()
        xoff,yoff,zoff=(xmax-xmin)*0.00001,\
            (ymax-ymin)*0.00001,(zmax-zmin)*0.00001
        self.minimums = [xmin-xoff,ymin-yoff,zmin-zoff]
        self.maximums = [xmax+xoff,ymax+yoff,zmax+zoff]
    
    """
    A method to set the number of jackknife regions to a new value.
    """
    def set_N_regions(self,N):
        self.N = N

    """
    Set up the actual jackknife regions.
    """
    def jackknife(self):
        if not self.measured:
            self.measure()
            self.measured = True
        xc,yc,zc = self.columns
        xmin,ymin,zmin = self.minimums
        xmax,ymax,zmax = self.maximums
        N = self.N
        xstep,ystep,zstep = (xmax-xmin)/N,(ymax-ymin)/N,(zmax-zmin)/N

        #Make a directory for the new jackknife files
        jkpath = self.path+"/jackknife_files/"
        os.system("mkdir "+jkpath)
        filename = self.filename
        infile = open(self.path+"/"+filename,"r")

        #Create the files for each jackknife region
        filelist = []
        for i in range(N**3):
            outfile = open(jkpath+"jk%i_"%i+filename,"w")
            filelist.append(outfile)
        
        #Loop over the lines in the input file and put them
        #in the correct jackknife file
        i = 0
        for line in infile:
            if line[0]=='#':
                continue
            parts = line.split()
            x,y,z = float(parts[xc]),float(parts[yc]),float(parts[zc])
            xi,yi,zi = int(x/xstep),int(y/ystep),int(z/zstep)
            index = zi*N*N + yi*N + xi
            filelist[index].write(line)
        
        #Close the output files
        for i in range(N**3):
            filelist[i].close()

"""
A unit test for creating some jackknife regions
"""
if __name__ == '__main__':
    jkr = Jackknifer(".","test.txt")
    jkr.measure()
    print jkr.minimums, jkr.maximums
    jkr.jackknife()

    #myjkr = Jackknifer(path="/media/tom/Data/Emulator_data/reduced_data",filename="reduced_box000_Z9.list",columns=[8,9,10],N=8)
    #myjkr.jackknife()
