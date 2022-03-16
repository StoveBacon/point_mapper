# point_mapper
A simple script that fulfills a curiosity I had: given a set of points on the XY plane, could all of their positions be deduced only from measurements between them?

The output data is being used to construct a 3D model that will subsequently be 3D printed for another project. As such, the script includes functions for writing to a `.scad` file since the language I'm using, OpenSCAD, does not support `.csv` files. The `.scad` file is simply a variable storing an OpenSCAD vector that contains the output data. The script also includes a simple algorithm that generates triangles between points which can also be exported to a `.scad` file.
