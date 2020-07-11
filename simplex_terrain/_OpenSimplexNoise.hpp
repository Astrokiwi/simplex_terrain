// #pragma once
/*******************************************************************************
  OpenSimplex Noise in C++
  Ported from https://gist.github.com/digitalshadow/134a3a02b67cecd72181
  Originally from https://gist.github.com/KdotJPG/b1270127455a94ac5d19
  Optimised by DigitalShadow
  This version originally by Mark A. Ropper (Markyparky56)
  Stripped down to 2D by David Williamson, with a couple extra helper functions
*******************************************************************************/
#include <array>
#include <vector>
#include <memory> // unique_ptr
#include <ctime> // time for random seed

#if defined(__clang__) // Couldn't find one for clang
#define FORCE_INLINE inline
#elif defined(__GNUC__) || defined(__GNUG__)
#define FORCE_INLINE __attribute__((always_inline))
#elif defined(_MSC_VER)
#define FORCE_INLINE __forceinline
#endif

class OpenSimplexNoise
{
protected:
  // Contribution structs
  struct Contribution2
  {
  public:
    double dx, dy;
    int xsb, ysb;
    Contribution2 *Next;

    Contribution2(double multiplier, int _xsb, int _ysb)
      : xsb(_xsb)
      , ysb(_ysb)
      , Next(nullptr)
    {
      dx = -_xsb - multiplier * SQUISH_2D;
      dy = -_ysb - multiplier * SQUISH_2D;
    }
    ~Contribution2()
    {
      if (Next != nullptr)
      {
        delete Next;
      }
    }
  };
  
  using pContribution2 = std::unique_ptr<Contribution2>;

  // Constants
  static const double STRETCH_2D;
  static const double SQUISH_2D;
  static const double NORM_2D;

  std::array<unsigned char, 256> perm;
  std::array<unsigned char, 256> perm2D;

  static std::array<double, 16> gradients2D;

  static std::vector<Contribution2*> lookup2D;

  static std::vector<pContribution2> contributions2D;

  struct StaticConstructor 
  {
    StaticConstructor() 
    { 
      gradients2D =
      {
         5,  2,    2,  5,
        -5,  2,   -2,  5,
         5, -2,    2, -5,
        -5, -2,   -2, -5,
      };
      
      // Create Contribution2s for lookup2D
      std::vector<std::vector<int>> base2D =
      {
        { 1, 1, 0, 1, 0, 1, 0, 0, 0 },
        { 1, 1, 0, 1, 0, 1, 2, 1, 1 }
      };
      std::vector<int> p2D =
      {
        0,  0,  1, -1, 0,  0, -1,  1, 0,  2,  1,  1, 1,  2,  2,  0, 1,  2,  0,  2, 1,  0,  0,  0
      };
      std::vector<int> lookupPairs2D =
      {
        0, 1,  1, 0,  4, 1, 17, 0, 20, 2, 21, 2, 22, 5, 23, 5, 26, 4, 39, 3, 42, 4, 43, 3
      };

      contributions2D.resize(6);
      for (int i = 0; i < static_cast<int>(p2D.size()); i += 4)
      {
        std::vector<int> baseSet = base2D[p2D[i]];
        Contribution2 *previous = nullptr, *current = nullptr;
        for (int k = 0; k < static_cast<int>(baseSet.size()); k += 3)
        {
          current = 
            new Contribution2(baseSet[k], baseSet[k + 1], baseSet[k + 2]);
          if (previous == nullptr)
          {
            contributions2D[i / 4].reset(current);
          }
          else
          {
            previous->Next = current;
          }
          previous = current;
        }
        current->Next = new Contribution2(p2D[i + 1], p2D[i + 2], p2D[i + 3]);
      }

      lookup2D.resize(64);
      for (int i = 0; i < static_cast<int>(lookupPairs2D.size()); i += 2)
      {
        lookup2D[lookupPairs2D[i]] = 
          contributions2D[lookupPairs2D[i + 1]].get();
      }


    }
  };
  static StaticConstructor staticConstructor;
  
  FORCE_INLINE static int FastFloor(double x)
  {
    int xi = static_cast<int>(x);
    return x < xi ? xi - 1 : xi;
  }

public:
  OpenSimplexNoise()
    : OpenSimplexNoise(static_cast<int64_t>(time(nullptr)))
  {}

  OpenSimplexNoise(int64_t seed)
  {
    std::array<char, 256> source;
    for (int i = 0; i < 256; i++)
    {
      source[i] = i;
    }
    seed = seed * 6364136223846793005L + 1442695040888963407L;
    seed = seed * 6364136223846793005L + 1442695040888963407L;
    seed = seed * 6364136223846793005L + 1442695040888963407L;
    for (int i = 255; i >= 0; i--)
    {
      seed = seed * 6364136223846793005L + 1442695040888963407L;
      int r = static_cast<int>((seed + 31) % (i + 1));
      if (r < 0)
      {
        r += (i + 1);
      }
      perm[i] = source[r];
      perm2D[i] = perm[i] & 0x0E;
      source[r] = source[i];
    }
  }

  double Evaluate(double x, double y)
  {
    double stretchOffset = (x + y) * STRETCH_2D;
    double xs = x + stretchOffset;
    double ys = y + stretchOffset;

    int xsb = FastFloor(xs);
    int ysb = FastFloor(ys);

    double squishOffset = (xsb + ysb) * SQUISH_2D;
    double dx0 = x - (xsb + squishOffset);
    double dy0 = y - (ysb + squishOffset);

    double xins = xs - xsb;
    double yins = ys - ysb;

    double inSum = xins + yins;
    int hash =
      static_cast<int>(xins - yins + 1) |
      static_cast<int>(inSum) << 1 |
      static_cast<int>(inSum + yins) << 2 |
      static_cast<int>(inSum + xins) << 4;

    Contribution2 *c = lookup2D[hash];

    double value = 0.0;
    while (c != nullptr)
    {
      double dx = dx0 + c->dx;
      double dy = dy0 + c->dy;
      double attn = 2 - dx * dx - dy * dy;
      if (attn > 0)
      {
        int px = xsb + c->xsb;
        int py = ysb + c->ysb;
        
        int i = perm2D[(perm[px & 0xFF] + py) & 0xFF];
        double valuePart = 
                       gradients2D[i    ] * dx 
                     + gradients2D[i + 1] * dy;

        attn *= attn;
        value += attn * attn * valuePart;
      }
      c = c->Next;
    }

    return value * NORM_2D;
  }

};

#ifndef OPENSIMPLEXNOISE_STATIC_CONSTANTS
#define OPENSIMPLEXNOISE_STATIC_CONSTANTS
const double OpenSimplexNoise::STRETCH_2D = -0.211324865405187;
const double OpenSimplexNoise::SQUISH_2D = 0.366025403784439;
const double OpenSimplexNoise::NORM_2D = 1.0 / 47.0;

std::array<double, 16> OpenSimplexNoise::gradients2D;

std::vector<OpenSimplexNoise::Contribution2*> OpenSimplexNoise::lookup2D;

std::vector<OpenSimplexNoise::pContribution2> OpenSimplexNoise::contributions2D;

// Initialise our static tables
OpenSimplexNoise::StaticConstructor OpenSimplexNoise::staticConstructor;
#endif


// Helper functions to generate a grid
// (Not using overloading to simplify the Cython)
std::vector<std::vector<double>> simplex_noise_2d_points(int64_t seed,std::vector<double> x_coords,std::vector<double> y_coords) {
    /**Generate 2D noise on all points of grid given by coordinate vectors*/

    OpenSimplexNoise noise_generator(seed);
    std::vector<std::vector<double>> out_map = std::vector<std::vector<double>>(x_coords.size(), std::vector<double>(y_coords.size(), 0));

    for(std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++) {
        for(std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++) {
            out_map[ix][iy] = noise_generator.Evaluate(x_coords[ix],y_coords[iy]);
        }
    }
    
    return out_map;
}

std::vector<std::vector<double>> simplex_noise_2d(int64_t seed, double x_min, double x_max, int nx, double y_min, double y_max, int ny) {
    /**Convert min/max/n into lists of coordinates, then loop through them with noise generator*/
    std::vector<double> x_coords(nx,0);
    std::vector<double> y_coords(ny,0);
    
    for ( std::vector<double>::size_type ix = 0; ix != x_coords.size(); ix++ ) {
        x_coords[ix] = (ix+.5)*1./(double)(nx)*(x_max-x_min)+x_min;
    }

    for ( std::vector<double>::size_type iy = 0; iy != y_coords.size(); iy++ ) {
        y_coords[iy] = (iy+.5)*1./(double)(ny)*(y_max-y_min)+y_min;
    }

    return simplex_noise_2d_points(seed,x_coords,y_coords);
}