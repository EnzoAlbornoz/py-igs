# Import Dependencies
import gi
from gi.repository import Gtk
from cairo import Context
# Setup Graphic
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
# Define Window
@Gtk.Template(filename="resources/interface/application.glade")
class ApplicationWindow(Gtk.ApplicationWindow):
    # Define Mount Point
    __gtype_name__ = "window-root"
    # Define Attributes
    widget_logger = Gtk.Template.Child("widget-logger-content")
    widget_logger_scroll = Gtk.Template.Child("widget-logger-historic")
    # Define Signals
    @Gtk.Template.Callback("on-canvas-draw")
    def on_canvas_draw(self, widget: Gtk, ctx: Context):
        viewport = widget.get_allocation()
        print(f"[{viewport.width}x{viewport.height}] at [{viewport.x},{viewport.y}]")
        # print(rec)
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(2)
        ctx.move_to(0, 0)
        ctx.line_to(200, 200)
        ctx.stroke()
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