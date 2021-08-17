
"""
3D Periodic Boundary Condition Creation
Author: Rutger Kok
Date: 15/04/2020

"""
from abaqus import *
from abaqusConstants import *
from regionToolset import Region
import numpy as np
import math

def periodicBC(modelName, dimensions):

    activeModel = mdb.models[modelName]
    asmbly = activeModel.rootAssembly

    xMin = dimensions[0]
    yMin = dimensions[1]
    zMin = dimensions[2]
    xMax = dimensions[3]
    yMax = dimensions[4]
    zMax = dimensions[5]
    xMid = xMin + (xMax - xMin) / 2.0
    yMid = yMin + (yMax - yMin) / 2.0

    # Creating faces
    createNodeSet(asmbly, 'F', xMax, yMin, zMin, xMax, yMax, zMax, (0, 1, 1))
    createNodeSet(asmbly, 'Bk', xMin, yMin, zMin, xMin, yMax, zMax, (0, 1, 1))
    createNodeSet(asmbly, 'L', xMin, yMin, zMax, xMax, yMax, zMax, (1, 1, 0))
    createNodeSet(asmbly, 'R', xMin, yMin, zMin, xMax, yMax, zMin, (1, 1, 0))
    createNodeSet(asmbly, 'T', xMin, yMax, zMin, xMax, yMax, zMax, (1, 0, 1))
    createNodeSet(asmbly, 'Bm', xMin, yMin, zMin, xMax, yMin, zMax, (1, 0, 1))

    # Creating edges
    createNodeSet(asmbly, 'FT', xMax, yMax, zMin, xMax, yMax, zMax, (0, 0, 1))
    createNodeSet(asmbly, 'FBm', xMax, yMin, zMin, xMax, yMin, zMax, (0, 0, 1))
    createNodeSet(asmbly, 'FR', xMax, yMin, zMin, xMax, yMax, zMin, (0, 1, 0))
    createNodeSet(asmbly, 'FL', xMax, yMin, zMax, xMax, yMax, zMax, (0, 1, 0))
    createNodeSet(asmbly, 'BkT', xMin, yMax, zMin, xMin, yMax, zMax, (0, 0, 1))
    createNodeSet(asmbly, 'BkBm', xMin, yMin, zMin, xMin, yMin, zMax, (0, 0, 1))
    createNodeSet(asmbly, 'BkR', xMin, yMin, zMin, xMin, yMax, zMin, (0, 1, 0))
    createNodeSet(asmbly, 'BkL', xMin, yMin, zMax, xMin, yMax, zMax, (0, 1, 0))
    createNodeSet(asmbly, 'TR', xMin, yMax, zMin, xMax, yMax, zMin, (1, 0, 0))
    createNodeSet(asmbly, 'BmR', xMin, yMin, zMin, xMax, yMin, zMin, (1, 0, 0))
    createNodeSet(asmbly, 'TL', xMin, yMax, zMax, xMax, yMax, zMax, (1, 0, 0))
    createNodeSet(asmbly, 'BmL', xMin, yMin, zMax, xMax, yMin, zMax, (1, 0, 0))

    # Creating vertices
    createVertexSet(asmbly, 'C1', xMax, yMax, zMax)
    createVertexSet(asmbly, 'C2', xMin, yMax, zMax)
    createVertexSet(asmbly, 'C3', xMin, yMax, zMin)
    createVertexSet(asmbly, 'C4', xMax, yMax, zMin)
    createVertexSet(asmbly, 'C5', xMax, yMin, zMax)
    createVertexSet(asmbly, 'C6', xMin, yMin, zMax)
    createVertexSet(asmbly, 'C7', xMin, yMin, zMin)
    createVertexSet(asmbly, 'C8', xMax, yMin, zMin)

    # Create master nodes to impose BCs on
    masterNode1ID = asmbly.ReferencePoint(point=(xMid, yMid, zMax + 1.0)).id
    masterNode2ID = asmbly.ReferencePoint(point=(xMid, yMid, zMax + 2.0)).id
    masterNode3ID = asmbly.ReferencePoint(point=(xMid, yMid, zMax + 3.0)).id
    masterNode1 = asmbly.referencePoints[masterNode1ID]
    masterNode2 = asmbly.referencePoints[masterNode2ID]
    masterNode3 = asmbly.referencePoints[masterNode3ID]
    masterNodeSet1 = asmbly.Set(referencePoints=(masterNode1, ),
                                name='MasterNode1')
    masterNodeSet2 = asmbly.Set(referencePoints=(masterNode2, ),
                                name='MasterNode2')
    masterNodeSet3 = asmbly.Set(referencePoints=(masterNode3, ),
                                name='MasterNode3')

    # Construction equations for pairs of nodes
    # Faces
    matchNodes(modelName, 'T', 'Bm', (0, 1, 0), (0, -1, 0))
    matchNodes(modelName, 'F', 'Bk', (1, 0, 0), (-1, 0, 0))
    matchNodes(modelName, 'L', 'R', (0, 0, 1), (0, 0, -1))
    # Edges
    matchNodes(modelName, 'FT', 'BkT', (1, 0, 0), (-1, 0, 0))
    matchNodes(modelName, 'BkT', 'BkBm', (0, 1, 0), (0, -1, 0))
    matchNodes(modelName, 'BkBm', 'FBm', (1, 0, 0), (1, 0, 0))
    matchNodes(modelName, 'FL', 'BkL', (1, 0, 0), (-1, 0, 0))
    matchNodes(modelName, 'BkL', 'BkR', (0, 0, 1), (0, 0, -1))
    matchNodes(modelName, 'BkR', 'FR', (1, 0, 0), (1, 0, 0))
    matchNodes(modelName, 'TL', 'BmL', (0, 1, 0), (0, -1, 0))
    matchNodes(modelName, 'BmL', 'BmR', (0, 0, 1), (0, 0, -1))
    matchNodes(modelName, 'BmR', 'TR', (0, 1, 0), (0, 1, 0))
    # Vertices
    matchNodes(modelName, 'C6', 'C2', (0, 1, 0), (0, 1, 0))
    matchNodes(modelName, 'C2', 'C3', (0, 0, 1), (0, 0, -1))
    matchNodes(modelName, 'C3', 'C4', (1, 0, 0), (1, 0, 0))
    matchNodes(modelName, 'C4', 'C8', (0, 1, 0), (0, -1, 0))
    matchNodes(modelName, 'C8', 'C5', (0, 0, 1), (0, 0, 1))
    matchNodes(modelName, 'C5', 'C1', (0, 1, 0), (0, 1, 0))
    matchNodes(modelName, 'C1', 'C7', (1, 1, 1), (-1.0, -1.0, -1.0))

    activeModel.rootAssembly.regenerate()


def createNodeSet(assembly, setName, xmin, ymin, zmin, xmax, ymax, zmax,
                  axesToTrim=None):
    tol1 = 0.001
    tol2 = 0.002
    xtol = tol1 - axesToTrim[0] * tol2
    ytol = tol1 - axesToTrim[1] * tol2
    ztol = tol1 - axesToTrim[2] * tol2
    findNodes = [inst.nodes.getByBoundingBox(xmin - xtol, ymin - ytol,
                                             zmin - ztol, xmax + xtol,
                                             ymax + ytol, zmax + ztol)
                 for inst in assembly.instances.values()
                 if inst.nodes.getByBoundingBox(xmin - xtol, ymin - ytol,
                                                zmin - ztol, xmax + xtol,
                                                ymax + ytol, zmax + ztol)]
    assembly.Set(nodes=findNodes, name=setName)


def createVertexSet(assembly, setName, x, y, z):
    findVertex = [inst.vertices.findAt(((x, y, z), ), )
                  for inst in assembly.instances.values()
                  if inst.vertices.findAt(((x, y, z), ), )]
    vertexSet = assembly.Set(vertices=findVertex, name=setName)


def matchNodes(modelName, masterSet, slaveSet, masterNodes, coeff):
    model = mdb.models[modelName]
    assembly = model.rootAssembly
    set1Nodes = assembly.sets[masterSet].nodes
    set2Nodes = assembly.sets[slaveSet].nodes
    set1Coords = [(node, node.coordinates[0], node.coordinates[1],
                   node.coordinates[2]) for node in set1Nodes]
    set2Coords = [(node, node.coordinates[0], node.coordinates[1],
                   node.coordinates[2]) for node in set2Nodes]
    for i, mNode in enumerate(masterNodes):
        s = [c + 1 for c in [0, 1, 2] if c != i]
        set1Sorted = sorted(set1Coords, key=lambda k: [k[s[0]], k[s[1]]])
        set2Sorted = sorted(set2Coords, key=lambda k: [k[s[0]], k[s[1]]])
        for j, node1 in enumerate(set1Sorted):
            node2 = set2Sorted[j]  # matched node in second set
            masterInstance = assembly.instances[node1[0].instanceName]
            slaveInstance = assembly.instances[node2[0].instanceName]
            slaveName = 'Slave-{}-{}-{}'.format(masterSet, slaveSet, j)
            masterName = 'Master-{}-{}-{}'.format(masterSet, slaveSet, j)
            siNodes = slaveInstance.nodes  # slave instance nodes
            miNodes = masterInstance.nodes  # master instance nodes
            snl = node2[0].label  # slave node label
            mnl = node1[0].label  # master node label
            assembly.Set(name=slaveName,
                         nodes=siNodes.sequenceFromLabels(((snl), ), ))
            assembly.Set(name=masterName,
                         nodes=miNodes.sequenceFromLabels(((mnl), ), ))
            dof = i + 1
            eqnName = '{}-{}-{}-{}'.format(masterSet, slaveSet, j, dof)
            mNode = 'MasterNode{}'.format(i + 1)
            model.Equation(name=eqnName,
                           terms=((1.0, slaveName, dof),
                                  (-1.0, masterName, dof),
                                  (coeff[i], mNode, dof)))
