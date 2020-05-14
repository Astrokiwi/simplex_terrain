import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import math
import subprocess
import sys

# these are global variables, suck it
n_octaves_max = 256
seeds = range(n_octaves_max)
persistence = .7

res = 256

sea_level = .2

cmap_terrain_steps = colors.LinearSegmentedColormap.from_list('terrain_steps',
        [(0,'#000080'),
        (.1,'#0000FF'),
        (sea_level,'#1E90FF'),
        (sea_level+1.e-9,'#228B22'),
        (.7,'yellow'),
        (.9,'#8B4513'),
        (1.,'white')
        ])

vmin=-.2
vmax=.19
vrange = (vmax-vmin)

def sum_octave_2dgrid_fromfile(xcoords,ycoords,nlevels=n_octaves_max):
    """ sum_octave_2dgrid_fromfile
    
    Sums layers of opensimplex noise to make a height map with some power spectrum
    
    adapted from https://cmaher.github.io/posts/working-with-simplex-noise/
    Python opensimplex library is super slow though, so I found some c++ version instead
    Interfacing C++ with Python is weirdly complex compared to e.g. interacing Fortran with C++
    So we just compile the C++ into an executible and dump the data to disk and load it like a shmuck
    Turns out the main bottleneck is the matplotlib plotting anyway, so whatevs
    """
    maxAmp = 0
    amp = 1
    freq = 1
    
    x_min = xcoords[0]
    x_max = xcoords[-1]
    nx = xcoords.size

    y_min = ycoords[0]
    y_max = ycoords[-1]
    ny = xcoords.size

    noise = np.zeros((nx,ny))


    #add successively smaller, higher-frequency terms
    for i in range(nlevels):
        subprocess.run(["./simplex_vector"]+[str(x) for x in [seeds[i],nx,ny,x_min*freq,x_max*freq,y_min*freq,y_max*freq]])
        indata = np.fromfile("noisemap.bin", dtype=np.double).reshape(nx,ny)*amp
        noise += np.fromfile("noisemap.bin", dtype=np.double).reshape(nx,ny)*amp
        maxAmp += amp
        amp *= persistence
        freq *= 2

    #take the average value of the iterations
    noise /= maxAmp
    return noise 

if __name__ == "__main__":
    for iplot,zoom in enumerate(2**np.arange(32)):
        print("zoom:",iplot,zoom)
        coords = np.linspace(.5-.5/zoom,.5+.5/zoom,res)
        xcoords = coords-0.8445e-5
        ycoords = coords+3.56413e-5
        maxlevel = int(math.log2(res*zoom))
        if maxlevel>n_octaves_max:
            maxlevel=n_octaves_max
        noise = sum_octave_2dgrid_fromfile(xcoords,ycoords,maxlevel)
        plt.imshow(noise,cmap=cmap_terrain_steps,vmin=vmin,vmax=vmax,extent=[xcoords[0],xcoords[-1],ycoords[0],ycoords[-1]],origin='lower')
        plt.colorbar()
        plt.savefig(f"noise{iplot}.png")
        plt.close('all')
