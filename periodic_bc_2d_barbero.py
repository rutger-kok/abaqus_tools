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


def periodicBC(modelName, xmin, ymin, xmax, ymax, strain):

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

    masterNodeID = part.ReferencePoint(point=(xmid, ymid, 0.0)).id
    masterNode = part.referencePoints[masterNodeID]
    masterNodeSet = part.Set(referencePoints=(masterNode, ), name='MasterNode')
    masterNodeRegion = Region(
        referencePoints=(partInstance.referencePoints[masterNodeID], ))

    activeModel.DisplacementBC(amplitude=UNSET, createStepName='Loading Step',
                               distributionType=UNIFORM, fieldName='',
                               fixed=OFF, localCsys=None, name='BC-1',
                               region=masterNodeRegion, u1=1.0, u2=UNSET,
                               ur3=UNSET)

    # Construction Pairs of nodes
    # Face 1 and 3 (right-left)
    face13Paired = []
    face13Paired.append(TakeVertexOut(SortListOfNodes(face1, 1)))
    face13Paired.append(TakeVertexOut(SortListOfNodes(face3, 1)))
    # Face 2 and 4 (top-bottom)
    face24Paired = []
    face24Paired.append(TakeVertexOut(SortListOfNodes(face2, 0)))
    face24Paired.append(TakeVertexOut(SortListOfNodes(face4, 0)))

    # Create constraint equations
    # Vertices

    # Master V1 (Contained in 1 and 3)
    activeModel.Equation(name='ConstraintV1-V3-1',
        terms=((1.0, 'Specimen.Vertex 1', 1), (-1.0, 'Specimen.Vertex 3', 1),
               (-strain[0]*(vertex1.nodes[-1].coordinates[0] -
                vertex3.nodes[-1].coordinates[0]) +
                -strain[2]/2.*(vertex1.nodes[-1].coordinates[1] -
                vertex3.nodes[-1].coordinates[1]), 'Specimen.MasterNode', 1)))
    activeModel.Equation(name='ConstraintV1-V3-2',
        terms=((1.0, 'Specimen.Vertex 1', 2), (-1.0, 'Specimen.Vertex 3', 2),
               (-strain[2]/2.*(vertex1.nodes[-1].coordinates[0] -
                vertex3.nodes[-1].coordinates[0]) +
                -strain[1]*(vertex1.nodes[-1].coordinates[1] -
                vertex3.nodes[-1].coordinates[1]), 'Specimen.MasterNode', 1)))

    # Master V2 (Contained in 2 and 4)
    activeModel.Equation(name='ConstraintV2-V4-1',
        terms=((1.0, 'Specimen.Vertex 2', 1), (-1.0, 'Specimen.Vertex 4', 1),
               (strain[2]/2.*(vertex4.nodes[-1].coordinates[1] -
                vertex2.nodes[-1].coordinates[1]) +
                strain[0]*(vertex4.nodes[-1].coordinates[0] -
                vertex2.nodes[-1].coordinates[0]), 'Specimen.MasterNode', 1)))
    activeModel.Equation(name='ConstraintV2-V4-2',
        terms=((1.0, 'Specimen.Vertex 2', 2), (-1.0, 'Specimen.Vertex 4', 2),
               (-strain[1]*(vertex2.nodes[-1].coordinates[1] -
                vertex4.nodes[-1].coordinates[1])  
                -strain[2]/2.*(vertex2.nodes[-1].coordinates[0] -
                vertex4.nodes[-1].coordinates[0]), 'Specimen.MasterNode', 1)))

    # For the edges
    for ii in range(len(face13Paired[0])):
        part.Set(name='MasterFace13-'+str(ii),
                 nodes=(part.nodes[face13Paired[0][ii]:face13Paired[0][ii]+1],))
        part.Set(name='SlaveFace13-'+str(ii),
                 nodes=(part.nodes[face13Paired[1][ii]:face13Paired[1][ii]+1],))
        # (6.13, i=1)
        activeModel.Equation(name='Constraint13-1-'+str(ii),
            terms=((1.0, 'Specimen.MasterFace13-'+str(ii), 1),
                   (-1.0, 'Specimen.SlaveFace13-'+str(ii), 1),
                   (-strain[0]*(part.nodes[face13Paired[0][ii]].coordinates[0] -
                    part.nodes[face13Paired[1][ii]].coordinates[0]),
                    'Specimen.MasterNode', 1)))
        # (6.13, i=2)
        activeModel.Equation(name='Constraint13-2-'+str(ii),
            terms=((1.0, 'Specimen.MasterFace13-'+str(ii), 2),
                   (-1.0, 'Specimen.SlaveFace13-'+str(ii), 2),
                   (-strain[2]/2.*(part.nodes[face13Paired[0][ii]].coordinates[0] -
                    part.nodes[face13Paired[1][ii]].coordinates[0]),
                    'Specimen.MasterNode', 1)))

    for ii in range(len(face24Paired[0])):
        part.Set(name='MasterFace24-'+str(ii),
                 nodes=(part.nodes[face24Paired[0][ii]:face24Paired[0][ii]+1],))
        part.Set(name='SlaveFace24-'+str(ii),
                 nodes=(part.nodes[face24Paired[1][ii]:face24Paired[1][ii]+1],))
        # (6.14, i=1)
        activeModel.Equation(name='Constraint24-1-'+str(ii),
            terms=((1.0, 'Specimen.MasterFace24-'+str(ii), 1),
                   (-1.0, 'Specimen.SlaveFace24-'+str(ii), 1),
                   (-strain[2]/2.*(part.nodes[face24Paired[0][ii]].coordinates[1] -
                    part.nodes[face24Paired[1][ii]].coordinates[1]),
                    'Specimen.MasterNode', 1)))
        # (6.14, i=2)
        activeModel.Equation(name='Constraint24-2-'+str(ii),
            terms=((1.0, 'Specimen.MasterFace24-'+str(ii), 2),
                   (-1.0, 'Specimen.SlaveFace24-'+str(ii), 2),
                   (-strain[1]*(part.nodes[face24Paired[0][ii]].coordinates[1]-
                    part.nodes[face24Paired[1][ii]].coordinates[1]),
                    'Specimen.MasterNode', 1)))        

    activeModel.rootAssembly.regenerate()


def TakeVertexOut(face):
    face.pop(0)
    face.pop(-1)
    return face


def SortListOfNodes(face, coordinate):
    newlist = []
    oldlist = []
    for ii in range(len(face.nodes)):
        oldlist.append(face.nodes[ii].coordinates[coordinate])
    orderedlist = sorted(oldlist)
    for ii in range(len(oldlist)):
        vecindex = oldlist.index(orderedlist[ii])
        newlist.append(face.nodes[vecindex].label-1)
    return newlist
