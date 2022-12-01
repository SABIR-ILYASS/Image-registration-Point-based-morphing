
# export SITK_SHOW_COMMAND=fslview

# help(toto) -> aide de toute les fonction de toto

import SimpleITK as sitk
import math

import tpmod as tp

import sys

import argparse


def svg2dimage(img, rootname):
    ''' save 2d image as nii and png '''
    sitk.WriteImage(img,                                                       rootname+".nii")
    sitk.WriteImage(sitk.Cast( sitk.Flip(img, [False, True]), sitk.sitkUInt8), rootname+'.png')
    


def mapImage(movNum,fixNum,nodeSpacing):

    print ("mapImage")

    # load images and point files
    image_fix, path_points_fix = tp.readImageAndPoints(fixNum)
    image_mov, path_points_mov = tp.readImageAndPoints(movNum)
    
    # create the bspline parameter map and set node spacing, max iter
    pm = sitk.GetDefaultParameterMap('bspline', finalGridSpacingInPhysicalUnits = nodeSpacing)
    pm['NumberOfSpatialSamples'] = ['256']
    pm['MaximumNumberOfIterations'] = ['256']
    
    # create elastix object for point registration
    pointWeight = 1
    selx = tp.createElastixPointMetric(image_mov, path_points_mov, image_fix, path_points_fix, pm, pointWeight)

    # run the registration
    selx.Execute()

    # get the transformation map and map the moving image in the fixed reference 
    tpm = selx.GetTransformParameterMap()
    res = selx.GetResultImage()
    res.CopyInformation(image_fix)

    return tpm, res



def morph(odir,movNum,fixNum,nodeSpacing,N):

    print ("morph")
    # read the moving image 
    # registration using mapImage 
    image_mov, _ = tp.readImageAndPoints(movNum)

    tpm, res = mapImage(movNum, fixNum, nodeSpacing)

    # get the bspline coefficient
    BsplineCoeff = tp.getBsplineCoeff(tpm)


    # for each "time" sample
    # compute the modified bspline coeff, the modified tpm
    # the intermediate image

    # transformix = sitk.TransformixImageFilter()
    img = []
    for k in range(0, N):
        alpha = k / (N - 1)
        
        new_BsplineCoeff = alpha * BsplineCoeff
        new_tpm = tp.setBsplineCoeff(tpm, new_BsplineCoeff)

        transformix = sitk.TransformixImageFilter()
        transformix.SetTransformParameterMap(new_tpm)
        transformix.SetMovingImage(image_mov)
        transformix.Execute()

        mov = transformix.GetResultImage()
        img.append(mov)
        # svg2dimage(img[k],"%s/img_%02d_%02d_%03d"     % (odir,movNum,fixNum,k))

    return img


def morphSym(odir,i,j,nodeSpacing,N):

    print ("morphSym")

    # we apply the function morph to the images of index i and j in the both directions
    image_i_j = morph(odir, i, j, nodeSpacing, N)
    image_j_i = morph(odir, j, i, nodeSpacing, N)

    img = []
    for k in range(0,N):
        alpha = k / (N - 1)
        im_inter = (1 - alpha) * image_i_j[k] + alpha * image_j_i[N - 1 - k]
        img.append(im_inter)
        svg2dimage(     img[k],"%s/img_%02d_%02d_%03d"     % (odir,i,j,k))

    return img

def morphEveryone(odir,nodeSpacing,N):

    print ("morphEveryone")
    # apply the morphing between image and the next 
    img = []
    for i in range(0,9): 
      img = img + morphSym(odir,i,i + 1,nodeSpacing,N)
       
    return img


if __name__ == '__main__':
    ##################################################################################
    ##################################################################################
    # parse command line 
    parser = argparse.ArgumentParser()

    parser.add_argument("-N",   dest='N',            default='20', help="number of samples")
    parser.add_argument("-ns",  dest='nodeSpacing',  default='6',  help="node spacing")

    parser.add_argument("exNum", help="which exercice")
    parser.add_argument("exArgs", help="argument for the given exercice",nargs='*')

    args = parser.parse_args()

    N           = int(args.N)
    nodeSpacing = int(args.nodeSpacing)

    exNum  = args.exNum
    exArgs = args.exArgs


    ##################################################################################
    ##################################################################################
    # registration and map for a given node spacing
    if exNum=="ex1":
        if len(exArgs)!=2:
            print( "exercice 1: tpnote movNum fixNum")
            sys.exit(1)
        movNum, fixNum = [int(a) for a in exArgs]
        tpm,img = mapImage(movNum,fixNum,nodeSpacing)
        svg2dimage(img,"ex1")
        
        print ("fslview -m single img_%02d ex1" % fixNum )
        print ("fsleyes -xh -yh img_%02d ex1" % fixNum )
        sys.exit(0)

    ##################################################################################
    ##################################################################################
    # morphing, non symmetric
    if exNum=="ex2":
        if len(exArgs)!=2:
            print( "exercice 2: tpnote movNum fixNum")
            sys.exit(1)
        movNum, fixNum = [int(a) for a in exArgs]
        imglist = morph("morph",movNum,fixNum,nodeSpacing,N)
        img3D   = sitk.JoinSeries(imglist)
        sitk.WriteImage(img3D, "ex2.nii")
        print ("fslview -m single img_%02d morph/img_%02d_%02d_???.nii img_%02d" % (fixNum,movNum,fixNum,movNum ) )
        print ("fslview -m single ex2.nii" )
        print ("fsleyes -xh -yh img_%02d morph/img_%02d_%02d_???.nii img_%02d" % (fixNum,movNum,fixNum,movNum ) )
        print ("fsleyes -xh -yh ex2.nii" )
        print ("display img_%02d.jpg morph/img_%02d_%02d_???.png img_%02d.jpg" % (fixNum,movNum,fixNum,movNum ) )
        sys.exit(0)

    ##################################################################################
    ##################################################################################
    # morphing symmetric
    if exNum=="ex3":
        if len(exArgs)!=2:
            print ("exercice 3: tpnote movNum fixNum")
            sys.exit(1)
        movNum, fixNum = [int(a) for a in exArgs]
        imglist = morphSym("morphSym",movNum,fixNum,nodeSpacing,N)
        img3D   = sitk.JoinSeries(imglist)
        sitk.WriteImage(img3D, "ex3.nii")
        print ("fslview -m single img_%02d morphSym/img_%02d_%02d_???.nii img_%02d" % (fixNum,movNum,fixNum,movNum ) )
        print ("fslview -m single ex3.nii" )
        print ("fsleyes -xh -yh img_%02d morphSym/img_%02d_%02d_???.nii img_%02d" % (fixNum,movNum,fixNum,movNum ) )
        print ("fsleyes -xh -yh ex3.nii" )
        print ("display img_%02d.jpg morphSym/img_%02d_%02d_???.png img_%02d.jpg" % (fixNum,movNum,fixNum,movNum ) )
        sys.exit(0)

    ##################################################################################
    ##################################################################################
    # morphing everyone
    if exNum=="ex4":
        if len(exArgs)!=0:
            print ("exercice 4: tpnote ex4 ")
            sys.exit(1)
        imglist = morphEveryone("morphEveryone",nodeSpacing,N)
        img3D   = sitk.JoinSeries(imglist)
        sitk.WriteImage(img3D, "ex4.nii")
#        print ("fslview -m single img_%02d morphSym/img_%02d_%02d_???.nii img_%02d" % (fixNum,movNum,fixNum,movNum ) )
        print ("fslview -m single ex4.nii" )
        print ("fsleyes -xh -yh ex4.nii" )
        displaycmd="display " 
        for i in range(0,9): 
           displaycmd += "morphEveryone/img_%02d_%02d_???.png " % (i+1, i)
        print (displaycmd)
       
        sys.exit(0)

    ##################################################################################
    ##################################################################################
    print ("unknown exercice " + args.exNum )
    


    