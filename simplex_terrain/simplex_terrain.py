import numpy as np
import math
from . import _OpenSimplexNoise
import warnings

#todo - add nose tests

class SimplexTerrainGenerator:
    """Class for generating OpenSimplexNoise, wrapping C++/Cython library.
    Generates seeds for each octave, can run with arbitrary power functions.

    Generate seeds with: 
       
    ```
        stg = SimplexTerrainGenerator(nmax=256)
    ```
    or
    ```
        stg = SimplexTerrainGenerator(seeds=[])
    ```
    
    `nmax` is the total number of seeds, which are generated from 0 to nmax-1.
    `seeds` is a manually generated list of seeds. Specifying `seeds` manually will override `nmax`
    
    Produce 2d height map grid by calling sum_octave_2dgrid (see documentation below)    
    """

    
    def __init__(self,nmax=256,seeds=None):
        """Constructor for SimplexTerrainGenerator
        
        Keyword Arguments:
        
        `nmax`: the total number of seeds, which are generated from 0 to nmax-1.
        `seeds`: a manually generated list of seeds. Specifying `seeds` manually will override `nmax`
        """
        
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
        self.n_octaves_max = len(self.seeds)
        if nmax!=self.n_octaves_max:
            warnings.warn(f"Setting nmax to length of `seeds` (={self.n_octaves_max}), overriding nmax={nmax} in constructor")


    def sum_octave_2dgrid(self,xcoords=None,ycoords=None,nlevels=None,bounds=None,res=None,persistence=.7):
        """Sums layers of opensimplex noise to make a height map with some power spectrum
    
        adapted from https://cmaher.github.io/posts/working-with-simplex-noise/
        Python opensimplex library is super slow though, so I found some c++ version instead
        and hacked it into a Cython library
        
        sum_octave_2dgrid(self,xcoords=None,ycoords=None,bounds=None,res=None,nlevels=None,persistence=.7)
        
        Keyword arguments:
        
        `xcoords, ycoords`: List or array of x & y coordinates to generate noise for. Only the first & last entries and the length of each array is actually used - i.e. it assumes points are evenly space on a rectangular grid. Raises an exception if `res` or `bounds` is specified

        `bounds``: [[xmin,xmax],[ymin,ymax]] giving bounds of region to generate noise for. `res` must also be specified. Raises an exception if `xcoords` or `ycoords` is also specified.
        `res`: [nx,ny] if `bounds` are specified. Raises an exception if `xcoords` or `ycoords` is also specified.
        
        `nlevels`: maximum number of noise octaves to sum. Noise octaves are only calculated if they are resolved.
        
        `persistence`: a number or function defining the relative amplitudes of each octave. If given as a number, amplitude of level l is persistence**l. You usually want 0<l<1 but I won't judge. If given as a function, amplitude of level l is persistence(l). This allows more complex power functions, if you want to produce clusters of continents etc.
        
        Returns:
        
        2D numpy array of heights, unnormalised (range is about -.6 to .6)
        
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
        if (bounds is not None or res is not None) and (xcoords is not None or ycoords is not None):
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
            warnings.warn(f"nlevels>number of specified seeds, setting nlevels=number of specified seeds")
        
        # don't resolve beyond a pixel
        x_zoom = nx/(x_max-x_min)
        y_zoom = ny/(y_max-y_min)
        maxlevel = int(math.log2(min(x_zoom,y_zoom)))
        if nlevels>maxlevel:
            nlevels=maxlevel

        #add successively smaller, higher-frequency terms
        for i in range(nlevels):
            amp = persistence_function(i)
            indata = _OpenSimplexNoise.simplex_noise(self.seeds[i],x_min*freq,x_max*freq,nx,y_min*freq,y_max*freq,ny)
            noise += indata*amp
            maxAmp += amp
#             amp *= persistence
            freq *= 2

        #take the average value of the iterations
        noise /= maxAmp
        return noise 
