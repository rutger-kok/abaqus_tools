# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 12:00:37 2015

@author: miguel.herraez

Generate text file with equations for Periodic Boundary Conditions (PBC)

"""

# ----------------------START OF IMPORTS
try:
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
except:
    pass
import numpy as np
import time
import os


# from multiprocessing import Process  # not supported with MeshNodeArray


# ----------------------FUNCTIONS
def isfloat(string):
    """
    Check if a string is a float
    """
    try:
        float(string)
        return True
    except:
        return False


def cartesian_to_polar(x, y):
    """
    Transformation of cartesian coordinates into polar coordinates
    """
    r = np.sqrt(x * x + y * y)
    phi = np.arctan2(y, x)
    return r, phi


# ----------------------CLASSES

# Periodic Boundary Conditions
class PBC():
    """
    Example to use manual version (node sets):
    from module_RVE import specialBC
    a = mdb.models['circ_E'].rootAssembly
    nodes = [ [a.sets['RVE-1_RIGHT'].nodes, a.sets['RVE-1_LEFT'].nodes,   'right'],
                [a.sets['RVE-1_TOP'].nodes,   a.sets['RVE-1_BOTTOM'].nodes, 'top'],
                [a.sets['RVE-1_FRONT'].nodes, a.sets['RVE-1_BACK'].nodes,   'front'] ]

    pbc = specialBC.PBC(nodes, auto=False, MN= [0, -100, -200, -300])
    """
    # 2D models -> dimensions
    # Choosable faces -> pairs
    FACES_dict = {'LEFT': ["LEFT", "RIGHT", 1],
                  'RIGHT': ["RIGHT", "LEFT", 1],
                  'BOTTOM': ["BOTTOM", "TOP", 2],
                  'TOP': ["TOP", "BOTTOM", 2],
                  'BACK': ["BACK", "FRONT", 3],
                  'FRONT': ["FRONT", "BACK", 3]}
    FACES = FACES_dict.keys()

    # Master faces: RIGHT, TOP, FRONT
    # Slave faces: LEFT, BOTTOM, BACK
    fileName = None

    # Tolerance to round nodal coordinates
    # tolerance = 1.0e-6
    decimals = 5  # Rounding decimals
    verbose = True

    def __init__(self, nodes, pairs, MN, dimensions=3, fileName='PBC',
                 forbiddenNodes=[], decimals=6, verbose=False):
        """
        :param nodes: MeshNodeArray.
        :param dimensions: Number of dimensions of the model (2 or 3). Default is 3.
        :param MN: Master nodes can be provided as a list with three integers.
        :param pairs: Faces to attach PBCs (LEFT and/or BOTTOM and/or BACK).
        :return:
        """
        tIni = time.time()
        PBC.decimals = decimals
        PBC.verbose = verbose

        PBC.fileName = os.path.splitext(fileName)[0] + '.txt'

        # dimensions = 3
        self.dimensions = dimensions

        self.faceLabels = {}

        # Couple nodes of opposite faces and Master nodes
        self.couples = dict()

        # <editor-fold desc="auto-True">
        # The nodes to couple with PBCs are provided directly:
        #  [ [a.sets['RVE-1_RIGHT'].nodes, a.sets['RVE-1_LEFT'].nodes,   'right'],
        #    [a.sets['RVE-1_TOP'].nodes,   a.sets['RVE-1_BOTTOM'].nodes, 'top'],
        #    [a.sets['RVE-1_FRONT'].nodes, a.sets['RVE-1_BACK'].nodes,   'front'] ]
        self.nodes = nodes

        # Find nodes on faces
        self.faces = {'LEFT': {'x': 0.0, 'y': None, 'z': None},
                      'RIGHT': {'x': 1.0, 'y': None, 'z': None},
                      'BOTTOM': {'x': None, 'y': 0.0, 'z': None},
                      'TOP': {'x': None, 'y': 1.0, 'z': None},
                      'BACK': {'x': None, 'y': None, 'z': 0.0},
                      'FRONT': {'x': None, 'y': None, 'z': 1.0}, }

        # Find Master Nodes
        if not MN:
            self.MN = self.masterNodes()  # Improve for non cubic models
        else:
            self.MN = MN

        self.faceLabels = {}
        for i, (nodesFaceA, nodesFaceB, face) in enumerate(pairs):
            # Works coupling multiple faces with the same faceLabel
            self.couples[i] = PBC.FACES_dict[face.upper()]
            if verbose: print self.couples[i]
            faceA, faceB, _ = PBC.FACES_dict[face.upper()]

            # Master face
            self.faceLabels[faceA + str(i)] = self.faceNodes(x=self.faces[faceA]['x'], y=self.faces[faceA]['y'],
                                                             z=self.faces[faceA]['z'], faceNodes=nodesFaceA)

            # Slave face
            self.faceLabels[faceB + str(i)] = self.faceNodes(x=self.faces[faceB]['x'], y=self.faces[faceB]['y'],
                                                             z=self.faces[faceB]['z'], faceNodes=nodesFaceB)
        # </editor-fold>

        if verbose: print self.couples
        if verbose: print 'Master nodes: ', self.MN

        tPrev = time.time()
        self.coupleNodes(forbiddenNodes)
        if verbose: print('Time coupling: %f s.' % (time.time() - tPrev))

        ## Write text file to include periodic boundary conditions
        tPrev = time.time()
        self.writePBC()
        if verbose: print('Time writing: %f s.' % (time.time() - tPrev))
        if verbose: print('TOTAL TIME: %f s.' % (time.time() - tIni))

    def writePBC(self):
        f = open(PBC.fileName, "w")
        f.write('*EQUATION\n')
        # print 'dimensions: ', self.dimensions
        for slave, master, mn in self.couplingEquations:
            for u in range(self.dimensions):
                f.write(
                    '3\n\t{0:9d}, {3:d}, 1.00,\t {1:9d}, {3:d}, -1.00,\t {2:9d}, {3:d}, -1.00\n'.format(master, slave,
                                                                                                        mn, u + 1))
        print('File with periodic boundary conditions created: %s' % (PBC.fileName))
        f.close()
        return 0

    def _debug_writePBC(self):
        f = open('DEBUG-' + PBC.fileName, "w")
        f.write('*DEBUG\n')
        # print 'dimensions: ', self.dimensions
        for slave, master, mn in self.couplingEquations:
            for u in range(self.dimensions):
                f.write('{0:9d}, {1:9d}, {2:9d}\n'.format(master, slave, mn, u + 1))
        print('File with periodic boundary conditions for debugging: %s' % (PBC.fileName))
        f.close()
        return 0

    def writePBCexplicit(self, offsetMN=10000000, offsetElems=10000000, filename='PBCexplicit'):
        """
        :param offsetMN: starting label for the virtual master nodes
        :param offsetElems: starting label for the periodic elements
        :return:
        """
        # Translate geometric
        uMN = {}
        for i, mn in enumerate(self.MN):
            uMN[mn] = (offsetMN + 3 + i, offsetMN + i)

        f = open(filename + '.inp', "w")
        prelude = "*NODE, NSET=N_O\n"
        prelude += "  {0:9d}, -1., -1., -1.\n".format(offsetMN + 4)
        prelude += "  {0:9d}, -1., -1., -1.\n".format(offsetMN + 5)
        prelude += "  {0:9d}, -1., -1., -1.\n".format(offsetMN + 6)
        prelude += "*NODE, NSET=N_X\n"
        prelude += "  {0:9d}, 10., 0., 0.\n".format(offsetMN + 1)
        prelude += "*NODE, NSET=N_Y\n"
        prelude += "  {0:9d}, 0., 10., 0.\n".format(offsetMN + 2)
        prelude += "*NODE, NSET=N_Z\n"
        prelude += "  {0:9d}, 0., 0., 10.\n".format(offsetMN + 3)
        prelude += "*User Element, Nodes=4, Type=VU1001, I Properties=1, Properties=4, Coordinates=3, Variables=24\n"
        prelude += "  1,2,3\n"
        prelude += "*Element, Type=VU1001, Elset=Constrain\n"

        f.write(prelude)

        # f.write('*EQUATION\n')
        # print 'dimensions: ', self.dimensions
        for i, (slave, master, mn) in enumerate(self.couplingEquations):
            mn_0, mn_i = uMN[mn]
            f.write(" {0:9d}, {1:9d}, {2:9d}, {3:9d}, {4:9d}\n".format(offsetElems + i, master, slave, mn_i, mn_0))

        print('File with periodic boundary conditions created: {0:s}'.format(filename + '.inp'))

        f.write(
            "*Uel Property, Elset=Constrain\n**    ak,     ad,    am0,    am1,   frequency\n    <ak>,   <ad>,  <am0>,  <am1>,      100000")

        f.close()
        return 0

    def coupleNodes(self, forbiddenNodes=[]):
        # Couple nodes of opposite faces and Master nodes
        current_labels = [MN for MN in self.MN] + forbiddenNodes
        self.couplingEquations = list()

        for i, (faceMaster, faceSlave, MN_index) in self.couples.items():
            i_s = str(i)
            labelsFaceSlave = self.faceLabels[faceSlave + i_s]
            labelsFaceMaster = self.faceLabels[faceMaster + i_s]
            # print('%s: %d nodes' % (faceSlave, len(labelsFaceSlave)))
            # print('%s: %d nodes' % (faceMaster, len(labelsFaceMaster)))

            if len(labelsFaceSlave) == len(labelsFaceMaster):
                if PBC.verbose: print 'Matched: ',

                for labelSlave, labelMaster in zip(labelsFaceSlave, labelsFaceMaster):
                    if (labelMaster not in current_labels):
                        # print 'Master-%d\t Slave-%d\t MN-%d' % (labelMaster, labelSlave, self.MN[MN_index])
                        self.couplingEquations.append((labelSlave, labelMaster, self.MN[MN_index]))

                current_labels += labelsFaceMaster
            else:
                # Nodes are not linked
                print 'NOT MATCHED: ',

            if PBC.verbose: print '%s (%d) - %s (%d)' % (
            faceMaster + i_s, len(labelsFaceMaster), faceSlave + i_s, len(labelsFaceSlave))

        return 0

    def faceNodes(self, x=None, y=None, z=None, faceNodes=None):
        """
        This method finds the labels in a constant coordinate
        :param nodes:
        :param x:
        :param y:
        :param z:
        :return:
        """
        # Find nodes whose 'coordinate' is a given value
        if PBC.verbose: print('Finding nodes on: ')
        if isfloat(x):
            # Left-right PBC couple
            index = 0
            coord = float(x)
            order = ['z', 'y']
            if PBC.verbose: print('x = %4.2f' % coord)
        elif isfloat(y):
            # Top-bottom
            index = 1
            coord = float(y)
            order = ['z', 'x']
            if PBC.verbose: print('y = %4.2f' % coord)
        elif isfloat(z):
            # Front-back
            index = 2
            coord = float(z)
            order = ['x', 'y']
            if PBC.verbose: print('z = %4.2f' % coord)
        else:
            raise ValueError("No coordinate specified")

        currentNodes = [(node,
                         round(self.nodes[node][0], PBC.decimals),
                         round(self.nodes[node][1], PBC.decimals),
                         round(self.nodes[node][2], PBC.decimals))
                        for node in faceNodes]

        # Sort labels in ascending order of x and/or y and/or z
        dtype = [('label', 'l'), ('x', 'float'), ('y', 'float'), ('z', 'float')]
        currentNodesArray = np.array(currentNodes, dtype=dtype)
        sortedNodes = np.sort(currentNodesArray, order=order)  # order in ascending coordinates
        sortedLabels = [node[0] for node in sortedNodes]
        return sortedLabels

    def masterNodes(self):
        """ Returns labels of the Master Nodes """
        N_xy = [i for i, z in enumerate(self.mycoords[2]) if z == 0.0]

        # # Master node 0
        MN_0 = [(i, self.mylabels[i]) for i in N_xy if (self.mycoords[0][i] == self.mycoords[1][i] == 0.)][0][1]

        # # Master node x
        MN_x = \
        [(i, self.mylabels[i]) for i in N_xy if (self.mycoords[0][i] == self.L) and (self.mycoords[1][i] == 0.)][0][1]

        # # Master node y
        MN_y = \
        [(i, self.mylabels[i]) for i in N_xy if (self.mycoords[0][i] == 0.) and (self.mycoords[1][i] == self.H)][0][1]

        N_xz = [i for i, y in enumerate(self.mycoords[1]) if y == 0.0]
        # # Master node z
        MN_z = \
        [(i, self.mylabels[i]) for i in N_xz if (self.mycoords[0][i] == 0.) and (self.mycoords[2][i] == self.w)][0][1]

        # # # Master node 0
        # MN_0 = [node.label for node in self.nodes if node.coordinates==(0., 0., 0.)][0]
        #
        # # # Master node X
        # MN_x = [node.label for node in self.nodes if node.coordinates==(self.L, 0., 0.)][0]
        #
        # # # Master node Y
        # MN_y = [node.label for node in self.nodes if node.coordinates==(0., self.H, 0.)][0]
        #
        # # # Master node Z
        # MN_z = [node.label for node in self.nodes if node.coordinates==(0., 0., self.w)][0]

        print '--MN-- 0:{0:d} x:{1:d} y:{2:d} z:{3:d}'.format(MN_0, MN_x, MN_y, MN_z)

        return (MN_0, MN_x, MN_y, MN_z)

    def modelDimensions(self):
        """
        Compute dimensions of the model as the maximum coordinate on each direction
        """
        L = round(max(self.mycoords[0]), PBC.decimals)
        H = round(max(self.mycoords[1]), PBC.decimals)
        w = round(max(self.mycoords[2]), PBC.decimals)
        print 'Dimensions: {0:.2f} x {1:.2f} x {2:.2f}'.format(L, H, w)
        return (L, H, w)


if __name__ == '__main__':
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *

    # from driverUtils import executeOnCaeStartup

    if 1:
        model = mdb.models.values()[0]
        p = model.parts.values()[0]
        # pm = model.parts['MATRIX']
        # pf1 = model.parts['FIBER-1']
        # pf2 = model.parts['FIBER-2']

        # pm = model.rootAssembly

        # pm = model.rootAssembly.instances['Matrix-1']
        # pf = model.rootAssembly.instances['Fibers-1']
        # nodes = pm.nodes

        # model = mdb.models['Cube_125000elems']
        # p = model.parts.values()[0]
        # p = model.rootAssembly.instances.values()[0]
        # nodes =  [ [p.sets['MATRIX-1_RIGHT'].nodes, p.sets['MATRIX-1_LEFT'].nodes,   'right'],
        #            [p.sets['MATRIX-1_TOP'].nodes,   p.sets['MATRIX-1_BOTTOM'].nodes, 'top'],
        #            [p.sets['FRONT'].nodes,   p.sets['BACK'].nodes, 'front']]

        # nodes =  [ [p.sets['FRONT_F'].nodes,   p.sets['BACK_F'].nodes, 'front']]

        # nodes =  [ [pm.sets['RIGHT'].nodes,  pm.sets['LEFT'].nodes, 'right'],
        # [pm.sets['TOP'].nodes,    pm.sets['BOTTOM'].nodes, 'top'],
        #           [pm.sets['FRONT'].nodes,  pm.sets['BACK'].nodes, 'front'],
        #           ]

        # nodes =  [
        #            [pm.sets['RIGHT'].nodes,  pm.sets['LEFT'].nodes, 'right'],
        #            ##[pm.sets['TOP'].nodes,    pm.sets['BOTTOM'].nodes, 'top'],
        #            [pm.sets['FRONT'].nodes,    pm.sets['BACK'].nodes, 'front'],
        #            [pf1.sets['FACE_A'].nodes,  pf1.sets['FACE_B'].nodes, 'front'],
        #            [pf2.sets['FACE_A'].nodes,  pf2.sets['FACE_B'].nodes, 'right'],
        #            ### [pm.sets['FIBER_FRONT'].nodes,  pm.sets['FIBER_BACK'].nodes, 'front']
        #             ]
        # forbiddenNodes = [n.label for n in pf1.sets['SURF'].nodes] + [n.label for n in pf2.sets['SURF'].nodes]
        # pbc = PBC(nodes, dimensions=3, fileName='PBC-U45sall_F2', auto=False, decimals=6,
        #          MN=[0, 1000001, 1000002, 1000003], forbiddenNodes=[])
        nodes = [
            [p.sets['RIGHT_M'].nodes, p.sets['LEFT_M'].nodes, 'right'],
            ##[pm.sets['TOP'].nodes,    pm.sets['BOTTOM'].nodes, 'top'],
            [p.sets['FRONT_M'].nodes, p.sets['BACK_M'].nodes, 'front'],
            [p.sets['FACE_A2'].nodes, p.sets['FACE_B2'].nodes, 'front'],
            [p.sets['FACE_A1'].nodes, p.sets['FACE_B1'].nodes, 'right'],
            ### [pm.sets['FIBER_FRONT'].nodes,  pm.sets['FIBER_BACK'].nodes, 'front']
        ]

        pbc = PBC(nodes, dimensions=3, auto=False, decimals=6, fileName='PBC-U45e.txt',
                  MN=[-100, 1000001, 1000002, 1000003])

        # nodes = p.nodes

        # pbc._debug_writePBC()

        # pbc = PBC(nodes, dimensions=3, fileName='PBC', auto=False, forbiddenNodes=[],
        #           decimals=3)

        # nodes = [ [p.sets['RIGHT'].nodes, p.sets['LEFT'].nodes,   'right'], ]

        # pbc = PBC(pm.nodes, auto=False, dimensions=3, fileName='PBC-RP',
        #             MN=[1000000,1000001,1000002,1000003],)

        # pbc.writePBCexplicit(filename='PBE_'+l)
