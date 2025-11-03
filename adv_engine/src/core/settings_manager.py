"""
Manages application and project settings.
"""

import os
import json

class SettingsManager:
    def __init__(self, project_path=None):
        self.project_path = project_path
        self.app_settings_file = os.path.expanduser("~/.config/adv_engine/settings.json")
        self.project_settings_file = None
        if self.project_path:
            self.project_settings_file = os.path.join(self.project_path, "settings.json")

        self.app_settings = self._load_settings(self.app_settings_file, self._get_default_app_settings())
        self.project_settings = self._load_settings(self.project_settings_file, self._get_default_project_settings())

    def _get_default_app_settings(self):
        return {
            "autosave_enabled": True,
            "autosave_interval": 5, # in minutes
            "default_project_dir": os.path.expanduser("~/Documents/AdvEngineProjects")
        }

    def _get_default_project_settings(self):
        return {
            "project_name": "New Project",
            "default_scene": None
        }

    def _load_settings(self, file_path, defaults):
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    settings = json.load(f)
                    defaults.update(settings)
                    return defaults
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings from {file_path}: {e}")
                return defaults
        return defaults

    def _save_settings(self, file_path, settings):
        if file_path:
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    json.dump(settings, f, indent=2)
            except IOError as e:
                print(f"Error saving settings to {file_path}: {e}")

    def get_app_setting(self, key):
        return self.app_settings.get(key)

    def set_app_setting(self, key, value):
        self.app_settings[key] = value
        self._save_settings(self.app_settings_file, self.app_settings)

    def get_project_setting(self, key):
        return self.project_settings.get(key)

    def set_project_setting(self, key, value):
        self.project_settings[key] = value
        self._save_settings(self.project_settings_file, self.project_settings)
