from kivy.lang import Builder
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ColorProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kiImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
import pandas as pd
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')


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


    path = "Beans"
    page_number = StringProperty("")
    focused = False
    setup_done = False
    current_location = StringProperty("")
    current_rocktype = StringProperty("")
    current_size = StringProperty("")
    current_bnum = StringProperty("")
    current_aut = StringProperty("")
    current_ext = StringProperty("")
    current_volume = StringProperty("")
    current_weight = StringProperty("")
    current_hasl = StringProperty("")
    current_compass = StringProperty("")
    current_distance = StringProperty("")
    current_par_num = StringProperty("")
    
    verf = StringProperty("")
    verf_colour = ColorProperty('yellow')

   

    
    start_page_number = 0
    boulder_number = StringProperty("")
    rect_box = ObjectProperty(None)
    t_x = NumericProperty(0.0)
    t_y = NumericProperty(0.0)
    x1 = y1 = x2 = y2 = NumericProperty(0.0)
    array = []
    currenttext = StringProperty("Help ? \nKeyboard Bindings\nq = Go back\nw = Bad Boulder\ne = Good Boulder\nr = Go forward\nt = Location\ny = Rocktype\nu = Size\ni = Number of Boulders (BNum)\no = Extra\np = Author\ng = Volume\nh = Weight\nj = Height above sea level (HASL)\nk = Compass\nl = Distance\nf = SET FULL PAGE VIEW.\n##################\nGo forward to start verifying.")
    index = -1
    beeld = kiImage() # only use this line in first code instance

    def __init__(self, **kwargs):
        super(VerfScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def save_progress(self):
        
        
        save_array = []

        for boulder in self.array:
            if boulder[3] != 'DROPPED':
                save_array.append(boulder)

            
        with open(self.path, 'wb') as f:
            pickle.dump((self.word_data,save_array,self.start_page_number,self.report_number,True), f)

        self.array = save_array 
        self.index = 0

        self.update()


        # create content and add to the popup
        box = BoxLayout()
        b1 = Button(text="Export to a pdf")
        box.add_widget(b1)
        b2 = Button(text="Export to csv")
        box.add_widget(b2)
        b3 = Button(text="Export to pdf and csv")
        box.add_widget(b3)
        b4 = Button(text="Dismiss")
        box.add_widget(b4)

        popup = Popup(title='Save and Export', content=box, auto_dismiss=False, size_hint=(0.8, 0.5))

        # bind the on_press event of the button to the dismiss function
        b1.bind(on_press=self.export_pdf)
        b1.bind(on_press=popup.dismiss)
        
        b2.bind(on_press=self.export_csv)
        b2.bind(on_press=popup.dismiss)
        
        b3.bind(on_press=self.export_pdf)
        b3.bind(on_press=self.export_csv)
        b3.bind(on_press=popup.dismiss)
        
        b4.bind(on_press=popup.dismiss)

        # open the popup
        popup.open()

    def export_csv(self,e):
        
        
        d = {'Numbers' : [], 'Location': [], 'Size' : [], 'Volume': [], 'Weight': [], 'HASL': [], 'Compass': [], 'Distance': [], 'Rocktype' : [], 'Extra' : [], 'BNum' : [], 'Author' : [], 'Verified' : [], 'Page_Number' : [], 'par_num': []}


        for boulder in self.array:
            d['Numbers'].append(boulder[0]['Numbers'])
            d['Location'].append(boulder[0]['Location'])
            d['Size'].append(boulder[0]['Size'])
            d['Rocktype'].append(boulder[0]['Rocktype'])            
            d['Page_Number'].append(boulder[0]['Page_Number'])
            d['BNum'].append(boulder[0]['BNum'])
            d['Extra'].append(boulder[0]['Extra'])
            d['Author'].append(boulder[0]['Author'])
            d['Volume'].append(boulder[0]['Volume'])
            d['Weight'].append(boulder[0]['Weight'])
            d['HASL'].append(boulder[0]['HASL'])
            d['Compass'].append(boulder[0]['Compass'])
            d['Distance'].append(boulder[0]['Distance'])
            d['par_num'].append(boulder[0]['par_num'])
            d['Verified'].append(boulder[3])


        

        df = pd.DataFrame(data=d)

        df.to_csv(self.path+".csv")
        

    def export_pdf(self,e):
        index = 0

        pages = []

        for page in self.word_data:
            
            pageimg = page[1]
            boxes = []

            for element in [item for item in self.array if item[4] == index+self.start_page_number]:
                
                boulder = element[0]
                
                print(element)

                if element[3] == 'CORRECT':
                    highlight_colour = 'green'
                    highlight_amount = 0.8
                elif element[3] == 'INCORRECT':
                    highlight_colour = 'red'
                    highlight_amount = 1 
                elif element[3] == 'NOT VERIFIED':
                    highlight_colour = 'yellow'
                    highlight_amount = 1
                
        
                x,y,x_w,y_h = boulder['FullBB']

                y += 100
                x += 100
                y_h -= 100
                x_w -= 100

                box = (x,y,x_w,y_h)

                if box not in boxes:

                    pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb(highlight_colour), outline_width=5)
                    boxes.append(box)

                if len(boulder['LBB']):
                    for box in boulder['LBB']:
                        pageimg = self.highlight_area(pageimg, box, 1, outline_color=ImageColor.getrgb('green'), outline_width=5)

                if len(boulder['SBB']):
                    for box in boulder['SBB']:
                        pageimg = self.highlight_area(pageimg, box, 1, outline_color=ImageColor.getrgb('red'), outline_width=5)

                if len(boulder['RBB']):
                    for box in boulder['RBB']:
                        pageimg = self.highlight_area(pageimg, box, 1, outline_color=ImageColor.getrgb('blue'), outline_width=5)

                if len(boulder['ABB']):
                    for box in boulder['ABB']:
                        pageimg = self.highlight_area(pageimg, box, 1, outline_color=ImageColor.getrgb('orange'), outline_width=5)
                
                if len(boulder['EBB']):
                    for box in boulder['EBB']:
                        pageimg = self.highlight_area(pageimg, box, 1, outline_color=ImageColor.getrgb('honeydew'), outline_width=5)

                if len(boulder['CBB']):
                    for box in boulder['CBB']:
                        pageimg = self.highlight_area(pageimg, box, 1, outline_color=ImageColor.getrgb('darkgreen'), outline_width=5)
                
                if len(boulder['BBB']):
                    pageimg = self.highlight_area(pageimg, boulder['BBB'], 1, outline_color=ImageColor.getrgb('plum'), outline_width=5)

            pages.append(pageimg)

            index += 1 

        pages[0].save(self.path+".pdf", save_all=True, append_images=pages[1:])

    def setup(self, path):
        
        if path.split('.').pop() != 'pickle':

            self.manager.current = 'landing'

            buttonText = ""
            
            if path.split('.').pop() != 'pickle':
                buttonText += 'Please select a pickle file returned from running controller.py!'


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
                loaded_data = pickle.load(f)


            if len(loaded_data) == 4:

                self.word_data, boulder_data, self.start_page_number, self.report_number = loaded_data

                for i, boulder in boulder_data.iterrows():
                    area = boulder['FullBB']

                    area = (area[0]-50,area[1]-50,area[2]+50,area[3]+50)

                    wd_index = boulder['Page_Number']-self.start_page_number
                    
                    pageimg = self.word_data[wd_index][1]

                    highlight_amount = 0.95
                
                    pageimg = self.highlight_area(pageimg, boulder['BBB'], highlight_amount, outline_color=ImageColor.getrgb('cyan'), outline_width=5)
                    
                    if len(boulder['LBB']):
                        for box in boulder['LBB']:
                            pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb('green'), outline_width=5)

                    if len(boulder['SBB']):
                        for box in boulder['SBB']:
                            pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb('red'), outline_width=5)

                    if len(boulder['RBB']):
                        for box in boulder['RBB']:
                            pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb('blue'), outline_width=5)

                    if len(boulder['ABB']):
                        for box in boulder['ABB']:
                            pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb('yellow'), outline_width=5)

                    if len(boulder['EBB']):
                        for box in boulder['EBB']:
                            pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb('blue'), outline_width=5)
                        
                    if len(boulder['CBB']):
                        for box in boulder['CBB']:
                            pageimg = self.highlight_area(pageimg, box, highlight_amount, outline_color=ImageColor.getrgb('orange'), outline_width=5)

                    display_string = ""
                    for k, word in self.word_data[wd_index][0].loc[self.word_data[wd_index][0]['par_num'] == boulder['par_num']].iterrows():
                        display_string += word['text'] + " "
                    
                    self.array.append((boulder, pageimg.crop(area),display_string, "NOT VERIFIED",boulder['Page_Number']))
            
            elif len(loaded_data) == 5:
            
                self.word_data, self.array, self.start_page_number, self.report_number, preloaded = loaded_data

            else:
                print(loaded_data)
                raise("Wrong format of pickle file..")


            theimage = Im.open("./testingsnips/boulder.jpg")
            data = BytesIO()
            theimage.save(data, format='png')            
            data.seek(0) # yes you actually need this
            im = CoreImage(BytesIO(data.read()), ext='png')
            self.beeld.texture = im.texture

        self.setup_done = True
        self.path = path
        return True
    def _keyboard_closed(self):
        
        return

    def _on_keyboard_up(self, keyboard, keycode):

        if not self.setup_done:
            return False

        if self.focused:
            if keycode[1] == 'enter' and self.sub_but:
                self.submit_attribute(self.sub_but)
                self.popup.dismiss()
            if keycode[1] == 'escape' and self.popup:
                self.togglefocus(0)
                self.popup.dismiss()
                return True
            return False

        if keycode[1] == 'r':
            self.go_forward()
        if keycode[1] == 'w':
            self.bad_boulder(True)
        if keycode[1] == 'e':
            self.good_boulder(True)
        if keycode[1] == 'd':
            self.drop_boulder(False)
        if keycode[1] == 't':
            self.update_attribute('Location')
        if keycode[1] == 'y':
            self.update_attribute('Rocktype')
        if keycode[1] == 'u':
            self.update_attribute('Size')
        if keycode[1] == 'i':
            self.update_attribute('BNum')
        if keycode[1] == 'o':
            self.update_attribute('Extra')
        if keycode[1] == 'p':
            self.update_attribute('Author')
        if keycode[1] == 'g':
            self.update_attribute('Volume')
        if keycode[1] == 'h':
            self.update_attribute('Weight')
        if keycode[1] == 'j':
            self.update_attribute('HASL')
        if keycode[1] == 'k':
            self.update_attribute('Compass')
        if keycode[1] == 'l':
            self.update_attribute('Distance')
        if keycode[1] == 'f':
            self.set_full()
        
        elif keycode[1] == 'q':
            self.go_back()
        return True
    
    def go_forward(self):
        if self.index < len(self.array) - 1:
            self.index += 1
        self.update()

    def togglefocus(self,e):
        self.focused = True if not self.focused else False 
    
    def update_attribute(self, attribute):

        if not self.array[self.index][0][attribute]:
            self.array[self.index][0][attribute] = ''
            
        self.togglefocus(0)
        box = BoxLayout(orientation="vertical")
        self.loca = TextInput(text=str(self.array[self.index][0][attribute]),multiline=False)
        box.add_widget(self.loca)
        self.sub_but = Button(text="Submit Changes - " + attribute)
        dis_but = Button(text="Dismiss")
        box.add_widget(self.sub_but)
        box.add_widget(dis_but)
        self.popup = Popup(title=attribute, content=box, auto_dismiss=False, size_hint=(0.8, 0.5))
        self.sub_but.bind(on_press = self.submit_attribute)
        self.sub_but.bind(on_press = self.popup.dismiss)
        dis_but.bind(on_press=self.togglefocus)
        dis_but.bind(on_press=self.popup.dismiss)  
        # open the popup
        self.popup.open()      
        self.loca.focus = True  


    def submit_attribute(self, button):
        if button:
            self.togglefocus(0)
            location = self.loca.text
            
            tmp = list(self.array[self.index])
            boulder = tmp[0]
            boulder[button.text.split('-')[1].strip()] = location
            tmp[0] = boulder
            self.array[self.index] = tuple(tmp)
        
            self.update()

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

    def drop_boulder(self,move):
        if self.index >= 0:
            self.verf = "DROPPED"
            tmp = list(self.array[self.index])
            tmp[3] = self.verf
            self.array[self.index] = tuple(tmp)
            
        if move:
            self.index += 1
        self.update()

    def update(self):
        
        if self.index != -1:
            self.focused = False
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
            self.current_bnum = "Number of Boulders : " + str(self.array[self.index][0]['BNum'])
            self.current_ext = "Extra : " + str(self.array[self.index][0]['Extra'])
            self.current_aut = "Author : " + str(self.array[self.index][0]['Author'])
            self.current_size = "Size : " + str(self.array[self.index][0]['Size'])
            self.verf = self.array[self.index][3]

            self.current_volume = "Volume : " + str(self.array[self.index][0]['Volume'])
            self.current_weight = "Weight : " + str(self.array[self.index][0]['Weight'])
            self.current_hasl = "HASL : " + str(self.array[self.index][0]['HASL'])
            self.current_compass = "Compass : " + str(self.array[self.index][0]['Compass'])
            self.current_distance = "Distance : " + str(self.array[self.index][0]['Distance'])
            self.current_par_num = "Paragraph :" + str(self.array[self.index][0]['par_num'])

            if self.verf == "NOT VERIFIED":
                self.verf_colour = "yellow"

            if self.verf == "CORRECT":
                self.verf_colour = "green"
            
            if self.verf == "INCORRECT":
                self.verf_colour = "red"

            if self.verf == "DROPPED":
                self.verf_colour = "orange"
            
    
        return True

    def set_full(self):

        if self.index != -1:
            boulder = self.array[self.index][0]
            wd_index = boulder['Page_Number']-self.start_page_number    
            theimage = self.word_data[wd_index][1]
            theimage = self.highlight_area(theimage,boulder['FullBB'],1, outline_color=ImageColor.getrgb('black'), outline_width=5)
            data = BytesIO()
            theimage.save(data, format='png')            
            data.seek(0) # yes you actually need this
            im = CoreImage(BytesIO(data.read()), ext='png')
            self.beeld.texture = im.texture


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
    def build(self):
        self.title = "Boulder Verification App"
        self.MyScreenManager = ScreenManager()
        self.MyScreenManager.add_widget(LandingScreen(name='landing'))
        self.MyScreenManager.add_widget(VerfScreen(name='verf'))
        return self.MyScreenManager

    def start_verf(self):
        
        if self.MyScreenManager.get_screen('verf').setup(self.path):
            self.MyScreenManager.current = 'verf'


if __name__ == '__main__':
    MyApp().run()