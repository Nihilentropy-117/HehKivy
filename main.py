from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from embedding_models import LocalSFR, GTELargeEnV15, EmberV1

embedding_models_list = [LocalSFR, GTELargeEnV15, EmberV1]
active_embedding_model = None


class TabA(BoxLayout):
    def __init__(self, **kwargs):
        super(TabA, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # Dropdowns
        dropdown1 = DropDown()
        for i in range(10):
            btn = Button(text=f'Option {i}', size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
            dropdown1.add_widget(btn)
        mainbutton1 = Button(text='Dropdown 1', size_hint=(1, None), height=44)
        mainbutton1.bind(on_release=dropdown1.open)
        dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
        self.add_widget(mainbutton1)

        dropdown2 = DropDown()
        for i in range(10):
            btn = Button(text=f'Option {i}', size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
            dropdown2.add_widget(btn)
        mainbutton2 = Button(text='Dropdown 2', size_hint=(1, None), height=44)
        mainbutton2.bind(on_release=dropdown2.open)
        dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
        self.add_widget(mainbutton2)

        # Text inputs
        textinput1 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        textinput2 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        self.add_widget(textinput1)
        self.add_widget(textinput2)

        # Buttons
        button1 = Button(text='Button 1', size_hint=(1, None), height=44)
        button2 = Button(text='Button 2', size_hint=(1, None), height=44)
        self.add_widget(button1)
        self.add_widget(button2)


class TabB(BoxLayout):
    def __init__(self, **kwargs):
        super(TabB, self).__init__(**kwargs)
        self.orientation = 'vertical'

        dropdown1 = DropDown()
        for i in range(10):
            btn = Button(text=f'Option {i}', size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
            dropdown1.add_widget(btn)
        mainbutton1 = Button(text='Dropdown 1', size_hint=(1, None), height=44)
        mainbutton1.bind(on_release=dropdown1.open)
        dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
        self.add_widget(mainbutton1)

        dropdown2 = DropDown()
        for i in range(10):
            btn = Button(text=f'Option {i}', size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
            dropdown2.add_widget(btn)
        mainbutton2 = Button(text='Dropdown 2', size_hint=(1, None), height=44)
        mainbutton2.bind(on_release=dropdown2.open)
        dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
        self.add_widget(mainbutton2)

        textinput1 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        textinput2 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        self.add_widget(textinput1)
        self.add_widget(textinput2)

        button1 = Button(text='Button 1', size_hint=(1, None), height=44)
        button2 = Button(text='Button 2', size_hint=(1, None), height=44)
        self.add_widget(button1)
        self.add_widget(button2)


class TabC(BoxLayout):
    def __init__(self, **kwargs):
        super(TabC, self).__init__(**kwargs)
        self.orientation = 'vertical'

        dropdown1 = DropDown()
        for i in range(10):
            btn = Button(text=f'Option {i}', size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
            dropdown1.add_widget(btn)
        mainbutton1 = Button(text='Dropdown 1', size_hint=(1, None), height=44)
        mainbutton1.bind(on_release=dropdown1.open)
        dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
        self.add_widget(mainbutton1)

        dropdown2 = DropDown()
        for i in range(10):
            btn = Button(text=f'Option {i}', size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
            dropdown2.add_widget(btn)
        mainbutton2 = Button(text='Dropdown 2', size_hint=(1, None), height=44)
        mainbutton2.bind(on_release=dropdown2.open)
        dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
        self.add_widget(mainbutton2)

        textinput1 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        textinput2 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        self.add_widget(textinput1)
        self.add_widget(textinput2)

        button1 = Button(text='Button 1', size_hint=(1, None), height=44)
        button2 = Button(text='Button 2', size_hint=(1, None), height=44)
        self.add_widget(button1)
        self.add_widget(button2)


class TabSettings(BoxLayout):
    def __init__(self, **kwargs):
        super(TabSettings, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # Adjust padding and spacing
        total_horizontal_padding = 100  # Total horizontal padding
        padding_left = total_horizontal_padding * 0.2
        padding_right = total_horizontal_padding * 0.8
        self.padding = [padding_left, 10, padding_right, 10]
        self.spacing = 10

        spacer = Widget(size_hint=(1, None),
                        height=44
                        )

        self.add_widget(Label(text='Embedding Model',
                              size_hint=(1, None),
                              height=44
                              ))

        spinner = Spinner(
            # default value shown
            text='Home',
            # available values
            values=[model.name for model in embedding_models_list],
            size_hint=(1, None),
            height=44)

        def show_selected_value(spinner, text):
            _ = spinner
            global active_embedding_model
            active_embedding_model = text
            print(f"Active Embedding Model Updated: {active_embedding_model}")

        spinner.bind(text=show_selected_value)
        self.add_widget(spinner)

        self.add_widget(spacer)

        textinput1 = TextInput(hint_text='Notes Files Directory', size_hint=(1, None), height=44)
        self.add_widget(textinput1)


        textinput2 = TextInput(hint_text='Enter text here', size_hint=(1, None), height=44)
        self.add_widget(textinput2)

        # Buttons
        button1 = Button(text='Button 1', size_hint=(1, None), height=44)
        button2 = Button(text='Button 2', size_hint=(1, None), height=44)
        self.add_widget(button1)
        self.add_widget(button2)

        # Transparent Widget to push all other widgets up
        self.add_widget(Widget())

    def update_active_model(self, spinner, text):
        global active_embedding_model
        active_embedding_model = text
        print(f"Active Embedding Model Updated: {active_embedding_model}")


class MyTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super(MyTabbedPanel, self).__init__(**kwargs)
        self.do_default_tab = False

        tab_a = TabbedPanelItem(text='Tab A')
        tab_a.add_widget(TabA())
        self.add_widget(tab_a)

        tab_b = TabbedPanelItem(text='Tab B')
        tab_b.add_widget(TabB())
        self.add_widget(tab_b)

        tab_c = TabbedPanelItem(text='Tab C')
        tab_c.add_widget(TabC())
        self.add_widget(tab_c)

        tab_d = TabbedPanelItem(text='Settings')
        tab_d.add_widget(TabSettings())
        self.add_widget(tab_d)


class MyApp(App):
    def build(self):
        return MyTabbedPanel()


if __name__ == '__main__':
    MyApp().run()
