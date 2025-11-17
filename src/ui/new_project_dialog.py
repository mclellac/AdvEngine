import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from ..core.project_manager import ProjectManager


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), "new_project_dialog.ui"))
class NewProjectDialog(Adw.AlertDialog):
    __gtype_name__ = "NewProjectDialog"

    project_name_entry = Gtk.Template.Child()
    template_combo = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._populate_templates()

    def _populate_templates(self):
        templates = ProjectManager.get_templates()
        self.template_combo.set_model(Gtk.StringList.new(templates))
        if templates:
            self.template_combo.set_selected(0)

    def get_project_name(self):
        return self.project_name_entry.get_text()

    def get_selected_template(self):
        selected_item = self.template_combo.get_selected_item()
        if selected_item:
            return selected_item.get_string()
        return None
