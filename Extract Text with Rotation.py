import cv2
import numpy as np
import pytesseract
import subprocess
import glob 
import os
import sys
import re
import PIL
from PIL import Image, ImageEnhance, ImageFilter, ImageSequence

# define file or image  such as a.tif or a.jpg
files = "c"
fl= files+'.tif' 

src_path = "/home/skaushik/iPERMS/" 

os.chdir(src_path+'/Image_split_output')

def get_rotation(filenames):
    tmp = subprocess.Popen(['tesseract', filenames, '-', '-psm', '0'],
                           stdout= subprocess.PIPE, stderr = subprocess.PIPE).communicate()[1]

    for i in tmp.split("\n"):
        if i.split(":")[0]== 'Orientation in degrees':
            return int(i.split(":")[1].strip())
        
def removePunctuation(opencv1_text):
    rmnewline = opencv1_text.replace('\n', ' ').replace('\r',' ').strip()
    nourl = re.sub(r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', '', rmnewline)
    nospc = re.sub(r'[^a-z0-9\s]',' ',nourl.lower())
    #print re.sub('[ \t]+',' ',nospc)
    return re.sub('[ \t]+',' ',nospc).encode('utf8')


def get_string(img_path, file_name):
    
    img = cv2.imread(img_path + file_name)

    #Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    #Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    #Apply threshold to get image with only black and white
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    # Write the image after apply opencv
    cv2.imwrite(src_path + files +"_image.jpg", img)

    #Recognize text with tesseract for python
    print(src_path +  files+"_image.jpg")
    
    img = Image.open(img_path + file_name)
    
    for i, page in enumerate(ImageSequence.Iterator(img)):
        page.save( file_name+ "page%d.jpg" % i)
    
    
        im = Image.open( file_name+ "page%d.jpg" % i)#(src_path + files +"_image.jpg")
        im = im.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(2)
        im = im.convert('1')
        im.save (file_name+ "page%d.jpg" % i+"_image.jpg")

        result= pytesseract.image_to_string(Image.open( file_name+ "page%d.jpg" % i+"_image.jpg").rotate(360-get_rotation(file_name+ "page%d.jpg" % i+"_image.jpg")))
        z= removePunctuation(result)
        print z
        
                                              
get_string(src_path , fl )