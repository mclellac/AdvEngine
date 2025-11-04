pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'advengine'
gnome = import('gnome')

gnome.compile_resources('advengine',
  'advengine.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'advengine.in',
  output: 'advengine',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

advengine_sources = [
  '__init__.py',
  'main.py',
  'core/__init__.py',
  'core/data_schemas.py',
  'core/project_manager.py',
  'core/settings_manager.py',
  'core/ue_exporter.py',
  'ui/attribute_editor.py',
  'ui/__init__.py',
  'ui/item_editor.py',
  'ui/module_assets.py',
  'ui/module_audio.py',
  'ui/module_character.py',
  'ui/module_cutscene.py',
  'ui/module_dialogue.py',
  'ui/module_font.py',
  'ui/module_interaction.py',
  'ui/module_logic.py',
  'ui/module_log.py',
  'ui/module_quest.py',
  'ui/module_scene.py',
  'ui/module_state.py',
  'ui/module_ui_builder.py',
  'ui/preferences.py',
  'ui/search_results.py',
  'ui/shortcuts.py',
  'ui/verb_editor.py',
  'ui/widgets'
]

install_data(advengine_sources, install_dir: moduledir)
