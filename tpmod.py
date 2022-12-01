
# export SITK_SHOW_COMMAND=fslview


import SimpleITK as sitk
import math
import numpy as np


# return the image, the point set filename
def readImageAndPoints(num):
    img = sitk.ReadImage("img_%02d.nii" % num)
    return img, ("pts_%02d.txt" % num)



#def createElastix(mov,fix,parameterMap):
#    selx = sitk.ElastixImageFilter()
#    selx.SetFixedImage(fix)
#    selx.SetMovingImage(mov)
#    selx.SetParameterMap(parameterMap)
#
#    return selx


def createElastixPointMetric(mov,movPtsFile,fix,fixPtsFile,parameterMap,pointWeight):
    "create an elastix object for registration with corresponding point metric"
    " parameterMap must already have 2 metric: first for intensity registration, second for regulariaation"
    " pointWeight is the weight of the point metric (1-pointWeight for the intensity registration)"
    selx = sitk.ElastixImageFilter()

    parameterMap["Metric0Weight"] = [str(1-pointWeight)]
    parameterMap["Metric2Weight"] = [str(pointWeight)]
    selx.SetParameterMap(parameterMap)

    selx.AddParameter( "Metric", "CorrespondingPointsEuclideanDistanceMetric" )

    selx.SetMovingImage(mov)
    selx.SetFixedImage(fix)

    selx.SetMovingPointSetFileName(movPtsFile)
    selx.SetFixedPointSetFileName(fixPtsFile)
    return selx



#def getBsplineCoeff(selx):
#    return np.array(selx.GetTransformParameterMap()[0]['TransformParameters'])
def getBsplineCoeff(tpm):
    return np.array([float(ci) for ci in tpm[0]['TransformParameters'] ])

def setBsplineCoeff(tpm,bsplCoeff):
    tpm[0]['TransformParameters'] = tuple([ str(ci) for ci in bsplCoeff])
    return tpm


def applyTransfo():
    transformix = sitk.TransformixImageFilter()
#    transformixImageFilter.ComputeDeformationFieldOn()

## registration parameters
#parameterMap = sitk.GetDefaultParameterMap('translation')
#parameterMap = sitk.GetDefaultParameterMap('affine')
#"spline"
#"bspline"
#"groupwise"

#parameterMap = sitk.GetDefaultParameterMap('affine')
#sitk.PrintParameterMap(parameterMap)
#
#
#parameterMap = sitk.GetDefaultParameterMap('bspline')
#sitk.PrintParameterMap(parameterMap)
#
#parameterMap["Metric"].append("CorrespondingPointsEuclideanDistanceMetric")
#
## The CorrespondingPointsEuclideanDistanceMetric metric must be specified 
## as the last metric due to technical constraints in elastix.
#
#
#
#parameterMap['NumberOfSpatialSamples'] = ['4096']
#parameterMap['MaximumNumberOfIterations'] = ['4096']
##resultImage = sitk.Elastix(fix, mov, parameterMap)
##sitk.Show(resultImage)
#
#

