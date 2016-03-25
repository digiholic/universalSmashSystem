from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['numpy', 'pygame'], excludes = [])

executables = [
    Executable('main.py', 'Console', targetName = 'main.exe')
]

setup(name='TUSSLE',
      version = '0.1',
      description = 'The Universal Smash System and Legacy Editor',
      options = dict(build_exe = buildOptions),
      executables = executables)
