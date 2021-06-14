import OCR_helper as OCR
from PIL import Image
from datetime import date


# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path

# Getting date for the report formatting
DATE = date.today().strftime("%d/%m/%Y")[:5]
        

def print_all_volumes():
    for i in range(3,8):
        images = convert_from_path("./bouldercopies/" + str(i) + "_Report_" + DATE[:2] + "_" + DATE[3:] + ".pdf", 500)    
        for image in images:
            OCR.print_from_image(image)

def print_one_volume(number):
    images = convert_from_path("./bouldercopies/" + str(number) + "_Report_" + DATE[:2] + "_" + DATE[3:] + ".pdf", 500)    
    for image in images:
        OCR.print_from_image(image)

