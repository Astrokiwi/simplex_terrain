#Build with: 
#python setup.py build_ext --inplace

from setuptools import Extension,setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules = cythonize(Extension("OpenSimplexNoise",["OpenSimplexNoise.pyx"],
        language="c++",             # generate C++ code
        compiler_directives={'language_level' : 3},
        extra_compile_args=["-stdlib=libc++","-std=c++17"],
        extra_link_args= ["-stdlib=libc++","-std=c++17"])),
    include_dirs=[np.get_include()]
)