from kivy.lang import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.graphics import Point
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kiImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout



from PIL import Image as Im
from io import BytesIO
import numpy as np
import pickle
import cv2
from PIL import Image, ImageColor, ImageDraw, ImageEnhance

Builder.load_file("./kvScenes/verf.kv")

# on_press: root.manager.current = '_first_screen_'

class LandingScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
    pass 

class VerfScreen(Screen):
    rect_box = ObjectProperty(None)
    t_x = NumericProperty(0.0)
    t_y = NumericProperty(0.0)
    x1 = y1 = x2 = y2 = NumericProperty(0.0)
    array = []
    currenttext = StringProperty("Lets get started!")
    index = -1
    beeld = kiImage() # only use this line in first code instance

    def __init__(self, **kwargs):
        super(VerfScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def setup(self, path, page_num):
        
        if path.split('.').pop() != 'pickle' or not page_num.isnumeric():

            self.manager.current = 'landing'

            buttonText = ""
            
            if path.split('.').pop() != 'pickle':
                buttonText += 'Please select a pickle file returned from running controller.py!'

            if not page_num.isnumeric():
                buttonText += "\n\nPlease ensure you have supplied a number for the page start"


            # create content and add to the popup
            content = Button(text=buttonText)
            popup = Popup(title='Oops!', content=content, auto_dismiss=False, size_hint=(0.8, 0.5))

            # bind the on_press event of the button to the dismiss function
            content.bind(on_press=popup.dismiss)

            # open the popup
            popup.open()

        else:


            with open(path, 'rb') as f:
                self.word_data, self.boulder_data = pickle.load(f)

            # create content and add to the popup

            start_page_number = int(page_num)

            for i, boulder in self.boulder_data.iterrows():
                area = boulder['FullBB']

                wd_index = boulder['Page_Number']-start_page_number

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
                
                self.array.append((boulder, pageimg.crop(area),display_string))

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'e':
            print("Good")
            self.go_forward()
        elif keycode[1] == 'q':
            print("Bad") 
            self.go_back()
        return True
    
    def go_forward(self):
        if self.index < len(self.array) - 1:
            self.index += 1
        self.update()

    def go_back(self):
        if self.index > 0:
            self.index -= 1
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

    path = ""
    page_num = 0
    def build(self):
        
        self.MyScreenManager = ScreenManager()
        self.MyScreenManager.add_widget(LandingScreen(name='landing'))
        self.MyScreenManager.add_widget(VerfScreen(name='verf'))
        return self.MyScreenManager

    def start_verf(self):
        
        self.MyScreenManager.current = 'verf'
        print(self.page_num)
        self.MyScreenManager.get_screen('verf').setup(self.path,self.page_num)


if __name__ == '__main__':
    MyApp().run()