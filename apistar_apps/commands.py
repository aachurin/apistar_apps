import os
import shutil
import apistar_apps
from apistar import exceptions, Command
from apistar.interfaces import Console


PACKAGE_DIR = os.path.dirname(apistar_apps.__file__)
LAYOUTS_DIR = os.path.join(PACKAGE_DIR, 'layouts')


def copy_files(console: Console, source_dir: str, target_dir: str):
    copy_paths = []
    for dir_path, dirs, filenames in os.walk(source_dir):
        dirs[:] = [d for d in dirs if not d.startswith('_')]
        for filename in filenames:
            source_path = os.path.join(dir_path, filename)
            rel_path = os.path.relpath(source_path, source_dir)
            target_path = os.path.join(target_dir, rel_path)
            if os.path.exists(target_path):
                message = 'Project files already exist.'
                raise exceptions.CommandLineError(message)
            copy_paths.append((source_path, target_path))

    for source_path, target_path in sorted(copy_paths):
        console.echo(target_path)
        parent = os.path.dirname(target_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.copy(source_path, target_path)


def copy_layout(console: Console, target_dir: str, layouts_dir: str, layout: str='default'):
    choices = [x for x in os.listdir(layouts_dir)]
    if layout not in choices:
        message = "Invalid layout option. Use %s" % (
            ', '.join('`%s`' % x for x in choices))
        raise exceptions.CommandLineError(message)

    source_dir = os.path.join(layouts_dir, layout)
    copy_files(console, source_dir, target_dir)


def startproject(console: Console, target_dir: str, layout: str='default') -> None:
    """
    Create a new project in TARGET_DIR.

    Args:
      console: The console to write output about file creation.
      target_dir: The directory to use when creating the project.
      layout: Select the project layout to use.
    """

    layouts_dir = os.path.join(LAYOUTS_DIR, 'project')
    copy_layout(console, target_dir, layouts_dir=layouts_dir, layout=layout)


def startapp(console: Console, target_dir: str, layout: str='default') -> None:
    """
    Create a new app in TARGET_DIR.

    Args:
      console: The console to write output about file creation.
      target_dir: The directory to use when creating the app.
      layout: Select the app layout to use.
    """
    layouts_dir = os.path.join(LAYOUTS_DIR, 'app')
    copy_layout(console, target_dir, layouts_dir=layouts_dir, layout=layout)


commands = [Command('startapp', startapp)]
