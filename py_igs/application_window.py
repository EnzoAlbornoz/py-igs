# Import Dependencies
import gi
from gi.repository import Gtk
from cairo import Context
from primitives.viewport import Viewport
from primitives.window import Window
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
    widget_canvas = Gtk.Template.Child("viewport-canvas")
    # file_obj = FileOBJ.from_path("example/objects/african_head.obj")
    # Define Constructor
    def __init__(self, *args, **kwargs) -> None:
        # Call Super Constructor
        super().__init__(*args, **kwargs)
        # Add Attributes
        self.viewport = None
    # Define References Getters and Setters
    def set_viewport(self, viewport: Viewport):
        self.viewport = viewport
    def get_viewport(self) -> Viewport:
        return self.viewport
    @Gtk.Template.Callback("on-canvas-draw")
    def on_canvas_draw(self, _widget, ctx: Context):
        # Clear Screen
        ctx.set_source_rgb(0, 0, 0)
        ctx.rectangle(0, 0 , self.viewport.get_width(), self.viewport.get_height())
        ctx.fill()
        # Print New Screen
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(1)
        # Draw Viewport
        self.viewport.draw(ctx)
        # # Draw Wireframe
        # for face in self.file_obj.faces:
        #     face_l = list(face)
        #     for i in range(3):
        #         v0 = self.file_obj.vertices[face_l[i]]
        #         v1 = self.file_obj.vertices[face_l[(i+1) % 3]]
        #         x0 = (v0.x + 1) * viewport.width / 2
        #         x1 = (v1.x + 1) * viewport.width / 2
        #         y0 = (v0.y + 1) * viewport.height / 2
        #         y1 = (v1.y + 1) * viewport.height / 2
        #         ctx.move_to(x0, viewport.height - y0)
        #         ctx.line_to(x1, viewport.height - y1)
        #         ctx.stroke()
    # Define Utility Functions
    def console_log(self, message: str):
        # Load Console Buffer
        buffer = self.widget_logger.get_buffer()
        # Insert Message in Buffer
        buffer.insert_at_cursor(f"{message}\n")
        # Scroll Down Console
        adjustment = self.widget_logger_scroll.get_vadjustment()
        v_adjust_to = adjustment.get_upper() - adjustment.get_page_size()
        adjustment.set_value(v_adjust_to)
    # Define Signals
    @Gtk.Template.Callback("on-canvas-configure")
    def on_canvas_configure(self, _widget, event):
        # Resize Viewport
        if self.viewport is None:
            self.viewport = Viewport(0, 0, event.width, event.height)
            self.viewport.set_window(Window(0, 0, event.width, event.height))
        else:
            self.viewport.set_width(event.width, True)
            self.viewport.set_height(event.height, True)
        # Log Operation
        self.console_log(f"[Viewport] Resized to {self.viewport.get_width()}x{self.viewport.get_height()}")
    
    @Gtk.Template.Callback("on-btn-clicked-move-up")
    def on_btn_clicked_move_up(self, _button):
        # Pan Window Down
        self.viewport.window.pan(0, -10)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-down")
    def on_btn_clicked_move_down(self, _button):
        # Pan Window Down
        self.viewport.window.pan(0, 10)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-left")
    def on_btn_clicked_move_left(self, _button):
        # Pan Window Down
        self.viewport.window.pan(10, 0)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-right")
    def on_btn_clicked_move_right(self, _button):
        # Pan Window Down
        self.viewport.window.pan(-10, 0)
        # Force Redraw
        self.widget_canvas.queue_draw()

    @Gtk.Template.Callback("on-btn-clicked-zoom-in")
    def on_btn_clicked_zoom_in(self, _button):
        # Pan Window Down
        self.viewport.window.scale(0.9)
        # Force Redraw
        self.widget_canvas.queue_draw()
    
    @Gtk.Template.Callback("on-btn-clicked-zoom-out")
    def on_btn_clicked_zoom_out(self, _button):
        # Pan Window Down
        self.viewport.window.scale(1.1)
        # Force Redraw
        self.widget_canvas.queue_draw()