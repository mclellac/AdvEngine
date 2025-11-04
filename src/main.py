import sys
import subprocess
import gi

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


class AdvEngineWindow(Adw.ApplicationWindow):
    def __init__(self, project_manager, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = project_manager
        self.base_title = "AdvEngine"
        self.set_title(self.base_title)
        self.set_default_size(1280, 800)

        self.project_manager.register_dirty_state_callback(self.on_dirty_state_changed)

        # Use a ToolbarView as the main content container
        main_container = Adw.ToolbarView()
        self.set_content(main_container)

        header = Adw.HeaderBar()
        main_container.add_top_bar(header)

        # Sidebar Toggle
        self.toggle_button = Gtk.ToggleButton(icon_name="sidebar-show-symbolic", tooltip_text="Toggle Sidebar")
        header.pack_start(self.toggle_button)

        save_button = Gtk.Button(label="Save", tooltip_text="Save project (Ctrl+S)")
        save_button.set_css_classes(["flat"])
        save_button.connect("clicked", self.on_save_clicked)
        header.pack_start(save_button)

        play_button = Gtk.Button(label="Play", tooltip_text="Launch game (Ctrl+P)")
        play_button.set_css_classes(["flat"])
        play_button.connect("clicked", self._on_play_clicked)
        header.pack_start(play_button)

        new_project_button = Gtk.Button(label="New Project", tooltip_text="Create a new project")
        new_project_button.set_css_classes(["flat"])
        new_project_button.connect("clicked", lambda w: self.get_application().lookup_action("new-project").activate(None))
        header.pack_start(new_project_button)

        menu = Gio.Menu.new()
        menu.append("Preferences", "app.preferences")
        menu.append("Keyboard Shortcuts", "app.shortcuts")
        menu.append("Export Localization", "app.export-localization")
        menu.append("Import Localization", "app.import-localization")
        menu.append("About", "app.about")

        menu_button = Gtk.MenuButton(menu_model=menu, icon_name="open-menu-symbolic", tooltip_text="Application Menu")
        header.pack_end(menu_button)

        search_entry = Gtk.SearchEntry(placeholder_text="Search Project")
        search_entry.connect("search-changed", self.on_search_changed)
        header.pack_end(search_entry)

        # Use Adw.OverlaySplitView for a modern layout
        self.split_view = Adw.OverlaySplitView()
        main_container.set_content(self.split_view)

        self.toggle_button.bind_property("active", self.split_view, "show-sidebar", GObject.BindingFlags.BIDIRECTIONAL)

        self.content_stack = Adw.ViewStack()
        self.split_view.set_content(self.content_stack)

        welcome_label = Gtk.Label(label="Select an editor from the sidebar.", css_classes=["title-1"])
        welcome_page = Adw.StatusPage(child=welcome_label)
        self.content_stack.add_named(welcome_page, "welcome")

        # --- Sidebar setup ---
        sidebar_scroll = Gtk.ScrolledWindow()
        self.sidebar_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE, css_classes=["boxed-list"])
        self.sidebar_list.connect("row-activated", self.on_sidebar_activated)
        sidebar_scroll.set_child(self.sidebar_list)
        self.split_view.set_sidebar(sidebar_scroll)

        # --- Instantiate and Add Editors ---
        self.add_editor("Scenes", "scenes_editor", SceneEditor(self.project_manager))
        self.add_editor("Logic", "logic_editor", LogicEditor(self.project_manager))
        self.add_editor("Interactions", "interaction_editor", InteractionEditor(self.project_manager))
        self.add_editor("Dialogue", "dialogue_editor", DialogueEditor(self.project_manager))
        self.add_editor("Cutscenes", "cutscene_editor", CutsceneEditor(self.project_manager))
        self.add_editor("Assets", "assets_editor", AssetEditor(self.project_manager))
        self.add_editor("Global State", "global_state_editor", GlobalStateEditor(self.project_manager))
        self.add_editor("Characters", "character_manager", CharacterManager(self.project_manager))
        self.add_editor("Quests", "quest_editor", QuestEditor(self.project_manager))
        self.add_editor("UI Builder", "ui_builder", UIBuilder(self.project_manager))
        self.add_editor("Fonts", "font_manager", FontManager(self.project_manager))
        self.add_editor("Log", "log_viewer", LogViewer(self.project_manager))

        verbs_items_stack = Adw.ViewStack()
        verbs_items_switcher = Adw.ViewSwitcher(stack=verbs_items_stack, policy=Adw.ViewSwitcherPolicy.WIDE)
        verbs_items_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        verbs_items_container.append(verbs_items_switcher)
        verbs_items_container.append(verbs_items_stack)

        verbs_items_stack.add_titled_with_icon(ItemEditor(self.project_manager), "items", "Items", "edit-find-replace-symbolic")
        verbs_items_stack.add_titled_with_icon(AttributeEditor(self.project_manager), "attributes", "Attributes", "document-properties-symbolic")
        verbs_items_stack.add_titled_with_icon(VerbEditor(self.project_manager), "verbs", "Verbs", "input-gaming-symbolic")
        self.add_editor("Database", "verbs_items_editor", verbs_items_container)

        self.add_editor("Audio", "audio_editor", AudioEditor(self.project_manager))

        self.search_results_view = SearchResultsView()
        self.content_stack.add_named(self.search_results_view, "search_results")

        # Set initial state
        self.sidebar_list.select_row(self.sidebar_list.get_row_at_index(0))
        self.on_sidebar_activated(self.sidebar_list, self.sidebar_list.get_selected_row())
        self.split_view.set_show_sidebar(True)

        self.setup_logic_editor_actions()

    def setup_logic_editor_actions(self):
        add_dialogue_action = Gio.SimpleAction.new("add-dialogue-node", None)
        add_dialogue_action.connect(
            "activate", lambda a, p: self.logic_editor.on_add_dialogue_node(None)
        )
        self.add_action(add_dialogue_action)

        add_condition_action = Gio.SimpleAction.new("add-condition-node", None)
        add_condition_action.connect(
            "activate", lambda a, p: self.logic_editor.on_add_condition_node(None)
        )
        self.add_action(add_condition_action)

        add_action_action = Gio.SimpleAction.new("add-action-node", None)
        add_action_action.connect(
            "activate", lambda a, p: self.logic_editor.on_add_action_node(None)
        )
        self.add_action(add_action_action)

        edit_node_action = Gio.SimpleAction.new("edit-node", None)
        edit_node_action.connect(
            "activate",
            lambda a, p: self.logic_editor.edit_node_dialog(
                self.logic_editor.selected_nodes[0]
            ),
        )
        self.add_action(edit_node_action)

        delete_node_action = Gio.SimpleAction.new("delete-node", None)
        delete_node_action.connect(
            "activate", lambda a, p: self.logic_editor.on_delete_node(None)
        )
        self.add_action(delete_node_action)

        add_action_to_dialogue_action = Gio.SimpleAction.new("add-action-to-dialogue", None)
        add_action_to_dialogue_action.connect("activate", self.on_add_action_to_dialogue)
        self.add_action(add_action_to_dialogue_action)

    def on_search_changed(self, search_entry):
        """Handler for the search entry's search-changed signal."""
        query = search_entry.get_text()
        if not query:
            if self.content_stack.get_visible_child_name() == "search_results":
                self.content_stack.set_visible_child_name("welcome")
            return

        results = self.project_manager.search(query)
        self.search_results_view.update_results(results)
        self.content_stack.set_visible_child_name("search_results")

    def on_add_action_to_dialogue(self, action, param):
        if self.logic_editor.selected_nodes and isinstance(self.logic_editor.selected_nodes[0], DialogueNode):
            dialogue_node = self.logic_editor.selected_nodes[0]

            # Create a new action node
            new_node = self.logic_editor.on_add_action_node(None, return_node=True)

            # Position it to the right of the dialogue node
            new_node.x = dialogue_node.x + dialogue_node.width + 50
            new_node.y = dialogue_node.y

            # Connect them
            dialogue_node.outputs.append(new_node.id)
            new_node.inputs.append(dialogue_node.id)

            self.logic_editor.project_manager.set_dirty()
            self.logic_editor.canvas.queue_draw()
            self.logic_editor.minimap.queue_draw()

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
        """
        Handler for the play button click.
        Saves the project and attempts to launch the Unreal Engine editor.
        """
        self.get_application().save_project()

        # This is a placeholder for running the Unreal Engine project.
        # In a real scenario, you'd fetch the UE path from settings.
        ue_path = "/path/to/unreal/engine/bin/editor"
        project_file = f"{self.project_manager.project_path}/AdvEngine.uproject"

        try:
            subprocess.Popen([ue_path, project_file])
            print(f"Launching Unreal Engine with project: {project_file}")
        except FileNotFoundError:
            print(f"Error: Could not find the Unreal Engine editor at '{ue_path}'.")
            # In a real app, you'd show a user-friendly error dialog.
            error_dialog = Adw.MessageDialog(
                transient_for=self,
                heading="Unreal Engine Not Found",
                body=f"Could not find the Unreal Engine editor at the specified path: {ue_path}. Please configure the correct path in the application settings.",
            )
            error_dialog.add_response("ok", "OK")
            error_dialog.connect("response", lambda d, r: d.close())
            error_dialog.present()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            error_dialog = Adw.MessageDialog(
                transient_for=self,
                heading="Error Launching Engine",
                body=f"An unexpected error occurred while trying to launch Unreal Engine: {e}",
            )
            error_dialog.add_response("ok", "OK")
            error_dialog.connect("response", lambda d, r: d.close())
            error_dialog.present()


class AdvEngine(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_manager = None
        self.win = None
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        # This is called when the application is first launched
        self.load_project("TestGame")

        save_action = Gio.SimpleAction.new("save-project", None)
        save_action.connect("activate", lambda a, p: self.save_project())
        self.add_action(save_action)
        self.set_accels_for_action("app.save-project", ["<Primary>s"])

        play_action = Gio.SimpleAction.new("play-game", None)
        play_action.connect("activate", lambda a, p: self.win._on_play_clicked(None))
        self.add_action(play_action)
        self.set_accels_for_action("app.play-game", ["<Primary>p"])

        new_project_action = Gio.SimpleAction.new("new-project", None)
        new_project_action.connect("activate", self.on_new_project_activate)
        self.add_action(new_project_action)

        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_activate)
        self.add_action(preferences_action)

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.on_shortcuts_activate)
        self.add_action(shortcuts_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        self.add_action(about_action)

        export_localization_action = Gio.SimpleAction.new("export-localization", None)
        export_localization_action.connect("activate", self.on_export_localization)
        self.add_action(export_localization_action)

        import_localization_action = Gio.SimpleAction.new("import-localization", None)
        import_localization_action.connect("activate", self.on_import_localization)
        self.add_action(import_localization_action)

        self.setup_navigation_shortcuts()

    def setup_navigation_shortcuts(self):
        shortcuts = {
            "1": "scenes_editor",
            "2": "logic_editor",
            "3": "interaction_editor",
            "4": "dialogue_editor",
            "5": "cutscenes_editor",
            "6": "assets_editor",
            "7": "global_state_editor",
            "8": "character_manager",
            "9": "quest_editor",
            "0": "verbs_items_editor",
        }
        for key, view_name in shortcuts.items():
            action = Gio.SimpleAction(name=f"go-to-{view_name}")
            action.connect("activate", self.on_go_to, view_name)
            self.add_action(action)
            self.set_accels_for_action(f"app.go-to-{view_name}", [f"<Primary>{key}"])

    def on_go_to(self, action, param, view_name):
        if self.win:
            self.win.content_stack.set_visible_child_name(view_name)
            for row in self.win.sidebar_list:
                if row.get_name() == view_name:
                    self.win.sidebar_list.select_row(row)
                    break

    def on_export_localization(self, action, param):
        """Handler for the export localization menu item."""
        dialog = Gtk.FileChooserNative(
            title="Export Localization",
            transient_for=self.win,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save"
        )

        def on_dialog_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                self.project_manager.export_localization(file.get_path())

        dialog.connect("response", on_dialog_response)
        dialog.show()

    def on_import_localization(self, action, param):
        """Handler for the import localization menu item."""
        dialog = Gtk.FileChooserNative(
            title="Import Localization",
            transient_for=self.win,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open"
        )

        def on_dialog_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                self.project_manager.import_localization(file.get_path())

        dialog.connect("response", on_dialog_response)
        dialog.show()

    def save_project(self):
        """Saves the current project if it's dirty."""
        if self.project_manager and self.project_manager.is_dirty:
            self.project_manager.save_project()

    def load_project(self, project_path):
        """Loads a project and shows its window."""
        self.project_manager = ProjectManager(project_path)
        self.project_manager.load_project()

        # Create a new window for the project
        new_win = AdvEngineWindow(
            application=self, project_manager=self.project_manager
        )
        new_win.present()

        # If there was an old window, close it.
        if self.win:
            self.win.close()

        self.win = new_win

    def on_new_project_activate(self, action, param):
        dialog = Gtk.FileChooserNative(
            title="Create a New Project",
            transient_for=self.win,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            accept_label="_Create"
        )

        # The DropDown for templates can't be easily added to a native dialog.
        # For now, we'll simplify and always use the default template.
        # A better solution might involve a custom dialog before opening the file chooser.

        def on_dialog_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                folder = dialog.get_file().get_path()
                # TODO: Re-implement template selection. For now, use default.
                template = ProjectManager.get_templates()[0]
                success, error = ProjectManager.create_project(folder, template)
                if success:
                    self.load_project(folder)
                else:
                    # You might want to show an error dialog here
                    print(f"Error creating project: {error}")

        dialog.connect("response", on_dialog_response)
        dialog.show()

    def on_preferences_activate(self, action, param):
        dialog = PreferencesDialog(parent=self.win, project_manager=self.project_manager, settings_manager=self.project_manager.settings)
        dialog.present()

    def on_shortcuts_activate(self, action, param):
        dialog = ShortcutsDialog(transient_for=self.win)
        dialog.present()

    def on_about_activate(self, action, param):
        dialog = Adw.AboutWindow(
            transient_for=self.win,
            application_name="AdvEngine",
            developer_name="Carey McLelland",
            version="0.1.0",
            comments="A modern adventure game editor.",
            website="https://example.com",
        )
        dialog.present()


def main(version="0.1.0"):
    """
    Main entry point for the AdvEngine application.

    Initializes and runs the Adw.Application.
    """
    app = AdvEngine()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
