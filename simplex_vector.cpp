#include <iostream>
#include <array>
#include <fstream>
#include <stdlib.h>

#include "OpenSimplexNoise.hpp"

// #include "/Users/davidjwilliamson/anaconda3/lib/python3.6/site-packages/pybind11/include/pybind11/pybind11.h"

// class CoordSimplexNoise {
//     public:
//         CoordSimplexNoise(int64_t seed) {
//             this->noise_generator = std::make_unique<OpenSimplexNoise>(seed);
//         }
//         
//         std::vector<std::vector<double>> evaluate(std::vector<double> x_coords,std::vector<double> y_coords) {
//             std::vector<std::vector<double>> out_map = std::vector<std::vector<double>>(y_coords.size(), std::vector<double>(x_coords.size(), 0));
//             
//             for(std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++) {
//                 for(std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++) {
//                     out_map[ix][iy] = this->noise_generator->Evaluate(x_coords[ix],y_coords[iy]);
//                 }
//             }
//             
//             return out_map;
//         }
//     
//     private:
//         std::unique_ptr<OpenSimplexNoise> noise_generator;
// };

std::vector<std::vector<double>> simplex_noise_2d(int64_t seed,std::vector<double> x_coords,std::vector<double> y_coords) {
    OpenSimplexNoise noise_generator(seed);
    std::vector<std::vector<double>> out_map = std::vector<std::vector<double>>(x_coords.size(), std::vector<double>(y_coords.size(), 0));

    for(std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++) {
        for(std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++) {
            out_map[ix][iy] = noise_generator.Evaluate(x_coords[ix],y_coords[iy]);
        }
    }
    
    return out_map;
}


int main(int argc, char *argv[]) {
//     int nx=5,ny=4;
//     
//     double x_min=.2,x_max=.4;
//     double y_min=.1,y_max=.3;
    
    int seed = atoi(argv[1]);
    
    int nx = atoi(argv[2]);
    int ny = atoi(argv[3]);

    double x_min = atof(argv[4]);
    double x_max = atof(argv[5]);
    double y_min = atof(argv[6]);
    double y_max = atof(argv[7]);
    
//     std::cout << nx << " " << ny << " " << x_min << " " << x_max << " " << y_min << " " << y_max << std::endl;
    
//     std::unique_ptr<CoordSimplexNoise> x = std::make_unique<CoordSimplexNoise>(12);
    std::vector<double> x_coords(nx,0);
    std::vector<double> y_coords(ny,0);
    
    for ( std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++ ) {
        x_coords[ix] = (ix+.5)*1./(double)(nx)*(x_max-x_min)+x_min;
    }

    for ( std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++ ) {
        y_coords[iy] = (iy+.5)*1./(double)(ny)*(y_max-y_min)+y_min;
    }

    std::vector<std::vector<double>> out_map = simplex_noise_2d(seed,x_coords,y_coords);
    
    std::ofstream outFile;
    outFile.open("noisemap.bin", std::ios::binary);
    for(std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++) {
        for(std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++) {
            outFile.write(reinterpret_cast<const char*>(&out_map[ix][iy]), sizeof(double));
      }
    }
    outFile.close();

//     for(std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++) {
//         for(std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++) {
//             std::cout << out_map[ix][iy] << " ";
//         }
//         std::cout << std::endl;
//     }

    return 0;
}

