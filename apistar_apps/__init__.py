import os
import typing
import importlib
from apistar import App, Component, Command, get_current_app
from apistar.types import CommandConfig, RouteConfig
from apistar.exceptions import ConfigurationError
from apistar.core import Include
from apistar.frameworks.cli import CliApp
from . import commands as apps_commands


__all__ = ('AppLoader', )


class LoadedApps(typing.NamedTuple):
    routes: RouteConfig
    commands: CommandConfig
    components: typing.List[Component]
    settings: typing.Dict[str, typing.Any]


def AppLoader(app_class,
              commands: CommandConfig=None,
              components: typing.List[Component]=None,
              settings_module: str='settings') -> App:

    components = list(components or [])
    commands = list(commands or [])

    apps = _load_apps(settings_module)

    return app_class(
        routes=apps.routes,
        settings=apps.settings,
        commands=(commands + apps.commands + apps_commands.commands),
        components=(components + apps.components),
        )


def _is_list_of(list_, class_):
    return isinstance(list_, (list, tuple)) and all(isinstance(x, class_) for x in list_)


def _lookup_classes(module, cls, attr):
    result = getattr(module, attr, None)
    if result is not None:
        return result
    try:
        module = importlib.import_module(module.__name__ + '.' + attr)
        result = getattr(module, attr)
        if result is not None:
            return result
        result = []
        for name in dir(module):
            inst = getattr(module, name)
            if isinstance(inst, cls):
                result.append(inst)
        return result or None
    except ImportError:
        pass


def _load_attr(path):
    try:
        module, attr = path.rsplit('.', 1)
    except ValueError:
        msg = "Invalid path '%s'" % path
        raise ImportError(msg)
    module = importlib.import_module(module)
    return getattr(module, attr, None)


def _populate_routes(routes):
    for route in routes:
        if isinstance(route, Include):
            if isinstance(route.routes, str):
                route.routes = _load_attr(route.routes + '.urls')
                if route.routes is None:
                    msg = "Count not load urls from module '%s'" % route.routes
                    raise ConfigurationError(msg)
            _populate_routes(route.routes)


def _load_apps(settings_module):
    try:
        module = importlib.import_module(settings_module)
    except ImportError:
        msg = "Could not load settings from '%s'" % settings_module
        raise ConfigurationError(msg)

    settings = {
        key: value for key, value in module.__dict__.items()
        if not key.startswith('_')
    }

    apps = settings.get('INSTALLED_APPS', ())

    if not isinstance(apps, (list, tuple)):
        msg = "The 'INSTALLED_APPS' setting must be a list or tuple"
        raise ConfigurationError(msg)

    app_modules = []
    apps_load_hooks = []
    for app in apps:
        try:
            app_module = importlib.import_module(app)
            app_modules.append(app_module)
        except ImportError:
            msg = "Could not load application '%s'" % app
            raise ConfigurationError(msg)
        if hasattr(app_module, 'apps_load_hook') and callable(app_module.apps_load_hook):
            apps_load_hooks.append(app_module.apps_load_hook)

    components = []
    commands = []

    for app_module in app_modules:

        # find components
        app_components = _lookup_classes(app_module, Component, 'components')
        if app_components:
            if not _is_list_of(app_components, Component):
                msg = "Application '%s' is broken (bad list of components)" % app
                raise ConfigurationError(msg)
            components.extend(app_components)

        # find commands
        app_commands = _lookup_classes(app_module, Command, 'commands')
        if app_commands:
            if not _is_list_of(app_commands, Command):
                msg = "Application '%s' is broken (bad list of commands)" % app
                raise ConfigurationError(msg)
            commands.extend(app_commands)

        # run hooks
        for hook in apps_load_hooks:
            hook(app, app_module)

    routeconf = settings.get('ROUTECONF', 'routes.urls')

    msg = "Could not load urls from module '%s'" % routeconf

    try:
        routes = _load_attr(routeconf)
    except ImportError:
        raise ConfigurationError(msg)

    if routes is None:
        raise ConfigurationError(msg)

    _populate_routes(routes)

    return LoadedApps(routes, commands, components, settings)


def main() -> None:
    if os.path.exists('app.py'):
        app = get_current_app()
    else:
        app = CliApp.__new__(CliApp)
        app.BUILTIN_COMMANDS = []
        app.__init__(
            commands=[
                Command('startproject', apps_commands.startproject)
            ]
        )
    app.main()
