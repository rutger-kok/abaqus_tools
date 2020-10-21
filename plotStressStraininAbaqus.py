from odbAccess import *
from visualization import XYData, USER_DEFINED

# Use the output database displayed in the current viewport
vp = session.viewports[session.currentViewportName]
odb = vp.displayedObject
if type(odb) != visualization.OdbType:
    raise ValueError, 'An odb must be displayed in the current viewport.'

odbPath = vp.displayedObject.name
name = odbPath[odbPath.rfind('\\')+1:odbPath.rfind('.')]

data = []
for frame in odb.steps['Step-1'].frames:
    stress = frame.fieldOutputs['S']
    s11 = stress.values[0].data[0]
    strain = frame.fieldOutputs['LE']
    le11 = strain.values[0].data[0]
    data.append((le11,s11))

plotName = 'S11 vs LE11'
xAxisTitle = 'LE11'
yAxisTitle = 'S11'
xyData = session.XYData(plotName, data)
curve = session.Curve(xyData)
xyPlot = session.XYPlot(plotName)
chart = xyPlot.charts.values()[0]
chart.setValues(curvesToPlot=(plotName, ))
chart.axes1[0].axisData.setValues(useSystemTitle=False,
                                    title=xAxisTitle)
chart.axes2[0].axisData.setValues(useSystemTitle=False,
                                    title=yAxisTitle)

# Display the XY Plot in the current viewport
vp = session.viewports[session.currentViewportName]
vp.setValues(displayedObject=xyPlot)