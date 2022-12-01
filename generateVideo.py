import cv2
import numpy as np
import glob

# generate videos to better visualize the registration between the images
for path in ['morph', 'morphSym', 'morphEveryone']:
    out = cv2.VideoWriter('output' + path + '.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, (140, 209))
    for filename in glob.glob(r'' + path + '/*.png'):
        img = cv2.imread(filename)
        out.write(img)
    out.release()
