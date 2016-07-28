from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['numpy', 'pygame', 'requests', 'xml', 'Tkinter'], 
                    excludes = [], 
                    include_files = ['rexlia rg.ttf', 'full Pack 2025.ttf', 'settingsManager.py',
                                     'battle.py', 'main.py', 'musicManager.py', 'spriteManager.py',
                                     'engine/', 'fighters/', 'menu/', 'music/', 'settings/', 'sfx/',
                                     'builder/', 'sprites/', 'stages/', 'cacert.pem', 'editor.ico',
                                     'editor.xbm'])

base_b = None
if sys.platform == "win32":
    base_b = "Win32GUI"

executables = [
    Executable('main.py', base = base_b, targetName = 'TUSSLE.exe', icon='tussle.ico'),
    Executable('updater.py', 'console', targetName = 'updater.exe'),
    Executable('builderMain.py', base = base_b, targetName='LegacyEditor.exe', icon='editor.ico')
]

setup(name='TUSSLE',
      version = '0.5',
      description = 'The Universal Smash System and Legacy Editor',
      options = dict(build_exe = buildOptions),
      executables = executables)
