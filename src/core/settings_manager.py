"""Manages application and project settings for AdvEngine.

This module provides the SettingsManager class, which handles the loading,
saving, and accessing of both global application settings and project-specific
settings.
"""

import os
import json


class SettingsManager:
    """Handles loading and saving of configuration files.

    This class manages two types of settings files: a global application
    settings file stored in the user's config directory, and an optional
    project-specific settings file located at the root of a project. Project
    settings, when present, override the application settings.

    Attributes:
        project_path (str): The absolute path to the project directory.
        app_settings_file (str): The path to the application settings file.
        project_settings_file (str): The path to the project settings file.
        app_settings (dict): A dictionary of application-level settings.
        project_settings (dict): A dictionary of project-level settings.
    """

    def __init__(self, project_path: str = None):
        """Initializes a new SettingsManager instance.

        Args:
            project_path (str, optional): The absolute path to the project
                directory. Defaults to None.
        """
        self.project_path = project_path
        self.app_settings_file = os.path.expanduser(
            "~/.config/adv_engine/settings.json"
        )
        self.project_settings_file = None
        if self.project_path:
            self.project_settings_file = os.path.join(
                self.project_path, "settings.json"
            )

        self.app_settings = self._load_settings(
            self.app_settings_file, self._get_default_app_settings()
        )
        self.project_settings = self._load_settings(
            self.project_settings_file, self._get_default_project_settings()
        )

    def _get_default_app_settings(self):
        """Returns a dictionary with default application settings."""
        return {
            "recent_projects": [],
            "autosave_enabled": True,
            "autosave_interval": 5,
            "default_project_dir": os.path.expanduser("~/Documents/AdvEngineProjects"),
            "author": "",
            "ue_path": "",
            "default_node_width": 240,
            "default_node_height": 160,
            "grid_snap_enabled": True,
            "grid_size": 20,
        }

    def _get_default_project_settings(self):
        """Returns a dictionary with default project settings."""
        return {
            "project_name": "New Project",
            "default_scene": None,
            "author": self.get_app_setting("author"),
        }

    def _load_settings(self, file_path: str, defaults: dict) -> dict:
        """Loads a settings file from a given path.

        If the file does not exist or is invalid, it returns the defaults.

        Args:
            file_path (str): The path to the settings file.
            defaults (dict): The default settings to use if loading fails.

        Returns:
            dict: The loaded settings.
        """
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

    def _save_settings(self, file_path: str, settings: dict):
        """Saves a dictionary of settings to a file.

        Args:
            file_path (str): The path to the settings file.
            settings (dict): The settings dictionary to save.
        """
        if file_path:
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    json.dump(settings, f, indent=2)
            except IOError as e:
                print(f"Error saving settings to {file_path}: {e}")

    def get_app_setting(self, key: str):
        """Gets a specific application setting by key.

        Args:
            key (str): The key of the setting to retrieve.

        Returns:
            The value of the setting, or None if not found.
        """
        return self.app_settings.get(key)

    def set_app_setting(self, key: str, value):
        """Sets the value of an application setting and saves to disk.

        Args:
            key (str): The key of the setting to set.
            value: The new value of the setting.
        """
        self.app_settings[key] = value
        self._save_settings(self.app_settings_file, self.app_settings)

    def get_project_setting(self, key: str):
        """Gets a specific project setting by key.

        Args:
            key (str): The key of the setting to retrieve.

        Returns:
            The value of the setting, or None if not found.
        """
        return self.project_settings.get(key)

    def set_project_setting(self, key: str, value):
        """Sets the value of a project setting and saves to disk.

        Args:
            key (str): The key of the setting to set.
            value: The new value of the setting.
        """
        self.project_settings[key] = value
        self._save_settings(self.project_settings_file, self.project_settings)

    def get(self, key: str, default=None):
        """Gets a setting value, checking project settings first.

        If the key is not found in the project-specific settings, it falls
        back to the global application settings.

        Args:
            key (str): The key of the setting to retrieve.
            default: The value to return if the key is not found anywhere.
                     Defaults to None.

        Returns:
            The value of the setting.
        """
        if self.project_settings and key in self.project_settings:
            return self.project_settings[key]
        return self.app_settings.get(key, default)

    def set(self, key: str, value, is_project_specific: bool = False):
        """Sets a setting value, either for the project or the application.

        Args:
            key (str): The key of the setting to set.
            value: The new value of the setting.
            is_project_specific (bool): If True, sets the setting for the
                current project. Otherwise, sets it globally for the
                application. Defaults to False.
        """
        if is_project_specific:
            self.set_project_setting(key, value)
        else:
            self.set_app_setting(key, value)

    def add_recent_project(self, project_path: str):
        """Adds a project to the list of recent projects.

        This method ensures the list of recent projects does not contain
        duplicates and maintains a fixed size. The most recently opened
is
        at the top.

        Args:
            project_path (str): The path to the project to add.
        """
        recent = self.get_app_setting("recent_projects")
        if project_path in recent:
            recent.remove(project_path)
        recent.insert(0, project_path)
        # Keep the list at a reasonable size, e.g., 10 projects
        self.set_app_setting("recent_projects", recent[:10])

    def remove_recent_project(self, project_path: str):
        """Removes a project from the list of recent projects.

        Args:
            project_path (str): The path to the project to remove.
        """
        recent = self.get_app_setting("recent_projects")
        if project_path in recent:
            recent.remove(project_path)
            self.set_app_setting("recent_projects", recent)
