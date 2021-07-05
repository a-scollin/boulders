from types import TracebackType
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.graphics import Point
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ColorProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kiImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label



from PIL import Image as Im
from io import BytesIO
import numpy as np
import pickle
import cv2
from PIL import Image, ImageColor, ImageDraw, ImageEnhance
from numpy.lib.twodim_base import vander

Builder.load_file("./kvScenes/verf.kv")

# on_press: root.manager.current = '_first_screen_'

class LandingScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
    pass 

class VerfScreen(Screen):

    page_number = StringProperty("")

    current_location = StringProperty("")
    current_rocktype = StringProperty("")
    current_size = StringProperty("")
    verf = StringProperty("")
    verf_colour = ColorProperty('yellow')
    start_page_number = 0
    boulder_number = StringProperty("")
    rect_box = ObjectProperty(None)
    t_x = NumericProperty(0.0)
    t_y = NumericProperty(0.0)
    x1 = y1 = x2 = y2 = NumericProperty(0.0)
    array = []
    currenttext = StringProperty("Help ? \nKeyboard Bindings\n q = Go back\n w = Bad Boulder \n e = Good Boulder\n r = Go forward\np = Change Location\nGo forward to start verifying.")
    index = -1
    beeld = kiImage() # only use this line in first code instance

    def __init__(self, **kwargs):
        super(VerfScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def setup(self, path, page_num):
        
        if path.split('.').pop() != 'pickle' or not str(page_num).isnumeric():

            self.manager.current = 'landing'

            buttonText = ""
            
            if path.split('.').pop() != 'pickle':
                buttonText += 'Please select a pickle file returned from running controller.py!'

            print(page_num)
            if not str(page_num).isnumeric():
                buttonText += "\n\nPlease ensure you have supplied a number for the page start"


            # create content and add to the popup
            content = Button(text=buttonText)
            popup = Popup(title='Oops!', content=content, auto_dismiss=False, size_hint=(0.8, 0.5))

            # bind the on_press event of the button to the dismiss function
            content.bind(on_press=popup.dismiss)

            # open the popup
            popup.open()

            return False

        else:


            with open(path, 'rb') as f:
                self.word_data, self.boulder_data = pickle.load(f)

            # create content and add to the popup
            self.start_page_number = int(page_num)

            for i, boulder in self.boulder_data.iterrows():
                area = boulder['FullBB']

                wd_index = boulder['Page_Number']-self.start_page_number
                
                pageimg = self.word_data[wd_index][1]
                
                if len(boulder['LBB']):
                    for box in boulder['LBB']:
                        pageimg = self.highlight_area(pageimg, box, 1.5, outline_color=ImageColor.getrgb('green'), outline_width=5)

                if len(boulder['SBB']):
                    for box in boulder['SBB']:
                        pageimg = self.highlight_area(pageimg, box, 1.5, outline_color=ImageColor.getrgb('red'), outline_width=5)

                if len(boulder['RBB']):
                    for box in boulder['RBB']:
                        pageimg = self.highlight_area(pageimg, box, 1.5, outline_color=ImageColor.getrgb('blue'), outline_width=5)

                display_string = ""
                for k, word in self.word_data[wd_index][0].loc[self.word_data[wd_index][0]['par_num'] == boulder['par_num']].iterrows():
                    display_string += word['text'] + " "
                
                self.array.append((boulder, pageimg.crop(area),display_string, "NOT VERIFIED"))

                theimage = Im.open("./testingsnips/boulder.jpg")
                data = BytesIO()
                theimage.save(data, format='png')            
                data.seek(0) # yes you actually need this
                im = CoreImage(BytesIO(data.read()), ext='png')
                self.beeld.texture = im.texture

        return True
    def _keyboard_closed(self):
        
        return

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'r':
            self.go_forward()
        if keycode[1] == 'w':
            self.bad_boulder(True)
        if keycode[1] == 'e':
            self.good_boulder(True)
        if keycode[1] == 'p':
            self.update_location()
        elif keycode[1] == 'q':
            self.go_back()
        return True
    
    def go_forward(self):
        if self.index < len(self.array) - 1:
            self.index += 1
        self.update()

    def update_location(self):

        
        if not self.array[self.index][0]['Location']:
            return     
        else:

            box = BoxLayout(orientation="vertical")
            loca = TextInput(text=self.array[self.index][0]['Location'])
            box.add_widget(loca)

            sub_but = Button(text="Submit Changes")
            dis_but = Button(text="Dismiss")

            box.add_widget(sub_but)
            box.add_widget(dis_but)

            popup = Popup(title='Location', content=box, auto_dismiss=False, size_hint=(0.8, 0.5))

            location = loca.text
            sub_but.bind(on_press = lambda location, popup: self.submit_location(location, popup))
            dis_but.bind(on_press=popup.dismiss)            

            # open the popup
            popup.open()        

    def submit_location(self,loc, popup):
        

        print(loc)
        popup.dismiss()

    def go_back(self):
        if self.index > 0:
            self.index -= 1
        self.update()

    def bad_boulder(self, move):
        if self.index >= 0:
            self.verf = "INCORRECT"
            tmp = list(self.array[self.index])
            tmp[3] = self.verf
            self.array[self.index] = tuple(tmp)
        if move:
            self.index += 1

        self.update()

    def good_boulder(self,move):
        if self.index >= 0:
            self.verf = "CORRECT"
            tmp = list(self.array[self.index])
            tmp[3] = self.verf
            self.array[self.index] = tuple(tmp)
            
        if move:
            self.index += 1
        self.update()

    def update(self):
        
        if self.index != -1:

            theimage = self.array[self.index][1]
            data = BytesIO()
            theimage.save(data, format='png')            
            data.seek(0) # yes you actually need this
            im = CoreImage(BytesIO(data.read()), ext='png')
            self.currenttext = self.array[self.index][2]
            self.beeld.texture = im.texture
            self.boulder_number = "Boulder Number : " + str(self.index)
            self.page_number = "Page Number : " + str(self.array[self.index][0]['Page_Number'])
            self.current_location = "Location : " + str(self.array[self.index][0]['Location'])
            self.current_rocktype = "Rocktype : " + str(self.array[self.index][0]['Rocktype'])
            self.current_size = "Size : " + str(self.array[self.index][0]['Size'])
            self.verf = self.array[self.index][3]

            if self.verf == "NOT VERIFIED":
                self.verf_colour = "yellow"

            if self.verf == "CORRECT":
                self.verf_colour = "green"
            
            if self.verf == "INCORRECT":
                self.verf_colour = "red"
            
    
        return True

    


    def highlight_area(self, img, region, factor, outline_color=None, outline_width=1):
      
        img = img.copy()  # Avoid changing original image.
        img_crop = img.crop(region)

        brightner = ImageEnhance.Brightness(img_crop)
        img_crop = brightner.enhance(factor)

        img.paste(img_crop, region)

        if outline_color:
            draw = ImageDraw.Draw(img)  # Create a drawing context.
            left, upper, right, lower = region  # Get bounds.
            coords = [(left, upper), (right, upper), (right, lower), (left, lower),
                    (left, upper)]
            draw.line(coords, fill=outline_color, width=outline_width)

        return img

class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MyApp(App):

    path = "beans"
    page_num = 0
    def build(self):
        self.title = "Boulder Verification App"
        self.MyScreenManager = ScreenManager()
        self.MyScreenManager.add_widget(LandingScreen(name='landing'))
        self.MyScreenManager.add_widget(VerfScreen(name='verf'))
        return self.MyScreenManager

    def start_verf(self):
        
        if self.MyScreenManager.get_screen('verf').setup(self.path,self.page_num):
            self.MyScreenManager.current = 'verf'


if __name__ == '__main__':
    MyApp().run()