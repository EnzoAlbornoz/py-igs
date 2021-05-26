# Initialization File
# Should import main dependencies and create instantiate the application window
# Import Dependencies
import sys
import gi
# Ensure Gi Libraries
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
from gi.repository import Gtk
# Import Components
from application_window import ApplicationWindow
# Define Constants
_APPLICATION_ID="br.ufsc.py-igs"
what_is = lambda obj: print(type(obj), "\n\t"+"\n\t".join(dir(obj)))
# Define Application
class Application(Gtk.Application):
    # Define Constructor -------------------------------------------------------
    def __init__(self, *args, **kwargs):
        # Call Super
        super().__init__(*args, **kwargs, application_id=_APPLICATION_ID)
        self.args = args
        self.kwargs = kwargs
        # Define Attributes
        self.app_window = None
    # Define Lifecycle Handlers ------------------------------------------------
    # Pre-Visible Procedures
    def do_startup(self):
        Gtk.Application.do_startup(self)
    # To Visible Procedures
    def do_activate(self):
        # Create Application Window if does not exists
        if self.app_window is None:
            self.app_window = ApplicationWindow(application=self)
        # Show Application Window to User
        self.app_window.present()
# Define Entrypoint
if __name__ == "__main__":
    # Build Application
    application = Application()
    # Start Application
    application.run(sys.argv)