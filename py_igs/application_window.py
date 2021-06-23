# Import Dependencies
import gi
from sys import float_info
from enum import IntEnum, auto, unique
from gi.repository import Gtk, Gdk
from cairo import Context
from helpers import extract_points_as_vec2_from_box
from objects.line_2d import Line2D
from objects.point_2d import Point2D
from objects.wireframe_2d import Wireframe2D
from primitives.display_file import DisplayFile
from primitives.matrix import Matrix
from primitives.vec2 import Vector2
from primitives.viewport import Viewport
from primitives.window import Window
# Setup Graphic
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
# Define Constants
@unique
class DialogObjectType(IntEnum):
    POINT = 0
    LINE = 1
    WIREFRAME = 2
# Define Window
@Gtk.Template(filename="resources/interface/application.glade")
class ApplicationWindow(Gtk.ApplicationWindow):
    # Define Mount Point
    __gtype_name__ = "window-root"
    # Define Widgets
    widget_logger = Gtk.Template.Child("widget-logger-content")
    widget_logger_scroll = Gtk.Template.Child("widget-logger-historic")
    widget_canvas = Gtk.Template.Child("viewport-canvas")
    widget_objects_tree = Gtk.Template.Child("widget-objects-view")
    widget_objects_actions_remove = Gtk.Template.Child("widget-objects-actions-remove")
    widget_objects_actions_edit = Gtk.Template.Child("widget-objects-actions-edit")
    # Define Dialogs
    dialog_object_add = Gtk.Template.Child("window-object-add")
    dialog_object_add_object_name = Gtk.Template.Child("window-object-add-name-entry")
    dialog_object_add_tab_point_coords = Gtk.Template.Child("window-object-add-point-coords")
    dialog_object_add_tab_line_coords = Gtk.Template.Child("window-object-add-line-coords")
    dialog_object_add_tab_wireframe_coords = Gtk.Template.Child("window-object-add-wireframe-coords")
    dialog_object_add_btn_save = Gtk.Template.Child("window-object-add-btn-save")

    dialog_about = Gtk.Template.Child("window-about")
    # Global Attributes
    g_nav_adjustment_zoom = Gtk.Template.Child("g-widget-navigation-nav-adjustment-zoom")
    g_nav_adjustment_pan = Gtk.Template.Child("g-widget-navigation-nav-adjustment-pan")
    g_tree_objects_store = Gtk.Template.Child("g-widget-objects-tree-store")
    # Define Constructor
    def __init__(self, *args, **kwargs) -> None:
        # Call Super Constructor
        super().__init__(*args, **kwargs)
        # Add Attributes
        self.viewport = None
        self.display_file = DisplayFile()
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
        # Sync Tree Store with Display File
        self.sync_object_tree()
        # Define Variable to Handle Tree Select
        self.selected_object_name = None
        # Define Variables to Handle New Objects
        self.add_object_current_type_page = None
        self.add_object_current_type = None
        self.add_object_wireframe_extra_points = []
    # Define Sync Functions
    def sync_object_tree(self):
        # Clear Object Store
        self.g_tree_objects_store.clear()
        # Append all objects again
        for object_name, object_type, *_ in self.display_file.get_objects():
            self.g_tree_objects_store.append((object_name, f"{object_type}"))
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
        self.viewport.draw(ctx, self.display_file)
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
        # Log
        self.console_log(f"[Navigation] Moved {pan_step} to top")
    @Gtk.Template.Callback("on-btn-clicked-move-down")
    def on_btn_clicked_move_down(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Down
        self.viewport.window.pan(0, -pan_step)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Moved {pan_step} to bottom")
    @Gtk.Template.Callback("on-btn-clicked-move-left")
    def on_btn_clicked_move_left(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Left
        self.viewport.window.pan(-pan_step, 0)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Moved {pan_step} to left")
    @Gtk.Template.Callback("on-btn-clicked-move-right")
    def on_btn_clicked_move_right(self, _button):
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Right
        self.viewport.window.pan(pan_step, 0)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Moved {pan_step} to right")

    # Zoom Handlers
    @Gtk.Template.Callback("on-btn-clicked-zoom-in")
    def on_btn_clicked_zoom_in(self, _button):
        # Get Zoom Diff
        adjustment_ammount = self.g_nav_adjustment_zoom.get_value()
        zoom_ammount = (adjustment_ammount / 100)
        # Zoom In
        self.viewport.window.scale(1 - zoom_ammount)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Zoomed in {adjustment_ammount}%")
    @Gtk.Template.Callback("on-btn-clicked-zoom-out")
    def on_btn_clicked_zoom_out(self, _button):
        # Get Zoom Diff
        adjustment_ammount = self.g_nav_adjustment_zoom.get_value()
        zoom_ammount = (adjustment_ammount / 100)
        # Zoom Out
        self.viewport.window.scale(1 + zoom_ammount)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Zoomed out {adjustment_ammount}%")
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

    # Handle Widget Objects Row
    @Gtk.Template.Callback("on-widget-objects-row-selected") 
    def on_widget_objects_row_selected(self, tree, path, column):
        # Enable click on buttons if they are disable
        if not self.widget_objects_actions_remove.get_sensitive():
            self.widget_objects_actions_remove.set_sensitive(True)
        # if not self.widget_objects_actions_edit.get_sensitive():
        #     self.widget_objects_actions_edit.set_sensitive(True)
        # Get Selected Object Name
        list_iter = self.g_tree_objects_store.get_iter(path)
        (selected_name, *_) = self.g_tree_objects_store.get(list_iter, 0)
        # Save Object Name
        self.selected_object_name = selected_name
    
    @Gtk.Template.Callback("on-widget-objects-actions-remove-clicked") 
    def on_widget_objects_actions_remove_clicked(self, _button):
        # Check Double Delete
        if self.selected_object_name is None:
            self.widget_objects_actions_remove.set_sensitive(False)
            return
        # Remove Selected Item from Display File
        object_name = self.selected_object_name
        self.display_file.remove_object(object_name)
        self.selected_object_name = None
        # Remove Selected Item from TreeView
        self.sync_object_tree()
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Display File] Removed {object_name} from display file")
    # Handle Objects Actions
    @Gtk.Template.Callback("on-dialog-objects-delete-event")
    def on_dialog_objects_delete_event(self, dialog, _event):
        # Hide Window
        dialog.hide()
        # Do Not Destroy
        return True

    @Gtk.Template.Callback("on-btn-clicked-objects-add")
    def on_btn_clicked_objects_add(self, _button):
        # Reset Tabs Values
        for box_coords in self.dialog_object_add_tab_point_coords.get_children():
            # Filter Buttons inside Box
            for box_coords_element in box_coords.get_children():
                if isinstance(box_coords_element, Gtk.SpinButton):
                    # Configure Buttons
                    box_coords_element_adjustment = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
                    box_coords_element.set_adjustment(box_coords_element_adjustment)
                    box_coords_element.set_numeric(True)
        for box_coords in self.dialog_object_add_tab_line_coords.get_children():
            # Filter Buttons inside Box
            for box_coords_element in box_coords.get_children():
                if isinstance(box_coords_element, Gtk.SpinButton):
                    # Configure Buttons
                    box_coords_element_adjustment = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
                    box_coords_element.set_adjustment(box_coords_element_adjustment)
                    box_coords_element.set_numeric(True)
        for box_coords in self.dialog_object_add_tab_wireframe_coords.get_children():
            # Filter Buttons inside Box
            for box_coords_element in box_coords.get_children():
                if isinstance(box_coords_element, Gtk.SpinButton):
                    # Configure Buttons
                    box_coords_element_adjustment = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
                    box_coords_element.set_adjustment(box_coords_element_adjustment)
                    box_coords_element.set_numeric(True)
        # Reset Text
        self.dialog_object_add_object_name.set_text("")
        # Set Default Settings
        if self.add_object_current_type is None:
            self.add_object_current_type = DialogObjectType.POINT
        self.add_object_current_type_page = self.dialog_object_add_tab_point_coords
        # Show Dialog
        self.dialog_object_add.show()
    
    @Gtk.Template.Callback("on-notebook-page-change-object-type")
    def on_notebook_page_change_object_type(self, _notebook, page, page_num):
        # Save Selected Page
        self.add_object_current_type_page = page
        # Save Selected Type Too
        self.add_object_current_type = DialogObjectType(page_num)

    @Gtk.Template.Callback("on-btn-add-objects-cancel")
    def on_btn_add_objects_cancel(self, _button):
        # Hide Window
        self.dialog_object_add.hide()
        # Emit Response
        self.dialog_object_add.response(Gtk.ResponseType.CANCEL)

    
    @Gtk.Template.Callback("on-btn-add-objects-add")
    def on_btn_add_objects_add(self, _button):
        # Hide Window
        self.dialog_object_add.hide()
        # Emit Response
        self.dialog_object_add.response(Gtk.ResponseType.OK)

    @Gtk.Template.Callback("on-dialog-add-objects-response")
    def on_dialog_add_objects_response(self, _dialog, response_id):
        # Ignore if canceling
        if response_id == Gtk.ResponseType.OK:
            # Define Object to Add
            object_to_build = None
            # Check Type of Page
            if self.add_object_current_type == DialogObjectType.POINT:
                # Get Points
                [point_vec2] = extract_points_as_vec2_from_box(self.dialog_object_add_tab_point_coords)
                # Build Object
                object_to_build = Point2D(point_vec2)
            elif self.add_object_current_type == DialogObjectType.LINE:
                # Get Points
                [point_from, point_to] = extract_points_as_vec2_from_box(self.dialog_object_add_tab_line_coords)
                # Build Object
                object_to_build = Line2D(point_from, point_to)
            elif self.add_object_current_type == DialogObjectType.WIREFRAME:
                # Get Points
                points = extract_points_as_vec2_from_box(self.dialog_object_add_tab_wireframe_coords)
                # Build Object
                object_to_build = Wireframe2D(*points)
            # Get Object Name
            object_name = self.dialog_object_add_object_name.get_text()
            # Add Object to Display File
            self.display_file.add_object(object_name, object_to_build)
            self.sync_object_tree()
            # Log
            self.console_log(f"[Display File] Added {object_name} of type {object_to_build.get_type()} to display file")
        # Clear Extra Fields
        self.dialog_object_add_clear_extra_vertices()

    @Gtk.Template.Callback("on-dialog-object-add-name-entry-changed")
    def on_dialog_object_add_name_entry_changed(self, entry):
        # Check Entry Value
        object_name = entry.get_text()
        if (
            # Check If Name is Valid
            len(object_name) < 1 or
            # Check if Already Exists
            object_name in self.display_file.get_names()
        ):
            self.dialog_object_add_btn_save.set_sensitive(False)
            return
        # Allow Save Button
        self.dialog_object_add_btn_save.set_sensitive(True)

    
    @Gtk.Template.Callback("on-dialog-object-add-btn-add-vertex")
    def on_dialog_object_add_btn_add_vertex(self, _button):
        # Create Vertex Box
        vertex_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 8)
        # Create Labels
        vertex_label_x = Gtk.Label.new("X: ")
        vertex_label_y = Gtk.Label.new("Y: ")
        # Create Spin Button Adjustments
        spin_adjustment_x = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
        spin_adjustment_y = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
        # Create Spin Button
        spin_button_x = Gtk.SpinButton.new(spin_adjustment_x, 1, 0)
        spin_button_y = Gtk.SpinButton.new(spin_adjustment_y, 1, 0)
        # Configure Spins
        spin_button_x.set_numeric(True)
        spin_button_y.set_numeric(True)
        # Add Destroy Button
        vertex_box_idx = len(self.add_object_wireframe_extra_points)
        def destroy_vertex(_button):
            # Remove From List
            self.add_object_wireframe_extra_points.pop(vertex_box_idx)
            # Destroy
            vertex_box.destroy()
        destroy_button = Gtk.Button.new_with_label("🗑")
        destroy_button.connect("clicked", destroy_vertex)
        # Add Children to Box
        vertex_box.pack_start(vertex_label_x, False, True, 0)
        vertex_box.pack_start(spin_button_x, True, True, 0)
        vertex_box.pack_start(vertex_label_y, False, True, 0)
        vertex_box.pack_start(spin_button_y, True, True, 0)
        vertex_box.pack_start(destroy_button, False, True, 0)
        # Add Box to Coords
        self.dialog_object_add_tab_wireframe_coords.pack_start(vertex_box, False, True, 0)
        # Add Box to Extra Points List
        self.add_object_wireframe_extra_points.append(vertex_box)
        # Update Widget
        self.dialog_object_add_tab_wireframe_coords.show_all()

    def dialog_object_add_clear_extra_vertices(self):
        # Destroy Wireframe Extra Points
        for vertex_box in self.add_object_wireframe_extra_points:
            # Destroy Box
            vertex_box.destroy()
        # Clear List Refs
        self.add_object_wireframe_extra_points= []

    # Handle Menu Bar
    @Gtk.Template.Callback("on-global-menu-btn-about")
    def on_global_menu_btn_about(self, _button):
        # Show Dialog
        self.dialog_about.show()

    @Gtk.Template.Callback("on-window-about-delete-event")
    def on_window_about_delete_event(self, dialog, _event):
        # Hide Window
        dialog.hide()
        # Do Not Destroy
        return True

    @Gtk.Template.Callback("on-window-about-btn-close")
    def on_window_about_btn_close(self, _button):
        # Hide Dialog
        self.dialog_about.hide()