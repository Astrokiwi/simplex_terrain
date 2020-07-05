import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import math
import subprocess
import sys

class simplex_terrain_generator:
    def __init__(self,nmax=256,seeds=None):
        self.n_octaves_max = nmax
        if seeds is None:
            self.seeds = range(nmax)
        else:
            try:
                len(seeds)
                self.seeds=seeds
            except TypeError:
                try:
                    self.seeds = range(seeds,nmax+seeds)
                except:
                    raise ValueError("seeds must be integer or list")

    def sum_octave_2dgrid_fromfile(self,xcoords=None,ycoords=None,nlevels=None,bounds=None,res=None,persistence=.7):
        """ sum_octave_2dgrid_fromfile
    
        Sums layers of opensimplex noise to make a height map with some power spectrum
    
        adapted from https://cmaher.github.io/posts/working-with-simplex-noise/
        Python opensimplex library is super slow though, so I found some c++ version instead
        Interfacing C++ with Python is weirdly complex compared to e.g. interacing Fortran with C++
        So we just compile the C++ into an executible and dump the data to disk and load it like a shmuck
        Turns out the main bottleneck is the matplotlib plotting anyway, so whatevs
        """
        maxAmp = 0
#         amp = 1
        freq = 1
        
        try:
            persistence(2)
            persistence_function = persistence
        except TypeError:
            persistence_function = lambda x: persistence**x
        
        if bounds is not None and res is None or bounds is None and res is not None:
            raise ValueError("Must specify both bounds and res")
        if bounds is not None and (xcoords is not None or ycoords is not None):
            raise ValueError("Can not specify both xcoords/ycoords and bounds/res")

        if bounds is not None:
            x_min = bounds[0][0]
            x_max = bounds[0][1]
            nx = res[0]

            y_min = bounds[1][0]
            y_max = bounds[1][1]
            ny = res[1]
        else:
            x_min = xcoords[0]
            x_max = xcoords[-1]
            nx = xcoords.size

            y_min = ycoords[0]
            y_max = ycoords[-1]
            ny = ycoords.size

        noise = np.zeros((nx,ny))
        
        if nlevels is None:
            nlevels = self.n_octaves_max
        elif nlevels>self.n_octaves_max:
            nlevels=self.n_octaves_max
        
        # don't resolve beyond a pixel
        x_zoom = nx/(x_max-x_min)
        y_zoom = ny/(y_max-y_min)
        maxlevel = int(math.log2(min(x_zoom,y_zoom)))
        if nlevels>maxlevel:
            nlevels=maxlevel

        #add successively smaller, higher-frequency terms
        for i in range(nlevels):
            amp = persistence_function(i)
            subprocess.run(["./simplex_vector"]+[str(x) for x in [self.seeds[i],nx,ny,x_min*freq,x_max*freq,y_min*freq,y_max*freq]])
            indata = np.fromfile("noisemap.bin", dtype=np.double).reshape(ny,nx).T*amp
            noise += indata
            maxAmp += amp
#             amp *= persistence
            freq *= 2

        #take the average value of the iterations
        noise /= maxAmp
        return noise 

if __name__ == "__main__":
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
    
    n_octaves_max=256
    ter_gen = simplex_terrain_generator(n_octaves_max)


#     for iplot,zoom in enumerate(2**np.arange(32)):
    for iplot,zoom in enumerate(2**np.arange(4)):
        print("zoom:",iplot,zoom)
        coords = np.linspace(.5-.5/zoom,.5+.5/zoom,res)
#         xcoords = coords-0.8445e-5
        xcoords = np.linspace(.5-.5/zoom,.5+.5/zoom,res*2)-0.8445e-5
        ycoords = coords+3.56413e-5
        maxlevel = int(math.log2(res*zoom))
        if maxlevel>n_octaves_max:
            maxlevel=n_octaves_max
        noise = ter_gen.sum_octave_2dgrid_fromfile(xcoords,ycoords,maxlevel)
        plt.imshow(noise,cmap=cmap_terrain_steps,vmin=vmin,vmax=vmax,extent=[xcoords[0],xcoords[-1],ycoords[0],ycoords[-1]],origin='lower')
        plt.colorbar()
        plt.savefig(f"noise{iplot:03d}.png")
        plt.close('all')
