#!python
#cython: language_level=3
#distutils: language = c++

from libcpp.vector cimport vector
from numpy cimport int64_t
import numpy as np

cdef extern from "OpenSimplexNoise.hpp":
    vector[vector[double]] simplex_noise_2d(int64_t seed, double x_min, double x_max, int nx, double y_min, double y_max, int ny)

def simplex_noise(seed,x0,x1,nx,y0,y1,ny):
    return np.array(simplex_noise_2d(seed,x0,x1,nx,y0,y1,ny))