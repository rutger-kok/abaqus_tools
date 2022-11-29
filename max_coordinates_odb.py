'''
This script determines the maximum and minimum x, y, z values for the assembly
in the currently selected output database (.odb).


Last modified: 01/02/2021
(c) Rutger Kok
'''
from odbAccess import *
import visualization
from caeModules import *

# Use the output data
odb = vp.displayedObject
if type(odb) != visualization.OdbType:
    raise ValueError, 'An odb must be displayed! Please open an odb.'

# Alternatively use a path to an odb
# path = ''  # specify the path to your odb here
# odb = openOdb(path)
# name = path[path.rfind('\\')+1:path.rfind('.')]

# first find the max/min coords for each instance in an assembly, then find the
# max/min for the whole assembly
max_inst_values = []  # initialize lists of max/min coords for each instance
min_inst_values = []
# iterate over each instance in an odb assembly
for instance in odb.rootAssembly.instances.values():
    # use generator expression to extract coordinates
    coord_list = (node.coordinates for node in instance.nodes)
    # find max and min x, y, z in the instance and append
    max_inst_values.append([max(i) for i in zip(*coord_list)])
    min_inst_values.append([min(j) for j in zip(*coord_list)])
# determine max/min x, y, z in the whole assembly
max_values = [max(k) for k in zip(*max_inst_values)]
min_values = [min(j) for j in zip(*min_inst_values)]
print max_values, min_values
