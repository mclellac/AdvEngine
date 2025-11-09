"""A factory for creating GObject wrappers for dataclasses."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject
import json


def create_gobject_wrapper(dataclass_type):
    """Dynamically creates a GObject wrapper for a given dataclass."""

    class_name = f"{dataclass_type.__name__}GObject"

    properties = {}
    for name, type_hint in dataclass_type.__annotations__.items():
        if type_hint == int:
            properties[name] = GObject.Property(type=int, default=0)
        elif type_hint == bool:
            properties[name] = GObject.Property(type=bool, default=False)
        elif type_hint == str:
            properties[name] = GObject.Property(type=str, default="")
        elif type_hint == dict:
            properties[name] = GObject.Property(type=str, default="{}")
        else:
            properties[name] = GObject.Property(type=str, default="")

    def __init__(self, instance):
        GObject.Object.__init__(self)
        self.instance = instance
        for prop in self.list_properties():
            prop_name = prop.name.replace("-", "_")
            if hasattr(instance, prop_name):
                value = getattr(instance, prop_name)
                if isinstance(value, dict):
                    value = json.dumps(value)
                setattr(self, prop_name, value)
        self.connect("notify", self._on_property_changed)

    def _on_property_changed(self, obj, pspec):
        py_attr_name = pspec.name.replace("-", "_")
        if hasattr(self.instance, py_attr_name):
            value = getattr(self, py_attr_name)
            if isinstance(getattr(self.instance, py_attr_name), dict):
                value = json.loads(value)
            setattr(self.instance, py_attr_name, value)

    new_class = type(
        class_name,
        (GObject.Object,),
        {
            "__gtype_name__": class_name,
            "__init__": __init__,
            "_on_property_changed": _on_property_changed,
            **properties,
        },
    )

    return new_class
