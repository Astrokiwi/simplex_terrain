import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import opensimplex
import math
import subprocess
import sys

n_octaves_max = 64
seeds = range(n_octaves_max)
persistence = .7

res = 256

simplex_generators = [opensimplex.OpenSimplex(seed=seed) for seed in seeds]

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

# cmap_terrain_steps = colors.LinearSegmentedColormap.from_list('terrain_steps',
#         [(0,'#000080'),
#         (.1,'#0000FF'),
#         (sea_level,'#1E90FF'),
#         (sea_level+1.e-9,'#d2aa6d'),
#         (sea_level+0.1,'#228B22'),
#         (.7,'yellow'),
#         (.9,'#8B4513'),
#         (1.,'white')
#         ])

vmin=-.2
vmax=.19
vrange = (vmax-vmin)

force_insert_levels = [sea_level-1.e-9,sea_level,sea_level+1.e-9]
v_insert_levels = [vrange*x+vmin for x in force_insert_levels]

# v_sea_level = vrange*sea_level+vmin



def sumOcatave(x, y, nlevels):
    if nlevels>n_octaves_max:
        raise ValueError("Require nlevels<n_octaves_max")
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

def simplex_noise_2dgrid(xcoords,ycoords,nlevels=n_octaves_max):
    noise = np.zeros((xcoords.size,ycoords.size))
    for ix,x in enumerate(xcoords):
        for iy,y in enumerate(ycoords):
            noise[ix,iy] = sumOcatave(x,y,nlevels)
    return noise

def sum_octave_2dgrid_fromfile(xcoords,ycoords,nlevels=n_octaves_max):
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


for iplot,zoom in enumerate(2**np.arange(23)):
    print("zoom:",iplot,zoom)
    coords = np.linspace(.5-.5/zoom,.5+.5/zoom,res)
    xcoords = coords-0.85e-5
    ycoords = coords+3.72e-5
    maxlevel = int(math.log2(res*zoom))
    if maxlevel>n_octaves_max:
        maxlevel=n_octaves_max
#     noise = simplex_noise_2dgrid(coords,coords,maxlevel)
    noise = sum_octave_2dgrid_fromfile(xcoords,ycoords,maxlevel)
#     fig,sp = plt.subplots(2,1)
#     plt.imshow(noise,cmap=cmap_terrain_steps,vmin=0.,vmax=1.)
#     plt.imshow(noise,cmap='terrain',vmin=-.46,vmax=.19)
#     plt.contourf(noise,cmap='terrain',vmin=-.2,vmax=.19,levels=10)
#     min_lev = np.min(noise)
#     if min_lev<-.2: min_lev=-.2
#     max_lev = np.max(noise)
#     contour_levels = np.linspace(min_lev,max_lev,9)
#     for v_insert_level in v_insert_levels:
#         contour_levels = np.insert(contour_levels,np.searchsorted(contour_levels,v_insert_level),v_insert_level)
    contour_levels = np.linspace(vmin,vmax,128)
    plt.contourf(noise,cmap=cmap_terrain_steps,vmin=vmin,vmax=vmax,levels=contour_levels,extend='both',extent=[xcoords[0],xcoords[-1],ycoords[0],ycoords[-1]])
#     plt.imshow(noise,cmap='terrain',vmin=-.2,vmax=.19)
    plt.colorbar()
    plt.savefig(f"noise{iplot}.png")
    plt.close('all')