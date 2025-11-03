import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject

class PreferencesDialog(Adw.PreferencesWindow):
    """
    A dialog for application preferences.
    """
    __gtype_name__ = "PreferencesDialog"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(kwargs.get("parent"))
        self.set_modal(True)
        self.set_search_enabled(False)

        # Appearance Page
        page = Adw.PreferencesPage()
        self.add(page)

        # Theme Group
        group = Adw.PreferencesGroup(title="Appearance")
        page.add(group)

        # Theme Selector
        style_manager = Adw.StyleManager.get_default()

        row = Adw.ComboRow(
            title="Application Theme",
            model=Gtk.StringList.new(["System", "Light", "Dark"])
        )
        group.add(row)

        # Set initial selection based on current theme
        if style_manager.get_dark():
             if style_manager.get_system_supports_color_schemes():
                 row.set_selected(0) # System
             else:
                 row.set_selected(2) # Dark
        else:
            row.set_selected(1) # Light

        row.connect("notify::selected", self.on_theme_selected)

    def on_theme_selected(self, combo_row, _):
        """
        Applies the selected theme.
        """
        style_manager = Adw.StyleManager.get_default()
        selected = combo_row.get_selected()
        if selected == 0: # System
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        elif selected == 1: # Light
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else: # Dark
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
