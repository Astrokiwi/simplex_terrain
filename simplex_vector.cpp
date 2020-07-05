#include <iostream>
#include <array>
#include <fstream>
#include <stdlib.h>

#include "OpenSimplexNoise.hpp"


int main(int argc, char *argv[]) {
    
    int seed = atoi(argv[1]);
    
    int nx = atoi(argv[2]);
    int ny = atoi(argv[3]);

    double x_min = atof(argv[4]);
    double x_max = atof(argv[5]);
    double y_min = atof(argv[6]);
    double y_max = atof(argv[7]);
    
    std::vector<std::vector<double>> out_map = simplex_noise_2d(seed,x_min,x_max,nx,y_min,y_max,ny);
    
    std::ofstream outFile;
    outFile.open("noisemap.bin", std::ios::binary);
    for(std::vector<double>::size_type iy = 0; iy != ny; iy++) {
        for(std::vector<double>::size_type ix = 0; ix != nx; ix++) {
            outFile.write(reinterpret_cast<const char*>(&out_map[ix][iy]), sizeof(double));
      }
    }
    outFile.close();


    return 0;
}

