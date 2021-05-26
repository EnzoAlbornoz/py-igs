# Import Dependencies
import gi
from gi.repository import Gtk
# Setup Graphic
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
# Define Window
@Gtk.Template(filename="resources/interface/application.glade")
class ApplicationWindow(Gtk.ApplicationWindow):
    # Define Mount Point
    __gtype_name__ = "window-root"
    # Define Handlers
    widget_logger = Gtk.Template.Child("widget-logger-content")
    widget_logger_scroll = Gtk.Template.Child("widget-logger-historic")
    # Define Utility Functions
    def console_log(self, message):
        # Load Console Buffer
        buffer = self.widget_logger.get_buffer()
        # Insert Message in Buffer
        buffer.insert_at_cursor(f"{message}\n")
        # Scroll Down Console
        adjustment = self.widget_logger_scroll.get_vadjustment()
        v_adjust_to = adjustment.get_upper() - adjustment.get_page_size()
        adjustment.set_value(v_adjust_to)