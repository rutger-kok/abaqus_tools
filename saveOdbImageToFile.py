'''
Script to create image files from odbs
'''

from abaqusConstants import *
from abaqus import *
from caeModules import *
from visualization import *

def findOdbs(directory):
    ''' Search for .odb files in a directory.'''
    odbPaths = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.odb'):
                odbPaths.append(os.path.join(root, f))
    return odbPaths

def saveOdbImage(odbPath):
    '''
    Save viewport of an Abaqus ODB to a file as a .png
    '''
    root = odbPath[0:odbPath.rfind('\\')+1]  # directory odb file is in
    odbName = odbPath[odbPath.rfind('\\')+1:odbPath.rfind('.')]
    odb = openOdb(odbPath)  # open the odb file

    # display odb in viewport
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    # turn off annotations
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(triad=OFF, 
        title=OFF, state=OFF, annotations=OFF, compass=OFF)
    # set legend font options
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
        legendFont='-*-verdana-medium-r-normal-*-*-40-*-*-p-*-*-*')
    # display contours and modify display options
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
            CONTOURS_ON_DEF, ))
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(
        INVARIANT, 'Mises'), )
    session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
        maxAutoCompute=OFF, minAutoCompute=OFF, maxValue=2.25, minValue=0)    
    session.linkedViewportCommands.setValues(_highlightLinkedViewports=True)
    # show/hide specific regions of a model
    leaf = dgo.LeafFromElementSets(elementSets=('Between Clamps', ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    # set display angle
    session.viewports['Viewport: 1'].view.setValues(session.views['Front'])
    # set edge display options
    session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        visibleEdges=FEATURE)
    # set image size, specify path, and define image format
    session.pngOptions.setValues(imageSize=(3000, 1686))
    session.printOptions.setValues(reduceColors=False)
    imageName = 'C:\\Workspace\\ELSA\\Images\\' + odbName
    session.printToFile(fileName=imageName, format=PNG, 
        canvasObjects=(session.viewports['Viewport: 1'], ))
        
if __name__ == '__main__':
    d = 'C:\\Workspace\\ELSA'
    filePaths = findOdbs(d)
    for odbPath in filePaths:
        saveOdbImage(odbPath)
