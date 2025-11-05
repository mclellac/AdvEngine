import sys
import subprocess
import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GObject

from .core.project_manager import ProjectManager
from .core.data_schemas import DialogueNode
from .ui.item_editor import ItemEditor
from .ui.attribute_editor import AttributeEditor
from .ui.verb_editor import VerbEditor
from .ui.module_character import CharacterManager
from .ui.module_quest import QuestEditor
from .ui.module_ui_builder import UIBuilder
from .ui.module_font import FontManager
from .ui.module_log import LogViewer
from .ui.module_scene import SceneEditor
from .ui.module_logic import LogicEditor
from .ui.module_dialogue import DialogueEditor
from .ui.module_cutscene import CutsceneEditor
from .ui.module_assets import AssetEditor
from .ui.module_audio import AudioEditor
from .ui.module_state import GlobalStateEditor
from .ui.module_interaction import InteractionEditor
from .ui.preferences import PreferencesDialog
from .ui.shortcuts import ShortcutsDialog
from .ui.search_results import SearchResultsView
from .ui.welcome import WelcomeWindow


class EditorWindow(Adw.ApplicationWindow):
    def __init__(self, project_manager, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.base_title = "AdvEngine"
        self.set_title(self.base_title)
        self.set_default_size(1280, 800)

        self.project_manager.register_dirty_state_callback(self.on_dirty_state_changed)

        main_container = Adw.ToolbarView()
        self.set_content(main_container)

        header = Adw.HeaderBar()
        main_container.add_top_bar(header)

        self.toggle_button = Gtk.ToggleButton(icon_name="sidebar-show-symbolic", tooltip_text="Toggle Sidebar")
        header.pack_start(self.toggle_button)

        save_button = Gtk.Button(label="Save", tooltip_text="Save project (Ctrl+S)")
        save_button.connect("clicked", self.on_save_clicked)
        header.pack_start(save_button)

        play_button = Gtk.Button(label="Play", tooltip_text="Launch game (Ctrl+P)")
        play_button.connect("clicked", self._on_play_clicked)
        header.pack_start(play_button)

        new_project_button = Gtk.Button(label="New Project", tooltip_text="Create a new project")
        new_project_button.connect("clicked", lambda w: self.get_application().lookup_action("new-project").activate(None))
        header.pack_start(new_project_button)

        menu = Gio.Menu.new()
        menu.append("Preferences", "app.preferences")
        menu.append("Keyboard Shortcuts", "app.shortcuts")
        menu.append("About", "app.about")
        menu_button = Gtk.MenuButton(menu_model=menu, icon_name="open-menu-symbolic")
        header.pack_end(menu_button)

        search_entry = Gtk.SearchEntry(placeholder_text="Search Project")
        search_entry.connect("search-changed", self.on_search_changed)
        header.pack_end(search_entry)

        self.split_view = Adw.OverlaySplitView()
        main_container.set_content(self.split_view)

        self.toggle_button.bind_property("active", self.split_view, "show-sidebar", GObject.BindingFlags.BIDIRECTIONAL)

        self.content_stack = Adw.ViewStack()
        self.split_view.set_content(self.content_stack)

        self.sidebar_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)
        sidebar_scroll = Gtk.ScrolledWindow(child=self.sidebar_list)
        self.split_view.set_sidebar(sidebar_scroll)

        self.add_editor("Scenes", "scenes_editor", SceneEditor(self.project_manager))
        self.logic_editor = LogicEditor(self.project_manager)
        self.add_editor("Logic", "logic_editor", self.logic_editor)
        self.add_editor("Interactions", "interaction_editor", InteractionEditor(self.project_manager))
        self.add_editor("Dialogue", "dialogue_editor", DialogueEditor(self.project_manager))
        self.add_editor("Cutscenes", "cutscene_editor", CutsceneEditor(self.project_manager))
        self.add_editor("Assets", "assets_editor", AssetEditor(self.project_manager))
        self.add_editor("Audio", "audio_editor", AudioEditor(self.project_manager))
        self.add_editor("Global State", "global_state_editor", GlobalStateEditor(self.project_manager))
        self.add_editor("Characters", "character_manager", CharacterManager(self.project_manager))
        self.add_editor("Quests", "quest_editor", QuestEditor(self.project_manager))
        self.add_editor("UI Builder", "ui_builder", UIBuilder(self.project_manager))
        self.add_editor("Fonts", "font_manager", FontManager(self.project_manager))
        self.add_editor("Log", "log_viewer", LogViewer(self.project_manager))

        db_stack = Adw.ViewStack()
        db_switcher = Adw.ViewSwitcher(stack=db_stack)
        db_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        db_box.append(db_switcher)
        db_box.append(db_stack)
        db_stack.add_titled_with_icon(ItemEditor(self.project_manager), "items", "Items", "edit-find-replace-symbolic")
        db_stack.add_titled_with_icon(AttributeEditor(self.project_manager), "attributes", "Attributes", "document-properties-symbolic")
        db_stack.add_titled_with_icon(VerbEditor(self.project_manager), "verbs", "Verbs", "input-gaming-symbolic")
        self.add_editor("Database", "db_editor", db_box)

        self.search_results_view = SearchResultsView()
        self.content_stack.add_named(self.search_results_view, "search_results")

        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(self.sidebar_list, self.sidebar_list.get_selected_row())
        self.split_view.set_show_sidebar(True)

    def on_search_changed(self, search_entry):
        query = search_entry.get_text()
        if not query:
            if self.content_stack.get_visible_child_name() == "search_results":
                self.content_stack.set_visible_child_name("scenes_editor")
            return
        results = self.project_manager.search(query)
        self.search_results_view.update_results(results)
        self.content_stack.set_visible_child_name("search_results")

    def add_editor(self, name, view_name, widget):
        row = Adw.ActionRow(title=name)
        list_box_row = Gtk.ListBoxRow(name=view_name, child=row)
        self.sidebar_list.append(list_box_row)
        self.content_stack.add_named(widget, view_name)

    def on_sidebar_activated(self, listbox, row):
        if row:
            view_name = row.get_name()
            self.content_stack.set_visible_child_name(view_name)

    def on_dirty_state_changed(self, is_dirty):
        self.set_title(f"{self.base_title}{'*' if is_dirty else ''}")

    def on_save_clicked(self, button):
        self.get_application().save_project()

    def _on_play_clicked(self, button):
        self.get_application().save_project()
        ue_path = self.get_application().settings_manager.get("ue_path")
        if not ue_path:
            dialog = Adw.MessageDialog(transient_for=self, heading="Unreal Engine Path Not Set",
                                       body="Please set the path to the Unreal Engine editor in the preferences.")
            dialog.add_response("ok", "OK")
            dialog.connect("response", lambda d, r: d.close())
            dialog.present()
            return
        project_file = f"{self.project_manager.project_path}/AdvEngine.uproject"
        try:
            subprocess.Popen([ue_path, project_file])
        except FileNotFoundError:
            dialog = Adw.MessageDialog(transient_for=self, heading="Unreal Engine Not Found",
                                       body=f"Could not find the Unreal Engine editor at the specified path: {ue_path}")
            dialog.add_response("ok", "OK")
            dialog.connect("response", lambda d, r: d.close())
            dialog.present()
        except Exception as e:
            dialog = Adw.MessageDialog(transient_for=self, heading="Error Launching Engine",
                                       body=f"An unexpected error occurred: {e}")
            dialog.add_response("ok", "OK")
            dialog.connect("response", lambda d, r: d.close())
            dialog.present()


from .core.settings_manager import SettingsManager

class AdvEngine(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = None
        self.settings_manager = SettingsManager()
        self.win = None
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        if not self.win:
            self.win = WelcomeWindow(application=self)
        self.win.present()

        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", lambda a, p: self.save_project())
        self.add_action(save_action)
        self.set_accels_for_action("app.save", ["<Primary>s"])

        play_action = Gio.SimpleAction.new("play", None)
        play_action.connect("activate", lambda a, p: self.win._on_play_clicked(None) if hasattr(self.win, '_on_play_clicked') else None)
        self.add_action(play_action)
        self.set_accels_for_action("app.play", ["<Primary>p"])

        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_activate)
        self.add_action(preferences_action)

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.on_shortcuts_activate)
        self.add_action(shortcuts_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        self.add_action(about_action)

        new_project_action = Gio.SimpleAction.new("new-project", None)
        new_project_action.connect("activate", self.on_new_project_activate)
        self.add_action(new_project_action)

        open_project_action = Gio.SimpleAction.new("open-project", None)
        open_project_action.connect("activate", self.on_open_project_activate)
        self.add_action(open_project_action)

        export_localization_action = Gio.SimpleAction.new("export-localization", None)
        export_localization_action.connect("activate", self.on_export_localization)
        self.add_action(export_localization_action)

        import_localization_action = Gio.SimpleAction.new("import-localization", None)
        import_localization_action.connect("activate", self.on_import_localization)
        self.add_action(import_localization_action)

        self.setup_navigation_shortcuts()

    def setup_navigation_shortcuts(self):
        shortcuts = {
            "1": "scenes_editor", "2": "logic_editor", "3": "interaction_editor",
            "4": "dialogue_editor", "5": "cutscenes_editor", "6": "assets_editor",
            "7": "global_state_editor", "8": "character_manager", "9": "quest_editor",
            "0": "db_editor",
        }
        for key, view_name in shortcuts.items():
            action = Gio.SimpleAction(name=f"go-to-{view_name}")
            action.connect("activate", self.on_go_to, view_name)
            self.add_action(action)
            self.set_accels_for_action(f"app.go-to-{view_name}", [f"<Primary>{key}"])

    def on_go_to(self, action, param, view_name):
        if self.win and isinstance(self.win, EditorWindow):
            self.win.content_stack.set_visible_child_name(view_name)
            for row in self.win.sidebar_list:
                if row.get_name() == view_name:
                    self.win.sidebar_list.select_row(row)
                    break

    def on_export_localization(self, action, param):
        dialog = Gtk.FileChooserNative(title="Export Localization", transient_for=self.win, action=Gtk.FileChooserAction.SAVE)
        dialog.connect("response", lambda d, r: self.on_export_localization_response(d,r))
        dialog.show()

    def on_export_localization_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            self.project_manager.export_localization(file.get_path())

    def on_import_localization(self, action, param):
        dialog = Gtk.FileChooserNative(title="Import Localization", transient_for=self.win, action=Gtk.FileChooserAction.OPEN)
        dialog.connect("response", lambda d, r: self.on_import_localization_response(d, r))
        dialog.show()

    def on_import_localization_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            self.project_manager.import_localization(file.get_path())

    def on_open_project_activate(self, action, param):
        dialog = Gtk.FileChooserNative(title="Open Project", transient_for=self.win, action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.connect("response", lambda d, r: self.on_open_project_response(d, r))
        dialog.show()

    def on_open_project_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder = dialog.get_file().get_path()
            self.load_project(folder)

    def on_preferences_activate(self, action, param):
        dialog = PreferencesDialog(parent=self.win, project_manager=self.project_manager, settings_manager=self.settings_manager)
        dialog.present()

    def on_shortcuts_activate(self, action, param):
        dialog = ShortcutsDialog(transient_for=self.win)
        dialog.present()

    def on_about_activate(self, action, param):
        dialog = Adw.AboutWindow(transient_for=self.win, application_name="AdvEngine", developer_name="Carey McLelland", version="0.1.0")
        dialog.present()

    def save_project(self):
        if self.project_manager and self.project_manager.is_dirty:
            self.project_manager.save_project()

    def load_project(self, project_path, project_manager=None):
        if project_manager:
            self.project_manager = project_manager
        else:
            self.project_manager = ProjectManager(project_path)
        self.project_manager.load_project()
        self.settings_manager.add_recent_project(project_path)
        new_win = EditorWindow(application=self, project_manager=self.project_manager)
        new_win.present()
        if self.win:
            self.win.close()
        self.win = new_win

    def on_new_project_activate(self, action, param):
        dialog = Adw.MessageDialog(transient_for=self.win, heading="Create New Project")
        entry = Adw.EntryRow(title="Project Name")
        templates = ProjectManager.get_templates()
        combo = Adw.ComboRow(title="Template", model=Gtk.StringList.new(templates))
        combo.set_selected(0)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.append(entry)
        box.append(combo)
        dialog.set_extra_child(box)
        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("create", "_Create")

        def on_response(d, response):
            if response == "create":
                name = entry.get_text()
                selected_item = combo.get_selected_item()
                if not name or not selected_item:
                    error_dialog = Adw.MessageDialog(
                        transient_for=self.win,
                        heading="Error",
                        body="Project name cannot be empty.",
                    )
                    error_dialog.add_response("ok", "OK")
                    error_dialog.connect("response", lambda d, r: d.destroy())
                    error_dialog.present()
                    return
                template = selected_item.get_string()
                if name:
                    file_dialog = Gtk.FileChooserNative(title="Select Project Location", transient_for=self.win, action=Gtk.FileChooserAction.SELECT_FOLDER)
                    file_dialog.connect("response", lambda fd, resp: self.on_new_project_folder_selected(fd, resp, name, template))
                    file_dialog.show()
            d.destroy()
        dialog.connect("response", on_response)
        dialog.present()

    def on_new_project_folder_selected(self, dialog, response, name, template):
        if response == Gtk.ResponseType.ACCEPT:
            folder = dialog.get_file().get_path()
            project_path = os.path.join(folder, name)
            project_manager, error = ProjectManager.create_project(project_path, template)
            if project_manager:
                self.load_project(project_path, project_manager=project_manager)
            else:
                print(f"Error: {error}")

def main(version="0.1.0"):
    app = AdvEngine()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()
