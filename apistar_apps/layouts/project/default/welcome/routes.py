from apistar import Include, Route
from . import views

# Create your routes here.
urls = [
    Route('/', 'GET', views.welcome),
]
