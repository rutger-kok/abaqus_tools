from sys import path
githubPath = 'C:\\GitHub'
path.append('C:\\Python27\\Lib\\site-packages')
# path.append(githubPath + '\\path_to_mcs')
# import modelCreationScript as mcs
from itertools import product
from abaqusConstants import *
import csv


def parametricStudy():
    # define parameters and create design space
    param1 = (30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0)
    param2 = (65.0, )
    param3 = (15.0, 20.0, 25.0, 35.0)
    designSpace = product(param1, param2, param3)

    reportFilePath = 'C:\\Workspace\\PS_Summary.csv'
    headings = ['param1', 'param2', 'param3', 'result']

    # define any fixed parameters
    fixedParam1 = 300.0

    # run simulations
    with open(reportFilePath, 'ab') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(headings)                       
        for study in designSpace:
            p1, p2, p3 = study[0], study[1], study[2]
            r = mcs.main()  # result from model script
            csvWriter.writerow([p1, p2, p3, r])


if __name__ == '__main__':
    parametricStudy()