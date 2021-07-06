from PIL import Image
from tesserocr import PyTessBaseAPI, PSM, OEM

with PyTessBaseAPI(psm=PSM.OSD_ONLY, oem=OEM.LSTM_ONLY) as api:
    api.SetImageFile("./testingsnips/test1.png")

    print("1")
    os = api.DetectOrientationScript()
    print("Orientation: {orient_deg}\nOrientation confidence: {orient_conf}\n"
          "Script: {script_name}\nScript confidence: {script_conf}".format(**os))

with PyTessBaseAPI(psm=PSM.OSD_ONLY, oem=OEM.LSTM_ONLY) as api:
    api.SetImageFile("./testingsnips/test3.png")

    print("3")
    os = api.DetectOrientationScript()
    print("Orientation: {orient_deg}\nOrientation confidence: {orient_conf}\n"
          "Script: {script_name}\nScript confidence: {script_conf}".format(**os))