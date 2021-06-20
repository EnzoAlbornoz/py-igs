# Import Dependencies
import gi
from gi.repository import Gtk, Gdk
from cairo import Context
from primitives.vec2 import Vector2
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
    # Global Attributes
    g_nav_adjustment_zoom = Gtk.Template.Child("g-widget-navigation-nav-adjustment-zoom")
    g_nav_adjustment_pan = Gtk.Template.Child("g-widget-navigation-nav-adjustment-pan")
    # Define Constructor
    def __init__(self, *args, **kwargs) -> None:
        # Call Super Constructor
        super().__init__(*args, **kwargs)
        # Add Attributes
        self.viewport = None
        # Add Click Support for Canvas
        self.drag_coords = None
        self.widget_canvas.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.BUTTON1_MOTION_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.SCROLL_MASK
        )
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
    
    # Pan Handlers
    @Gtk.Template.Callback("on-btn-clicked-move-up")
    def on_btn_clicked_move_up(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Up
        self.viewport.window.pan(0, pan_step)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-down")
    def on_btn_clicked_move_down(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Down
        self.viewport.window.pan(0, -pan_step)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-left")
    def on_btn_clicked_move_left(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Left
        self.viewport.window.pan(-pan_step, 0)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-right")
    def on_btn_clicked_move_right(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Right
        self.viewport.window.pan(pan_step, 0)
        # Force Redraw
        self.widget_canvas.queue_draw()

    # Zoom Handlers
    @Gtk.Template.Callback("on-btn-clicked-zoom-in")
    def on_btn_clicked_zoom_in(self, _button):
        # Get Zoom Diff
        zoom_ammount = (self.g_nav_adjustment_zoom.get_value() / 100)
        # Zoom In
        self.viewport.window.scale(1 - zoom_ammount)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-zoom-out")
    def on_btn_clicked_zoom_out(self, _button):
        # Get Zoom Diff
        zoom_ammount = (self.g_nav_adjustment_zoom.get_value() / 100)
        # Zoom Out
        self.viewport.window.scale(1 + zoom_ammount)
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-canvas-scroll")
    def on_canvas_scroll(self, _canvas, event):
        # Get Zoom Diff
        zoom_ammount = (self.g_nav_adjustment_zoom.get_value() / 100)
        # Check Zoom Direction
        if event.direction == Gdk.ScrollDirection.UP:
            # Zoom In
            self.viewport.window.scale(1 - zoom_ammount)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            # Zoom Out
            self.viewport.window.scale(1 + zoom_ammount)
        else:
            raise ValueError(f"Scroll direction {event.direction} is not valid!")
        # Force Redraw
        self.widget_canvas.queue_draw()
        

    # Drag Handlers  
    @Gtk.Template.Callback("on-canvas-drag-start")
    def on_canvas_drag_start(self, _canvas, event):
        # Start Capturing Drag Data
        self.drag_coords = Vector2(event.x_root, event.y_root)
        # Get Display
        display = self.get_screen().get_display()
        # Get Cursor
        cursor_grabbing = Gdk.Cursor.new_from_name(display, "grabbing")
        # Hijack Cursor
        seat = display.get_default_seat()
        seat.grab(self.get_window(), Gdk.SeatCapabilities.POINTER, True, cursor_grabbing, event, None, None)
    @Gtk.Template.Callback("on-canvas-drag-end")
    def on_canvas_drag_end(self, _canvas, event):
        # Get Display
        display = self.get_screen().get_display()
        # Stop Grabbing
        seat = display.get_default_seat()
        seat.ungrab()
        # Stop Capturing Drag Data
        self.drag_coords = None
    @Gtk.Template.Callback("on-window-mouse-release")
    def on_window_mouse_release(self, _window, event):
        if not self.drag_coords is None:
            # Pipe Event
            self.on_canvas_drag_end(self.widget_canvas, event)
    @Gtk.Template.Callback("on-canvas-mouse-motion")
    def on_canvas_drag_motion(self, _canvas, event):
        # Check Draging
        if not self.drag_coords is None:
            # Get Event Drag Coords
            drag_coords_event = Vector2(event.x_root, event.y_root)
            # Get Inverse Scale of Viewport and Window
            inverse_scale = self.viewport.get_inverse_scale()
            # Compute Diff
            (diff_x, diff_y) = ((self.drag_coords - drag_coords_event) * inverse_scale).try_into_vec2().as_tuple()
            # Update View
            self.viewport.window.pan(diff_x, -diff_y)
            # Update Drag Coords
            self.drag_coords = drag_coords_event
            # Force Redraw
            self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-window-mouse-motion")
    def on_window_mouse_motion(self, _window, event):
        if not self.drag_coords is None:
            # Pipe Event
            self.on_canvas_drag_motion(self.widget_canvas, event)
    
    # Handle Canvas Enter/Leave
    @Gtk.Template.Callback("on-canvas-mouse-enter")
    def on_canvas_mouse_enter(self, _canvas, _event):
        # Get Display
        display = self.get_screen().get_display()
        # Get Cursor
        cursor_grabbing = Gdk.Cursor.new_from_name(display, "grab")
        # Change Cursor
        self.get_window().set_cursor(cursor_grabbing)
    @Gtk.Template.Callback("on-canvas-mouse-leave")
    def on_canvas_mouse_leave(self, _canvas, _event):
        # Reset Cursor
        self.get_window().set_cursor(None)