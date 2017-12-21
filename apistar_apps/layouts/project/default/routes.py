from apistar import Include


urls = [
    # Now you can include routes using path string.
    # In this case all routes must be in `urls`.
    Include('/', 'welcome.routes')
]
