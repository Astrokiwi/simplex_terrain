# simplex_terrain
Simple opensimplex terrain generator (work in progress)

C++ opensimplex generator from interwebs
Wrapped into an executible that creates a grid of opensimplex points
Python script to run multiple opensimplex levels to get arbitrarily fine level of detail
Then matplotlib to plot it as a "terrain"

The plotting is the slowest bit.

This is a bit better than perlin noise because it doesn't have those diamond-shaped artifacts, and because you don't need to calculate the large-scale grid at all. You can calculate the noise at any arbitrary point. This means you can zoom arbitrarily to any region without having to calculate any other regions. So if you e.g. want to make a self-consistent world map, and zoom in on specific areas, you can do that - you just need to keep the seeds consistent.
