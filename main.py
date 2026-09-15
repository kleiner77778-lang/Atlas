from kivy.app import App
from kivy.uix.label import Label

class AtlasApp(App):
    def build(self):
        return Label(text="Atlas E-Lkw Tracker läuft!")

if __name__ == '__main__':
    AtlasApp().run()
