from functools import total_ordering
import json
import pickle
import re
import sys
from os import name

import numpy as np
from numpy.core.fromnumeric import size
from numpy.lib.utils import byte_bounds
import pandas as pd
# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path
from PIL import Image
import cv2



# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
from scipy.ndimage import interpolation as inter
import numpy as np


pil_image = Image.open('./testingsnips/Testing.png').convert('RGB') 


text = pytesseract.image_to_data(pil_image, output_type='data.frame', config='--oem 2')


open_cv_image = np.array(pil_image) 
# Convert RGB to BGR 
open_cv_image = open_cv_image[:, :, ::-1].copy() 

teswords = text[text.conf != -1]


cv2.imshow("Tesseract", open_cv_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.waitKey(1)