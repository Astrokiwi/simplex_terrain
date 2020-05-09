import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import opensimplex
import math

n_ocatves_max = 20
seeds = range(n_ocatves_max)
persistence = .7

res = 256

simplex_generators = [opensimplex.OpenSimplex(seed=seed) for seed in seeds]

sea_level = .2

cmap_terrain_steps = colors.LinearSegmentedColormap.from_list('terrain_steps',
        [(0,'#000080'),
        (.1,'#0000FF'),
        (sea_level,'#1E90FF'),
        (sea_level+0.001,'#228B22'),
        (.7,'yellow'),
        (.9,'#8B4513'),
        (1.,'white')
        ])

vmin=-.2
vmax=.19
vrange = (vmax-vmin)
v_sea_level = vrange*sea_level+vmin

def sumOcatave(x, y, nlevels):
    if nlevels>n_ocatves_max:
        raise ValueError("Require nlevels<n_ocatves_max")
    maxAmp = 0
    amp = 1
    freq = 1
    noise = 0

    #add successively smaller, higher-frequency terms
    for i in range(nlevels):
        noise += simplex_generators[i].noise2d(x * freq, y * freq) * amp
        maxAmp += amp
        amp *= persistence
        freq *= 2

    #take the average value of the iterations
    noise /= maxAmp

    return noise

def simplex_noise_2dgrid(xcoords,ycoords,nlevels=n_ocatves_max):
    noise = np.zeros((xcoords.size,ycoords.size))
    for ix,x in enumerate(xcoords):
        for iy,y in enumerate(ycoords):
            noise[ix,iy] = sumOcatave(x,y,nlevels)
    return noise


for iplot,zoom in enumerate(2**np.arange(13)):
    print("zoom:",iplot,zoom)
    coords = np.linspace(.5-.5/zoom,.5+.5/zoom,res)
    maxlevel = int(math.log2(res*zoom))
    if maxlevel>n_ocatves_max:
        maxlevel=n_ocatves_max
    print("maxlevel=",maxlevel)
    noise = simplex_noise_2dgrid(coords,coords,maxlevel)
#     fig,sp = plt.subplots(2,1)
#     plt.imshow(noise,cmap=cmap_terrain_steps,vmin=0.,vmax=1.)
#     plt.imshow(noise,cmap='terrain',vmin=-.46,vmax=.19)
#     plt.contourf(noise,cmap='terrain',vmin=-.2,vmax=.19,levels=10)
    min_lev = np.min(noise)
    if min_lev<-.2: min_lev=-.2
    max_lev = np.max(noise)
    contour_levels = np.linspace(min_lev,max_lev,9)
    print(contour_levels)
    contour_levels = np.insert(contour_levels,np.searchsorted(contour_levels,v_sea_level),v_sea_level)
    print(contour_levels)
    plt.contourf(noise,cmap=cmap_terrain_steps,vmin=vmin,vmax=vmax,levels=contour_levels,extend='both')
    print(np.min(noise),np.max(noise))
    plt.colorbar()
    plt.savefig(f"noise{iplot}.png")
    plt.close('all')