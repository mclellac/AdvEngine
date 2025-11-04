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
  'main.py'
]

install_data(advengine_sources, install_dir: moduledir)
install_subdir('core', install_dir: moduledir)
install_subdir('ui', install_dir: moduledir)
