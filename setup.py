#Build with: 
#python setup.py build_ext --inplace

import setuptools
from Cython.Build import cythonize
import numpy as np


setuptools.setup(
    name='simplex_terrain',
    version='0.5.0',
    description='Heightmap terrain generator using OpenSimplexTerrain',
    author='David Williamson',
    author_email="david.john.williamson@gmail.com",
#     package_dir = {'simplex_terrain/': ''},
    packages=["simplex_terrain"],
#     packages=[setuptools.find_packages()],
    ext_modules = cythonize(setuptools.Extension("simplex_terrain._OpenSimplexNoise",["simplex_terrain/_OpenSimplexNoise.pyx"],
        language="c++",             # generate C++ code
        compiler_directives={'language_level' : 3},
        extra_compile_args=["-stdlib=libc++","-std=c++17"],
        extra_link_args= ["-stdlib=libc++","-std=c++17"])),
    include_dirs=[np.get_include()]
    
)