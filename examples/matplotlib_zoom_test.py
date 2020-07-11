import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import math
import simplex_terrain

def dump_test_zoom():
    """Test function to dump a zoom into some terrain as png files, using matplotlib
    """

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
    ter_gen = SimplexTerrainGenerator(n_octaves_max)


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
        noise = ter_gen.sum_octave_2dgrid(xcoords,ycoords,maxlevel)
        plt.imshow(noise,
			cmap=cmap_terrain_steps,
			vmin=vmin,
			vmax=vmax,
			extent=[xcoords[0],
			xcoords[-1],
			ycoords[0],
			ycoords[-1]],
			origin='lower')
        plt.colorbar()
        plt.savefig(f"noise{iplot:03d}.png")
        plt.close('all')

if __name__ == "__main__":
    dump_test_zoom()
