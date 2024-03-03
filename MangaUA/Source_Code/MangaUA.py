from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
import main

class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super(CenteredTextInput, self).__init__(**kwargs)
        self.multiline = False  # Заборонити багатостроковий режим
        self.text_validate_unfocus = False  # Не скидати фокус після введення тексту
        self.padding_y = [self.height / 3.5 - (self.line_height / 3.5), 0]  # Зсув по вертикалі для центрування тексту

class Container(FloatLayout):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        self.image = Image(source="Back.png")
        self.name_input = CenteredTextInput(hint_text='Manga Name', size_hint=(None, None), size=(544, 88), pos_hint={"center_x": 0.5, "top": 0.9}, background_color="#EBCBCB", font_size=36, halign='center')
        self.fron = Label(text="From", font_size = 36, pos_hint={"center_x": 0.19, "center_y": 0.5})
        self.select_page_input = CenteredTextInput(hint_text='Start', size_hint=(None, None), size=(90, 46), pos_hint={"x": 0.27, "center_y": 0.5}, background_color="#EBCBCB", halign='center')
        self.to = Label(text="to", font_size = 36, size=(87, 44), pos_hint={"center_x": 0.44, "center_y": 0.5})
        self.end_page_input = CenteredTextInput(hint_text='End', size_hint=(None, None), size=(90, 46), pos_hint={"center_x": 0.54, "center_y": 0.5}, background_color="#EBCBCB", halign='center')
        self.pages = Label(text="pages", font_size=36, size=(87, 44), pos_hint={"center_x": 0.70, "center_y": 0.5})
        self.download_button = Button(text='Download Manga', size_hint=(None, None), size=(388, 96), pos_hint={"center_x": 0.5, "y": 0.1}, background_color="#8C2323", font_size=48, border=(20,20,20,20))
        self.download_button.bind(on_press=self.download_manga)

        self.add_widget(self.image)
        self.add_widget(self.name_input)
        self.add_widget(self.fron)
        self.add_widget(self.select_page_input)
        self.add_widget(self.to)
        self.add_widget(self.end_page_input)
        self.add_widget(self.pages)
        self.add_widget(self.download_button)

    def download_manga(self, instance):
        main.download_images(self.name_input.text, self.select_page_input.text, self.end_page_input.text)

class MangaDownloaderApp(App):
    def build(self):
        Window.borderless = True
        Window.size = (700, 700)
        Window.clearcolor = ("#581F1F")
        return Container()

if __name__ == '__main__':
    MangaDownloaderApp().run()
