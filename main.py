import tomli
import tomli_w
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from sync_notes import sync as syncnotes
from kivy.uix.scrollview import ScrollView

# List of embedding models to choose from
embedding_models_list = ["LocalSFR", "GTELargeEnV15", "EmberV1"]
# Configuration file name
settings_file = "conf.toml"
# Default settings
default_settings = {
    "active_embedding_model": "GTELargeEnV15",
    "notes_directory": "./notes"
}

# Initialize settings with default values
settings = default_settings.copy()


# Custom Label class with a print method
class StatusLabel(Label):
    def xprint(self, text):
        self.text = text  # Update label text
        print(text)  # Print text to console


# Base class for tabs with common layout
class BaseTab(BoxLayout):
    def __init__(self, status_label, **kwargs):
        super(BaseTab, self).__init__(**kwargs)
        self.status_label = status_label  # Reference to status label
        self.orientation = 'vertical'  # Vertical layout

        total_horizontal_padding = 100  # Total padding value
        padding_left = total_horizontal_padding * 0.2  # Left padding
        padding_right = total_horizontal_padding * 0.8  # Right padding
        self.padding = [padding_left, 10, padding_right, 10]  # Set padding
        self.spacing = 10  # Space between widgets


# Tab for syncing notes
class TabSync(BaseTab):
    def __init__(self, status_label, **kwargs):
        super(TabSync, self).__init__(status_label, **kwargs)
        self.create_widgets()  # Initialize UI components

    def create_widgets(self):
        layout = BoxLayout(orientation='vertical')  # Main layout

        scroll_view = ScrollView(size_hint=(1, 1))  # Scrollable area
        self.label_output = Label(text='', size_hint_y=None)  # Label for output
        self.label_output.bind(texture_size=self.label_output.setter('size'))  # Adjust label size to text
        scroll_view.add_widget(self.label_output)  # Add label to scroll view
        layout.add_widget(scroll_view)  # Add scroll view to layout

        spacer = BoxLayout(size_hint_y=None, height=20)  # Spacer for spacing
        layout.add_widget(spacer)  # Add spacer to layout

        button_sync = Button(text='Sync Notes to Database', size_hint=(1, None), height=44)  # Sync button
        button_sync.bind(on_press=lambda instance: self.sync_notes())  # Bind sync action
        layout.add_widget(button_sync)  # Add button to layout

        self.add_widget(layout)  # Add main layout to tab

    def sync_notes(self):
        # Call sync function with current settings
        syncnotes(settings["active_embedding_model"], settings["notes_directory"], self.label_output)


# Example Tab B with text inputs and buttons
class TabB(BaseTab):
    def __init__(self, status_label, **kwargs):
        super(TabB, self).__init__(status_label, **kwargs)

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


# Example Tab C with text inputs and buttons (similar to Tab B)
class TabC(BaseTab):
    def __init__(self, status_label, **kwargs):
        super(TabC, self).__init__(status_label, **kwargs)

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


# Settings tab for configuring application settings
class TabSettings(BaseTab):
    def __init__(self, status_label, **kwargs):
        super(TabSettings, self).__init__(status_label, **kwargs)
        self.create_widgets()  # Initialize UI components
        self.load_config()  # Load initial configuration

    def create_widgets(self):
        self.add_widget(Label(text='Embedding Model', size_hint=(1, None), height=44))  # Label for spinner

        self.spinner_embedding_model = Spinner(
            text=settings["active_embedding_model"],
            values=embedding_models_list,
            size_hint=(1, None),
            height=44
        )  # Spinner for model selection
        self.spinner_embedding_model.bind(text=self.update_active_model)  # Bind spinner action
        self.add_widget(self.spinner_embedding_model)  # Add spinner to layout

        spacer = Widget(size_hint=(1, None), height=44)  # Spacer for spacing
        self.add_widget(spacer)  # Add spacer to layout

        self.textinput_notes_directory = TextInput(
            text=settings["notes_directory"],
            hint_text='Enter Notes Directory',
            size_hint=(1, None),
            height=44
        )  # Text input for notes directory
        self.textinput_notes_directory.bind(text=self.update_notes_directory)  # Bind text input action
        self.add_widget(self.textinput_notes_directory)  # Add text input to layout

        button_save = Button(text='Save', size_hint=(1, None), height=44)  # Save button
        button_save.bind(on_press=self.save_config)  # Bind save action
        self.add_widget(button_save)  # Add button to layout

        button_load = Button(text='Load', size_hint=(1, None), height=44)  # Load button
        button_load.bind(on_press=self.load_config)  # Bind load action
        self.add_widget(button_load)  # Add button to layout

        self.add_widget(Widget())  # Add empty widget for spacing

    def update_active_model(self, spinner, text):
        settings["active_embedding_model"] = text  # Update model in settings
        self.status_label.xprint(f"Active Embedding Model Updated: {settings['active_embedding_model']}")

    def update_notes_directory(self, instance, text):
        settings["notes_directory"] = text  # Update notes directory in settings

    def load_config(self, button=None):
        try:
            with open(settings_file, "rb") as f:
                global settings
                settings = tomli.load(f)  # Load settings from file
            self.populate_settings()  # Update UI with loaded settings
            self.status_label.xprint("Settings loaded from conf.toml")
        except FileNotFoundError:
            self.status_label.xprint("conf.toml not found. Using default settings.")

    def save_config(self, button):
        settings["active_embedding_model"] = self.spinner_embedding_model.text  # Save model from spinner
        settings["notes_directory"] = self.textinput_notes_directory.text  # Save directory from text input
        with open(settings_file, "wb") as f:
            tomli_w.dump(settings, f)  # Write settings to file
        self.status_label.xprint("Settings saved to conf.toml")

    def populate_settings(self):
        self.spinner_embedding_model.text = settings.get("active_embedding_model", "Select a Model")
        self.textinput_notes_directory.text = settings.get("notes_directory", "Enter Notes Directory")


# Custom tabbed panel with multiple tabs
class MyTabbedPanel(TabbedPanel):
    def __init__(self, status_label, **kwargs):
        super(MyTabbedPanel, self).__init__(**kwargs)
        self.status_label = status_label  # Reference to status label
        self.do_default_tab = False  # Disable default tab

        tab_sync = TabbedPanelItem(text='Sync')  # Sync tab
        tab_sync.add_widget(TabSync(self.status_label))  # Add sync tab content
        self.add_widget(tab_sync)  # Add sync tab to panel

        tab_b = TabbedPanelItem(text='Tab B')  # Tab B
        tab_b.add_widget(TabB(self.status_label))  # Add Tab B content
        self.add_widget(tab_b)  # Add Tab B to panel

        tab_c = TabbedPanelItem(text='Tab C')  # Tab C
        tab_c.add_widget(TabC(self.status_label))  # Add Tab C content
        self.add_widget(tab_c)  # Add Tab C to panel

        tab_d = TabbedPanelItem(text='Settings')  # Settings tab
        tab_d.add_widget(TabSettings(self.status_label))  # Add settings tab content
        self.add_widget(tab_d)  # Add settings tab to panel


# Main application class
class MyApp(App):
    def build(self):
        status_label = StatusLabel(size_hint_y=None, height=30, text="Welcome", halign="center", valign="middle")
        status_label.bind(size=status_label.setter('text_size'))  # Center text in status label

        tabbed_panel = MyTabbedPanel(status_label)  # Initialize custom tabbed panel

        layout = BoxLayout(orientation='vertical')  # Main layout
        layout.add_widget(tabbed_panel)  # Add tabbed panel to layout
        layout.add_widget(status_label)  # Add status label to layout

        return layout  # Return main layout


if __name__ == '__main__':
    MyApp().run()  # Run the application
