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
from PIL import Image as Im
from io import BytesIO



Builder.load_string("""

<MyScreenManager>:
    ThirdScreen:
        id: third_screen

<ThirdScreen>:
    name: '_third_screen_'
    id: third_screen
    BoxLayout:
        orientation: "vertical"
        id: third_screen_boxlayout
        Label:
            id: main_title
            text: "Title"
            size_hint: (1, 0.1)
        BoxLayout:
            id: image_box_layout
            Image:
                id: main_image
                texture: root.beeld.texture
        
            Label:
                id: Sentence
                text: root.currenttext
        BoxLayout:
            id: button_boxlayout
            orientation: "horizontal"
            padding: 10
            size_hint: (1, 0.15)
            Button:
                id: accept_button
                text: "<"
                size_hint: (0.33, 1)
                on_press: root.go_back()
            Button:
                id: crop_button
                text: "Undo"
                size_hint: (0.33, 1)
                on_press: root.undo()
            Button:
                id: cancel_button
                text: ">"
                size_hint: (0.33, 1) 
                on_press: root.go_forward()
""")

# on_press: root.manager.current = '_first_screen_'

class MyScreenManager(ScreenManager):
    pass

class ThirdScreen(Screen):
    rect_box = ObjectProperty(None)
    t_x = NumericProperty(0.0)
    t_y = NumericProperty(0.0)
    x1 = y1 = x2 = y2 = NumericProperty(0.0)
    array = [("Sentence this is a sentece.","./testingsnips/rep3test1.png"),("Sentence is this a sentece?","./testingsnips/rep3test2.png"),("Sentence this is sooonntance.","./testingsnips/rep3test3.png")]
    currenttext = StringProperty("Lets get started!")
    index = -1
    def __init__(self, **kwargs):
        super(ThirdScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.beeld = kiImage() # only use this line in first code instance


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
        
        theimage = Im.open("./testingsnips/rep3test1.png")
        data = BytesIO()
        theimage.save(data, format='png')
        data.seek(0) # yes you actually need this
        im = CoreImage(BytesIO(data.read()), ext='png')
        
        
        self.currenttext = self.array[self.index][0]
        self.beeld.texture = im.texture

        print(self.index)
        print(self.currenttext)
        
        return True

class MyApp(App):
    def build(self):
        return MyScreenManager()

if __name__ == '__main__':
    MyApp().run()