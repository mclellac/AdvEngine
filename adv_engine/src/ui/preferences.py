import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject
from ..core.settings_manager import SettingsManager

class PreferencesDialog(Adw.PreferencesWindow):
    """
    A dialog for application preferences.
    """
    __gtype_name__ = "PreferencesDialog"

    def __init__(self, parent, project_manager=None, settings_manager=None):
        super().__init__(transient_for=parent, modal=True)
        self.project_manager = project_manager
        self.settings_manager = settings_manager

        self.set_search_enabled(False)

        # Appearance Page
        appearance_page = Adw.PreferencesPage()
        self.add(appearance_page)

        # Theme Group
        theme_group = Adw.PreferencesGroup(title="Appearance")
        appearance_page.add(theme_group)

        # Theme Selector
        style_manager = Adw.StyleManager.get_default()
        theme_row = Adw.ComboRow(
            title="Application Theme",
            model=Gtk.StringList.new(["System", "Light", "Dark"])
        )
        theme_group.add(theme_row)

        if style_manager.get_dark():
            if style_manager.get_system_supports_color_schemes():
                theme_row.set_selected(0)
            else:
                theme_row.set_selected(2)
        else:
            theme_row.set_selected(1)
        theme_row.connect("notify::selected", self.on_theme_selected)

        # Editor Group
        editor_group = Adw.PreferencesGroup(title="Editor")
        appearance_page.add(editor_group)

        # Autosave Switch
        autosave_row = Adw.SwitchRow(title="Enable Autosave")
        autosave_row.set_active(self.settings_manager.get_app_setting("autosave_enabled"))
        autosave_row.connect("notify::active", self.on_autosave_toggled)
        editor_group.add(autosave_row)

        # Project Page
        if self.project_manager:
            project_page = Adw.PreferencesPage()
            self.add(project_page)

            project_group = Adw.PreferencesGroup(title="Project Settings")
            project_page.add(project_group)

            # Project Name
            project_name_row = Adw.EntryRow(title="Project Name")
            project_name_row.set_text(self.settings_manager.get_project_setting("project_name"))
            project_name_row.connect("notify::text", self.on_project_name_changed)
            project_group.add(project_name_row)

            # Default Scene
            scene_names = [scene.name for scene in self.project_manager.data.scenes]
            scene_ids = [scene.id for scene in self.project_manager.data.scenes]

            default_scene_row = Adw.ComboRow(
                title="Default Starting Scene",
                model=Gtk.StringList.new(scene_names)
            )

            # Set initial selection
            default_scene_id = self.settings_manager.get_project_setting("default_scene")
            if default_scene_id in scene_ids:
                default_scene_row.set_selected(scene_ids.index(default_scene_id))

            default_scene_row.connect("notify::selected", self.on_default_scene_changed, scene_ids)
            project_group.add(default_scene_row)

    def on_theme_selected(self, combo_row, _):
        style_manager = Adw.StyleManager.get_default()
        selected = combo_row.get_selected()
        if selected == 0:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
        elif selected == 1:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def on_autosave_toggled(self, switch, _):
        self.settings_manager.set_app_setting("autosave_enabled", switch.get_active())

    def on_project_name_changed(self, entry_row, _):
        self.settings_manager.set_project_setting("project_name", entry_row.get_text())

    def on_default_scene_changed(self, combo_row, _, scene_ids):
        selected_index = combo_row.get_selected()
        if selected_index >= 0 and selected_index < len(scene_ids):
            self.settings_manager.set_project_setting("default_scene", scene_ids[selected_index])
