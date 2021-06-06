# Import Dependencies
import gi
from gi.repository import Gtk
from cairo import Context
from parsers.file_obj import FileOBJ
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
    file_obj = FileOBJ.from_path("example/objects/african_head.obj")
    # Define Signals
    @Gtk.Template.Callback("on-canvas-draw")
    def on_canvas_draw(self, widget: Gtk, ctx: Context):
        viewport = widget.get_allocation()
        # Clear Screen
        ctx.set_source_rgb(0, 0, 0)
        ctx.rectangle(0, 0 , viewport.width, viewport.height)
        ctx.fill()
        # Print New Screen
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(1)
        # Draw Wireframe
        for face in self.file_obj.faces:
            face_l = list(face)
            for i in range(3):
                v0 = self.file_obj.vertices[face_l[i]]
                v1 = self.file_obj.vertices[face_l[(i+1) % 3]]
                x0 = (v0.x + 1) * viewport.width / 2
                x1 = (v1.x + 1) * viewport.width / 2
                y0 = (v0.y + 1) * viewport.height / 2
                y1 = (v1.y + 1) * viewport.height / 2
                ctx.move_to(x0, viewport.height - y0)
                ctx.line_to(x1, viewport.height - y1)
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