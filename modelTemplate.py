from abaqus import *
from abaqusConstants import *
from math import pi
import mesh
import regionToolset
import os
from sys import path
import ast
path.append('C:\\Python27\\Lib\\site-packages')
path.append("R:")


class AbaqusModel():
    def __init__(self, modelName):
        self.modelName = modelName
        mdb.Model(name=self.modelName, modelType=STANDARD_EXPLICIT)
        self.model = mdb.models[self.modelName]
        self.assembly = self.model.rootAssembly
        # set the work directory
        wd = 'C:\\Workspace\\{}'.format(self.modelName)
        if not os.path.exists(wd):
            os.makedirs(wd)
        os.chdir(wd)

    def createMaterials(self):
        '''Create material data'''
        pass

    def createExplicitStep(self):
        # mass scaling applied if increment < 1e-6
        self.model.ExplicitDynamicsStep(
            name='Loading Step', previous='Initial', timePeriod=self.time,
            massScaling=((SEMI_AUTOMATIC, MODEL, THROUGHOUT_STEP, 0.0, 1e-06,
                          BELOW_MIN, 1, 0, 0.0, 0.0, 0, None), ))
        self.model.fieldOutputRequests['F-Output-1'].setValues(
            variables=('S', 'LE', 'U', 'V', 'A', 'RF', 'CSTRESS', 'CSDMG',
                       'SDV', 'STATUS'),
            numIntervals=outputIntervals)

    def getFacesByBBox(self, boundingBox):
        '''
        Get faces from bounding box for a model with a large number of
        instances. The function iterates through all instances and adds any
        faces which are within the defined bounding box.
        '''
        x1, y1, z1, x2, y2, z2 = boundingBox
        faces = [inst.faces.getByBoundingBox(x1, y1, z1, x2, y2, z2)
                 for inst in self.assembly.instances.values()
                 if inst.faces.getByBoundingBox(x1, y1, z1, x2, y2, z2)]
        return faces

    def applyContraints(self, dimensions):
        '''Apply constraints to parts'''

        self.model.SmoothStepAmplitude(name='Smoothing Amplitude', timeSpan=STEP,
                                       data=((0.0, 0.0), (1e-05, 1.0)))

    def createInteractionProperty(self):
        '''Cohesive zone interaction properties'''
        alpha = 50
        E_33 = 11.6
        G_12 = 6.47
        GIc = 300.0e-6
        GIIc = 800.0e-6
        Ne = 5

        # calculate cohesive zone properties according to Turon (2007)
        K1 = (alpha * E_33) / self.t_thickness
        K2 = (alpha * G_12) / self.t_thickness
        tau1 = ((9*pi*E_33*GIc)/(32*Ne*self.meshSize))**0.5
        tau2 = ((9*pi*E_33*GIIc)/(32*Ne*self.meshSize))**0.5
        
        self.model.ContactProperty('Tangential')
        self.model.interactionProperties['Tangential'].TangentialBehavior(
            formulation=PENALTY, directionality=ISOTROPIC,
            slipRateDependency=OFF, pressureDependency=OFF,
            temperatureDependency=OFF, dependencies=0, table=((0.15, ), ),
            shearStressLimit=None, maximumElasticSlip=FRACTION, fraction=0.005,
            elasticSlipStiffness=None)
        self.model.interactionProperties['Tangential'].NormalBehavior(
            pressureOverclosure=HARD, allowSeparation=ON,
            constraintEnforcementMethod=DEFAULT)
        self.model.ContactProperty('Cohesive')
        self.model.interactionProperties['Cohesive'].CohesiveBehavior(
            defaultPenalties=OFF, table=((K1, K2, K2), ))
        self.model.interactionProperties['Cohesive'].Damage(
            criterion=QUAD_TRACTION, initTable=((tau1, tau2, tau2), ),
            useEvolution=ON, evolutionType=ENERGY, useMixedMode=ON,
            mixedModeType=BK, exponent=1.75, evolTable=((GIc, GIIc, GIIc), ))

    def createInteractions(self):
        '''
        Find and create cohesive zone interactions (for an explicit
        model). Uses the built-in contact detection function to find contacts,
        then iterates over that list to create interactions which are part of a
        General Contact definition.'''
        # determine contacts
        self.model.contactDetection(
            defaultType=CONTACT, interactionProperty='Cohesive',
            nameEachSurfaceFound=OFF, createUnionOfMasterSurfaces=ON,
            createUnionOfSlaveSurfaces=ON, searchDomain=MODEL,
            separationTolerance=0.0001)
        # create explicit general contact definition
        self.model.ContactExp(name='GC', createStepName='Initial')
        generalContact = self.model.interactions['GC']
        generalContact.includedPairs.setValuesInStep(
            stepName='Initial', useAllstar=ON)
        # define 'Tangential' as default behaviour
        generalContact.contactPropertyAssignments.appendInStep(
            stepName='Initial', assignments=((GLOBAL, SELF, 'Tangential'), ))
        # assign cohesive behaviour to contacting tape surfaces
        for interact in self.model.interactions.values():
            if interact.name == 'GC':
                continue
            else:
                masterName = interact.master[0]
                slaveName = interact.slave[0]
                masterSurf = self.assembly.surfaces[masterName]
                slaveSurf = self.assembly.surfaces[slaveName]
                generalContact.contactPropertyAssignments.appendInStep(
                    stepName='Initial',
                    assignments=((masterSurf, slaveSurf, 'Cohesive'), ))
                del self.model.interactions['{}'.format(interact.name)]

    def createJob(self, cpus=4):
        mdb.Job(
            name=self.modelName, model=self.modelName, description='',
            atTime=None, waitMinutes=0, waitHours=0, queue=None, type=ANALYSIS,
            memoryUnits=PERCENTAGE, explicitPrecision=DOUBLE_PLUS_PACK,
            nodalOutputPrecision=FULL, echoPrint=OFF, modelPrint=OFF,
            contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
            resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN,
            numDomains=cpus, activateLoadBalancing=False,
            multiprocessingMode=DEFAULT, numCpus=cpus, memory=90)

    def saveModel(self):
        mdb.saveAs(pathName=self.modelName)

    def inputPopup(self):
        '''Get user input using a pop-up'''
        userInput = getInputs(fields=(('Field 1:', '(0, 90)'),
                                      ('Field 2:', '25')),
                              label='Please provide the following information',
                              dialogTitle='Model Parameters')
        self.field1 = ast.literal_eval(userInput[0])  # angles of tapes
        self.field2 = float(userInput[1])


if __name__ == '__main__':

    # Simulation parameters
    time = 5.0  # duration to simulate [ms]
    outputIntervals = 50  # requested field output intervals
    testSpeed = 0.5  # crosshead velocity

    # Material parameters
    specimenType = 'B'
    tapeAngles = (0, 90)  # define angles of tapes
    tapeWidths = 15.0
    tapeSpacing = 1  # number of gaps between tapes in interlacing pattern
    tapeThickness = 0.18  # cured ply thickness e.g. 0.18125
    undulationRatio = 0.09  # ratio of undulation amplitude to length
    nLayers = 4  # symmetric 8 ply laminate

    # Mesh sizes
    fineMesh = 0.125
    mediumMesh = 1.0
    coarseMesh = 3.0

    # Define specimen dimensions
    # xMin = -25.0
    # xMax = -xMin
    # yMin = -75.0
    # yMax = -yMin
    # fineRegion = Polygon([(xMin, yMin), (xMax, yMin), (xMax, yMax),
    #                       (xMin, yMax)])
    # dimensions = [xMin, yMin, xMax, yMax]

    # RVE dimensions
    xMin = yMin = -(tapeWidths / 2.0)
    xMax = yMax = xMin + (tapeSpacing + 1) * (tapeWidths)
    yMin = -75.0
    yMax = 75.0
    fineRegion = Polygon([(xMin, yMin), (xMax, yMin), (xMax, yMax),
                         (xMin, yMax)])
    dimensions = [xMin, yMin, xMax, yMax]
    

    # Create model
    mdl = TensileModel(specimenType, undulationRatio)
    mdl.setTestParameters(time, outputIntervals, testSpeed)
    mdl.setSpecimenParameters(tapeAngles, tapeWidths, tapeSpacing,
                              tapeThickness, undulationRatio, nLayers)
    mdl.createMaterials()
    paths_f, grid_f = mdl.createTapePaths(fineRegion)
    mdl.create3DTapePartGroup(grid_f, mediumMesh)
    mdl.merge3DTapes(grid_f, paths_f)
    mdl.createExplicitStep()
    mdl.applyContraints(dimensions)
    mdl.createInteractionProperty()
    mdl.createInteractions()
    mdl.createJob()
    mdl.saveModel()
