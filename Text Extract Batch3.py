import pytesseract
import subprocess
import os
import sys
import re
import traceback
import shutil
from PIL import Image, ImageEnhance, ImageFilter, ImageSequence
   

## Get an Image files from a directory
def getImageFiles(target_dir):
    #print target_dir
    result_list = []
    for files in os.listdir(target_dir):
        if re.search("(.jpg|.png|.tif|.jpeg)$", files):
        
            result_list.append(os.path.join(target_dir,files))
        
    
    return result_list


## Rotate an image 
def getRotation(filenames):
    tmp = subprocess.Popen(['tesseract', filenames, '-', '-psm', '0'],stdout= subprocess.PIPE, stderr = subprocess.PIPE).communicate()[1]
    
    for i in tmp.split("\n"):
        if i.split(":")[0] == 'Orientation in degrees':
            return int(i.split(":")[1].strip())
    return 0
       
## split an images with more than one page        
def splitFiles(filenames_list, target_dir):
    
    first_regex = re.compile("(\w|-)*(.jpg|.png|.tif|.jpeg)$")
    second_regex = re.compile("(\w|-)*(?=(.jpg|.png|.tif|.jpeg)$)")
    third_regex = re.compile("(.jpg|.png|.tif|.jpeg)$")
    for files in filenames_list:
        img = Image.open(files)
        
        for i, page in enumerate(ImageSequence.Iterator(img)):
          
            page.save(first_regex.sub('',files) + "Image_split_output/" + 
                      second_regex.search(files).group(0)+
                      "_page%d%s"%(i, third_regex.search(files).group(0)))
          
            
## create a directory to save the images            
def createImageSplitDirectory(target_dir):
    if os.path.isdir(target_dir+"/Image_split_output") is False:
        os.mkdir(target_dir+"/Image_split_output")

        
def write_result(source_dir, file_full_name, data):
    file_name = re.match("(\w|-)*(?=(_page))", file_full_name).group(0)
    with open(source_dir+"/"+file_name+".txt", 'w+') as result_file:
        result_file.write(data)
        
        
    
## extract a text from images   
def startProcessing(target_dir, source_dir):    
        
    for files in os.listdir(target_dir+"/Image_split_output"):
          
        im = Image.open(target_dir+"/Image_split_output/"+files)
    
        im = im.filter(ImageFilter.MedianFilter())
       # enhancer = ImageEnhance.Contrast(im)
       # im = enhancer.enhance(2)
       # im = im.convert('1')
        result= pytesseract.image_to_string(im.rotate(360-getRotation(target_dir+"/Image_split_output/"+files)))

            
        if result== '':
            
            result = "No Text in this Image"
        
        z= removePunctuation(result)
        write_result(source_dir, files, z) 


## cleaning the extracted content     
def removePunctuation(opencv1_text):
    rmnewline = opencv1_text.replace('\n', ' ').replace('\r',' ').strip()
    nourl = re.sub(r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', '', rmnewline)
    nospc = re.sub(r'[^a-z0-9\s]',' ',nourl.lower())
    return re.sub('[ \t]+',' ',nospc).encode('utf8')

            
def main(target_dir, source_dir):
    try:
        files_list = getImageFiles(target_dir)
    
    except IOError as exp:
        print "----Exeption Occured While Reading Files From Target Directory----"
        print "Exception NO:",exp.errno
        print "Exceprtion Message:",exp.message
        
        
    
    if len(files_list) == 0:
        print "----There are no files in Target Directory---"
        sys.exit(0)
    
    
    createImageSplitDirectory(target_dir)
    
    
    try:
        splitFiles(files_list, target_dir)
    
    except IOError as exp:
        print "----Exeption Occured While Writing Files Into Image_Split_Dir----"
        print "Exception NO:",exp.errno
        print "Exceprtion Message:",exp.message
        
    startProcessing(target_dir, source_dir)
    shutil.rmtree(target_dir+"/Image_split_output")
       

if __name__ == "__main__":
    try:
        #main("/home/skaushik/iPERMS/DEMO/Forms_Image/","/home/skaushik/iPERMS/DEMO/Text_Files/" )
        ## main( "path for the image folder", "path a target folder" )
        main("/home/skaushik/Image","/home/skaushik/text_extract/" )
        
        
        
    except:
        print '------------Exception in main block---------------' 
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print  '\n'.join('!! ' + line for line in lines)

