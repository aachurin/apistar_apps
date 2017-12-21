## Apistar Apps

Django-like applications and configuration.

### Install

```bash
$ pip install apistar_apps
```

### Create a new project

```bash
$ apistar-apps startproject .
./app.py
./requirements.txt
./routes.py
./settings.py
./welcome/__init__.py
./welcome/routes.py
./welcome/views.py
$ cat settings.py
```

```python
# List of installed applications
INSTALLED_APPS = [
    'welcome',
]

# Routes
ROUTECONF = 'routes.urls'
```

```bash
$ cat routes.py
```

```python
from apistar import Include


urls = [
    # Now you can include routes using path string.
    # In this case all routes must be in `urls` variable.
    Include('/', 'welcome.routes')
]
```

### Create a new application

```bash
$ apistar startapp foobar
foobar/__init__.py
foobar/routes.py
foobar/views.py
```

And modify your `settings.py` and `routes.py` to add new application.

### Components and commands

To automatically load components and commands, create `components.py` and `commands.py` files in your application directory.

```python
# foobar/components.py

...

components = [
    Component(FoobarComponent)
]
```

Update your `settings.py`:

```python
# List of installed applications
INSTALLED_APPS = [
    'apistar_peewee',
    'welcome',
    'foobar',
]

# Routes
ROUTECONF = 'routes.urls'
```