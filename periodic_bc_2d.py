from abaqus import *
from abaqusConstants import *
from regionToolset import Region

"""
2D Periodic Boundary Condition Creation
Author: Rutger Kok
Date: 02/04/2020

Adapted from:
    Ever J. Barbero. Finite Element Analysis of Composite Materials, 
    CRC Press, Boca Raton, FL, 2007. ISBN: 1-4200-5433-3.

1) Model must contain single part called 'Specimen'

2) Geometry is defined as follows:

                        Face 2
                    2____________1
                    |            |
                    |            |
            Face 3  |            | Face 1
                    |            |
                    |____________|
                    3            4
                        Face 4

    Face1: right face
    Face2: top face
    Face3: left face
    Face4: bottom face
    Vertex1:  vertex between Face1 and Face2
    Vertex2:  vertex between Face 2 and Face3
    Vertex3:  vertex between Face 3 and Face4
    Vertex4:  vertex between Face 4 and Face1

3) The part MUST be meshed with an equal number of nodes at opposing Faces.

"""


def periodicBC(modelName, xmin, ymin, xmax, ymax, dispVector):

    activeModel = mdb.models[modelName]
    assembly = activeModel.rootAssembly
    part = activeModel.parts['Specimen']
    partEdges = part.edges
    partInstance = assembly.instances['Specimen']

    xmid = ymid = (abs(xmin)+abs(xmax))/2.0 + xmin

    # Creating faces
    tol = 0.001
    face1Edges = partEdges.getByBoundingBox(xmax-tol, ymin-tol, -1.0, xmax+tol,
                                            ymax+tol, 1.0)
    face1 = part.Set(edges=face1Edges, name='Face 1')
    face2Edges = partEdges.getByBoundingBox(xmin-tol, ymax-tol, -1.0, xmax+tol,
                                            ymax+tol, 1.0)
    face2 = part.Set(edges=face2Edges, name='Face 2')
    face3Edges = partEdges.getByBoundingBox(xmin-tol, ymin-tol, -1.0, xmin+tol,
                                            ymax+tol, 1.0)
    face3 = part.Set(edges=face3Edges, name='Face 3')
    face4Edges = partEdges.getByBoundingBox(xmin-tol, ymin-tol, -1.0, xmax+tol,
                                            ymin+tol, 1.0)
    face4 = part.Set(edges=face4Edges, name='Face 4')

    # Creating vertices
    partVertices = part.vertices
    vertex1 = part.Set(vertices=partVertices.findAt(((xmax, ymax, 0.0), ), ),
                       name='Vertex 1')
    vertex2 = part.Set(vertices=partVertices.findAt(((xmin, ymax, 0.0), ), ),
                       name='Vertex 2')
    vertex3 = part.Set(vertices=partVertices.findAt(((xmin, ymin, 0.0), ), ),
                       name='Vertex 3')
    vertex4 = part.Set(vertices=partVertices.findAt(((xmax, ymin, 0.0), ), ),
                       name='Vertex 4')

    masterNode1ID = assembly.ReferencePoint(point=(xmid, ymid, 1.0)).id
    masterNode2ID = assembly.ReferencePoint(point=(xmid, ymid, 2.0)).id
    masterNode1 = assembly.referencePoints[masterNode1ID]
    masterNode2 = assembly.referencePoints[masterNode2ID]
    masterNodeSet1 = assembly.Set(referencePoints=(masterNode1, ),
                                      name='MasterNode1')
    masterNodeSet2 = assembly.Set(referencePoints=(masterNode2, ),
                                      name='MasterNode2')
    masterNodeRegion1 = Region(
        referencePoints=(assembly.referencePoints[masterNode1ID], ))
    masterNodeRegion2 = Region(
        referencePoints=(assembly.referencePoints[masterNode1ID], ))

    # Construction Pairs of nodes
    # Face 1 and 3 (right-left)
    face13Paired = []
    face13Paired.append(SortListOfNodes(face1, 1))
    face13Paired.append(SortListOfNodes(face3, 1))
    # Face 2 and 4 (top-bottom)
    face24Paired = []
    face24Paired.append(TakeVertexOut(SortListOfNodes(face2, 0)))
    face24Paired.append(TakeVertexOut(SortListOfNodes(face4, 0)))

    # Top and Bottom faces (2 & 4)
    for i in range(len(face24Paired[0])):
        part.Set(name='MasterFace24-'+str(i),
                 nodes=(part.nodes[face24Paired[0][i]:face24Paired[0][i]+1],))
        part.Set(name='SlaveFace24-'+str(i),
                 nodes=(part.nodes[face24Paired[1][i]:face24Paired[1][i]+1],))
        # (6.14, i=1)
        activeModel.Equation(name='Constraint24-1-'+str(i),
                             terms=((1.0, 'Specimen.MasterFace24-'+str(i), 1),
                                    (-1.0, 'Specimen.SlaveFace24-'+str(i), 1),
                                    (1.0, 'MasterNode2', 1)))
        # (6.14, i=2)
        activeModel.Equation(name='Constraint24-2-'+str(i),
                             terms=((1.0, 'Specimen.MasterFace24-'+str(i), 2),
                                    (-1.0, 'Specimen.SlaveFace24-'+str(i), 2),
                                    (1.0, 'MasterNode2', 1)))

    # Left and Right faces (1 & 3)
    for j in range(len(face13Paired[0])):
        part.Set(name='MasterFace13-'+str(j),
                 nodes=(part.nodes[face13Paired[0][j]:face13Paired[0][j]+1],))
        part.Set(name='SlaveFace13-'+str(j),
                 nodes=(part.nodes[face13Paired[1][j]:face13Paired[1][j]+1],))
        # (6.13, i=1)
        activeModel.Equation(name='Constraint13-1-'+str(j),
                             terms=((1.0, 'Specimen.MasterFace13-'+str(j), 1),
                                    (-1.0, 'Specimen.SlaveFace13-'+str(j), 1),
                                    (1.0, 'MasterNode1', 1)))
        # (6.13, i=2)
        activeModel.Equation(name='Constraint13-2-'+str(j),
                             terms=((1.0, 'Specimen.MasterFace13-'+str(j), 2),
                                    (-1.0, 'Specimen.SlaveFace13-'+str(j), 2),
                                    (1.0, 'MasterNode1', 2)))
    # Apply BCs to master nodes
    if dispVector[0]:
        activeModel.DisplacementBC(amplitude=UNSET,
                                   createStepName='Loading Step',
                                   distributionType=UNIFORM, fieldName='',
                                   fixed=OFF, localCsys=None, name='BC-13',
                                   region=masterNodeRegion1, u1=dispVector[0],
                                   u2=UNSET, ur3=UNSET)
    if dispVector[1]:
        activeModel.DisplacementBC(amplitude=UNSET,
                                   createStepName='Loading Step',
                                   distributionType=UNIFORM, fieldName='',
                                   fixed=OFF, localCsys=None, name='BC-24',
                                   region=masterNodeRegion2, u1=UNSET,
                                   u2=dispVector[1], ur3=UNSET)

    activeModel.rootAssembly.regenerate()


def TakeVertexOut(face):
    face.pop(0)
    face.pop(-1)
    return face


def SortListOfNodes(face, coordinate):
    newlist = []
    oldlist = []
    for i in range(len(face.nodes)):
        oldlist.append(face.nodes[i].coordinates[coordinate])
    orderedlist = sorted(oldlist)
    for j in range(len(oldlist)):
        vecindex = oldlist.index(orderedlist[j])
        newlist.append(face.nodes[vecindex].label-1)
    return newlist
