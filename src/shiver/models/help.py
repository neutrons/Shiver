import webbrowser


def help_function(context):
    """
    open a browser with the appropriate help page
    """
    if context:
        webbrowser.open("https://neutrons.github.io/Shiver/GUI/")
