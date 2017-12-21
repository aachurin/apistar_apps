from apistar_apps import AppLoader
from apistar.frameworks.wsgi import WSGIApp


app = AppLoader(WSGIApp)


if __name__ == '__main__':
    app.main()
