# pyright: reportUnknownMemberType=false
# pyright: reportMissingTypeStubs=false
# pyright: reportGeneralTypeIssues=false
# pyright: reportUntypedBaseClass=false
# pyright: reportUntypedBaseClass=false
# pyright: reportUnknownParameterType=false
# pyright: reportUntypedClassDecorator=false
# pyright: reportUntypedFunctionDecorator=false
# Import Dependencies
from typing import Any, List
import gi
from math import fmod, radians
from os import getcwd
from sys import float_info
from functools import reduce
from enum import IntEnum, unique
from gi.repository import Gtk, Gdk
from cairo import Context
from helpers import extract_points_as_vec2_from_box, gdk_rgba_as_tuple, parse_text_into_points_2d
from objects.bspline_2d import BSpline2D
from objects.line_2d import Line2D
from objects.object_type import ObjectType
from objects.point_2d import Point2D
from objects.wireframe_2d import Wireframe2D
from objects.bezier_2d import Bezier2D
from primitives.display_file import DisplayFile
from primitives.graphical_object import GraphicalObject
from primitives.matrix import Vector2, Matrix, homo_coords2_matrix_identity, homo_coords2_matrix_rotate, homo_coords2_matrix_scale, homo_coords2_matrix_translate
from primitives.viewport import Viewport
from primitives.window import Window
from storage.descriptor_obj import DescriptorOBJ
from primitives.clipping_method import EClippingMethod
# Setup Graphic
gi.require_version("Gtk", "3.0")
gi.require_foreign("cairo")
# Define Constants
@unique
class DialogObjectType(IntEnum):
    POINT = 0
    LINE = 1
    WIREFRAME = 2
    WIREFRAME_TEXT = 3
    CURVE_TEXT = 4
@unique
class DialogSceneSaveType(IntEnum):
    SELECT_OBJECT = 0
    SELECT_MATERIAL = 1
# Define Window
@Gtk.Template(filename="resources/interface/application.glade")
class ApplicationWindow(Gtk.ApplicationWindow):
    # Define Mount Point
    __gtype_name__ = "window-root"
    # Define Widgets
    widget_logger: Any = Gtk.Template.Child("widget-logger-content")
    widget_logger_scroll: Any = Gtk.Template.Child("widget-logger-historic")
    widget_canvas: Any = Gtk.Template.Child("viewport-canvas")
    widget_objects_tree: Any = Gtk.Template.Child("widget-objects-view")
    widget_objects_actions_remove: Any = Gtk.Template.Child("widget-objects-actions-remove")
    widget_objects_actions_edit: Any = Gtk.Template.Child("widget-objects-actions-edit")
    widget_nav_btn_move_front: Any = Gtk.Template.Child("nav-btn-move-front")
    widget_nav_btn_move_back: Any = Gtk.Template.Child("nav-btn-move-back")
    # Define Dialogs
    dialog_object_add: Any = Gtk.Template.Child("window-object-add")
    dialog_object_add_object_name: Any = Gtk.Template.Child("window-object-add-name-entry")
    dialog_object_add_object_color: Any = Gtk.Template.Child("window-object-add-color-value")
    dialog_object_add_object_filled: Any = Gtk.Template.Child("window-object-add-filled")
    dialog_object_add_tab_point_coords: Any = Gtk.Template.Child("window-object-add-point-coords")
    dialog_object_add_tab_line_coords: Any = Gtk.Template.Child("window-object-add-line-coords")
    dialog_object_add_tab_wireframe_coords: Any = Gtk.Template.Child("window-object-add-wireframe-coords")
    dialog_object_add_tab_text_coords: Any = Gtk.Template.Child("window-object-add-text-value")
    dialog_object_add_btn_save: Any = Gtk.Template.Child("window-object-add-btn-save")
    dialog_object_add_tab_text_curve_type: Any = Gtk.Template.Child("widget-objects-add-curve-option-type-value")
    dialog_object_add_tab_text_curve_coords: Any = Gtk.Template.Child("widget-objects-add-curve-input-value")

    dialog_object_edit: Any = Gtk.Template.Child("window-object-edit")
    dialog_object_edit_rotate_around_center: Any = Gtk.Template.Child("window-object-edit-rotate-around-center")
    dialog_object_edit_rotate_around_origin: Any = Gtk.Template.Child("window-object-edit-rotate-around-origin")
    dialog_object_edit_rotate_around_point: Any = Gtk.Template.Child("window-object-edit-rotate-around-point")
    dialog_object_edit_rotate_x_value: Any = Gtk.Template.Child("window-object-edit-rotate-x-value")
    dialog_object_edit_rotate_y_value: Any = Gtk.Template.Child("window-object-edit-rotate-y-value")

    dialog_about: Any = Gtk.Template.Child("window-about")

    dialog_scene_loader: Any = Gtk.Template.Child("window-scene-loader")
    dialog_scene_loader_options_filled: Any = Gtk.Template.Child("window-scene-loader-filled")
    dialgo_scene_save: Any = Gtk.Template.Child("window-scene-save")
    # Global Attributes
    g_nav_adjustment_zoom: Any = Gtk.Template.Child("g-widget-navigation-nav-adjustment-zoom")
    g_nav_adjustment_pan: Any = Gtk.Template.Child("g-widget-navigation-nav-adjustment-pan")
    g_nav_adjustment_rotate: Any = Gtk.Template.Child("g-widget-navigation-nav-adjustment-rotation")
    g_tree_objects_store: Any = Gtk.Template.Child("g-widget-objects-tree-store")

    g_adj_dialog_edit_translate_x: Any = Gtk.Template.Child("g-window-object-edit-translate-adjustment-x")
    g_adj_dialog_edit_translate_y: Any = Gtk.Template.Child("g-window-object-edit-translate-adjustment-y")
    g_adj_dialog_edit_rotate_amount: Any = Gtk.Template.Child("g-window-object-edit-rotate-adjustment-amount")
    g_adj_dialog_edit_rotate_around_x: Any = Gtk.Template.Child("g-window-object-edit-rotate-around-adjustment-x")
    g_adj_dialog_edit_rotate_around_y: Any = Gtk.Template.Child("g-window-object-edit-rotate-around-adjustment-y")
    g_adj_dialog_edit_scale_x: Any = Gtk.Template.Child("g-window-object-edit-scale-adjustment-x")
    g_adj_dialog_edit_scale_y: Any = Gtk.Template.Child("g-window-object-edit-scale-adjustment-y")
    g_adj_dialog_edit_transform_list: Any = Gtk.Template.Child("g-window-object-edit-transformations-list")
    # Define Constructor
    def __init__(self, *args, **kwargs) -> None:
        # Call Super Constructor
        super().__init__(*args, **kwargs)
        # Add Attributes
        self.viewport = None
        self.viewport_margin = 20
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
        self.add_object_filled = False
        # Define Variable to Handle Object Editing
        self.edit_object_transform_list: List[Matrix] = []
        # Init White Color
        self.add_object_current_color = Gdk.RGBA()
        # Define Variables to Handle Scene Load
        self.scene_file_name = None
        self.material_file_name = None
        self.scene_save_step = None
        # Dimension Config
        self.is_third_dimension = False
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
        # Viewport Check
        if self.viewport is None:
            return
        # Clear Screen
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.rectangle(0, 0 , self.viewport.get_width() + (2 * self.viewport_margin), self.viewport.get_height() + (2 * self.viewport_margin))
        ctx.fill()
        # Print New Screen
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(1)
        # Draw Viewport
        self.viewport.draw(ctx, self.display_file)
        # Draw Outer Viewport
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_width(1)
        ctx.rectangle(self.viewport_margin, self.viewport_margin , self.viewport.get_width(), self.viewport.get_height())
        ctx.stroke()
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
    def on_canvas_configure(self, _widget, event: Any):
        # Resize Viewport
        width = event.width - self.viewport_margin
        height = event.height - self.viewport_margin
        if self.viewport is None:
            half_width = (width / 2)
            half_height = (height / 2)
            self.viewport = Viewport(self.viewport_margin, self.viewport_margin, width , height )
            self.viewport.set_window(Window(-half_width, -half_height, half_width, half_height))
        else:
            self.viewport.set_width(width - self.viewport_margin, True)
            self.viewport.set_height(height - self.viewport_margin, True)
        # Log Operation
        self.console_log(f"[Viewport] Resized to {self.viewport.get_width()}x{self.viewport.get_height()}")
    
    # Pan Handlers
    @Gtk.Template.Callback("on-btn-clicked-move-front")
    def on_btn_clicked_move_front(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Front
        self.viewport.window.move(0, 0, pan_step)
        # Log
        self.console_log(f"[Navigation] Moved {pan_step} to front")
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-back")
    def on_btn_clicked_move_back(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Pan Step
        pan_step = self.g_nav_adjustment_pan.get_value()
        # Pan Window Back
        self.viewport.window.move(0, 0, -pan_step)
        # Log
        self.console_log(f"[Navigation] Moved {pan_step} to back")
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-up")
    def on_btn_clicked_move_up(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        if self.is_third_dimension:
            # Get Rotation Step
            rotation_step = self.g_nav_adjustment_rotate.get_value()
            # Rotate To Right
            self.viewport.window.rotate_vertical(radians(rotation_step))
            # Log
            self.console_log(f"[Navigation] Looked {rotation_step} to top")
        else:
            # Get Pan Step
            pan_step = self.g_nav_adjustment_pan.get_value()
            # Pan Window Right
            self.viewport.window.pan(0, pan_step)
            # Log
            self.console_log(f"[Navigation] Moved {pan_step} to top")
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-down")
    def on_btn_clicked_move_down(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        if self.is_third_dimension:
            # Get Rotation Step
            rotation_step = self.g_nav_adjustment_rotate.get_value()
            # Rotate To Right
            self.viewport.window.rotate_vertical(radians(-rotation_step))
            # Log
            self.console_log(f"[Navigation] Looked {rotation_step} to bottom")
        else:
            # Get Pan Step
            pan_step = self.g_nav_adjustment_pan.get_value()
            # Pan Window Right
            self.viewport.window.pan(0, -pan_step)
            # Log
            self.console_log(f"[Navigation] Moved {pan_step} to bottom")
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-left")
    def on_btn_clicked_move_left(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        if self.is_third_dimension:
            # Get Rotation Step
            rotation_step = self.g_nav_adjustment_rotate.get_value()
            # Rotate To Right
            self.viewport.window.rotate_horizontal(radians(-rotation_step))
            # Log
            self.console_log(f"[Navigation] Looked {rotation_step} to left")
        else:
            # Get Pan Step
            pan_step = self.g_nav_adjustment_pan.get_value()
            # Pan Window Right
            self.viewport.window.pan(-pan_step, 0)
            # Log
            self.console_log(f"[Navigation] Moved {pan_step} to left")
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-move-right")
    def on_btn_clicked_move_right(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        if self.is_third_dimension:
            # Get Rotation Step
            rotation_step = self.g_nav_adjustment_rotate.get_value()
            # Rotate To Right
            self.viewport.window.rotate_horizontal(radians(rotation_step))
            # Log
            self.console_log(f"[Navigation] Looked {rotation_step} to right")
        else:
            # Get Pan Step
            pan_step = self.g_nav_adjustment_pan.get_value()
            # Pan Window Right
            self.viewport.window.pan(pan_step, 0)
            # Log
            self.console_log(f"[Navigation] Moved {pan_step} to right")
        # Force Redraw
        self.widget_canvas.queue_draw()

    # Zoom Handlers
    @Gtk.Template.Callback("on-btn-clicked-zoom-in")
    def on_btn_clicked_zoom_in(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Zoom Diff
        adjustment_ammount = self.g_nav_adjustment_zoom.get_value()
        zoom_ammount = 1 - (adjustment_ammount / 100)
        # Zoom In
        self.viewport.window.scale(zoom_ammount, zoom_ammount)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Zoomed in {adjustment_ammount}%")
    @Gtk.Template.Callback("on-btn-clicked-zoom-out")
    def on_btn_clicked_zoom_out(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Zoom Diff
        adjustment_ammount = self.g_nav_adjustment_zoom.get_value()
        zoom_ammount = 1 + (adjustment_ammount / 100)
        # Zoom Out
        self.viewport.window.scale(zoom_ammount, zoom_ammount)
        # Force Redraw
        self.widget_canvas.queue_draw()
        # Log
        self.console_log(f"[Navigation] Zoomed out {adjustment_ammount}%")
    @Gtk.Template.Callback("on-canvas-scroll")
    def on_canvas_scroll(self, _canvas, event):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Zoom Diff
        zoom_ammount = (self.g_nav_adjustment_zoom.get_value() / 100)
        # Check Zoom Direction
        if event.direction == Gdk.ScrollDirection.UP:
            # Zoom In
            self.viewport.window.scale(1 - zoom_ammount, 1 - zoom_ammount)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            # Zoom Out
            self.viewport.window.scale(1 + zoom_ammount, 1 + zoom_ammount)
        else:
            raise ValueError(f"Scroll direction {event.direction} is not valid!")
        # Force Redraw
        self.widget_canvas.queue_draw()

    # Rotation Handlers
    @Gtk.Template.Callback("on-btn-clicked-rotate-counterclockwise")
    def on_btn_clicked_rotate_counterclockwise(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Rotation Ammount
        rotation_value = self.g_nav_adjustment_rotate.get_value()
        # Rotate Right
        self.viewport.window.rotate(radians(-rotation_value))
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-clicked-rotate-clockwise")
    def on_btn_clicked_rotate_clockwise(self, _button):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Get Rotation Ammount
        rotation_value = self.g_nav_adjustment_rotate.get_value()
        # Rotate Left
        self.viewport.window.rotate(radians(rotation_value))
        # Force Redraw
        self.widget_canvas.queue_draw()
    @Gtk.Template.Callback("on-btn-change-dimensions")
    def on_btn_change_dimensions(self, button):
        # Update Values
        self.is_third_dimension = not self.is_third_dimension
        # Update Side Effects
        button.set_label("3D" if self.is_third_dimension else "2D")
        self.widget_nav_btn_move_front.set_sensitive(self.is_third_dimension)
        self.widget_nav_btn_move_back.set_sensitive(self.is_third_dimension)

    # Drag Handlers  
    @Gtk.Template.Callback("on-canvas-drag-start")
    def on_canvas_drag_start(self, _canvas, event: Any):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Start Capturing Drag Data
        self.drag_coords = Vector2(event.x_root, event.y_root)
        # Get Display
        display: Any = self.get_screen().get_display()
        # Get Cursor
        cursor_grabbing: Any = Gdk.Cursor.new_from_name(display, "grabbing")
        # Hijack Cursor
        seat = display.get_default_seat()
        seat.grab(self.get_window(), Gdk.SeatCapabilities.POINTER, True, cursor_grabbing, event, None, None)
    @Gtk.Template.Callback("on-canvas-drag-end")
    def on_canvas_drag_end(self, _canvas, event):
        # Get Display
        display: Any = self.get_screen().get_display()
        # Stop Grabbing
        seat = display.get_default_seat()
        seat.ungrab()
        # Stop Capturing Drag Data
        self.drag_coords = None
    @Gtk.Template.Callback("on-window-mouse-release")
    def on_window_mouse_release(self, _window, event: Any):
        if not self.drag_coords is None:
            # Pipe Event
            self.on_canvas_drag_end(self.widget_canvas, event)
    @Gtk.Template.Callback("on-canvas-mouse-motion")
    def on_canvas_drag_motion(self, _canvas, event: Any):
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Check Draging
        if not self.drag_coords is None:
            # Get Event Drag Coords
            drag_coords_event = Vector2(event.x_root, event.y_root)
            # Check if need to use 3D Commands
            if self.is_third_dimension and self.viewport is not None and self.viewport.window is not None:
                # Compute Diff
                (diff_x, diff_y) = (self.drag_coords - drag_coords_event).try_into_vec2().as_tuple()
                # Define Sensitivity
                MOUSE_SENSITIVITY = 15
                # Compute Percentage
                percentage_horizontal = diff_x / 180 * MOUSE_SENSITIVITY
                percentage_vertical = diff_y / 180 * MOUSE_SENSITIVITY
                # Rotate
                self.viewport.window.rotate_vertical(radians(percentage_vertical))
                self.viewport.window.rotate_horizontal(radians(percentage_horizontal))
            else:
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
        display: Any = self.get_screen().get_display()
        # Get Cursor
        cursor_grabbing: Any = Gdk.Cursor.new_from_name(display, "grab")
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
        if not self.widget_objects_actions_edit.get_sensitive():
            self.widget_objects_actions_edit.set_sensitive(True)
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
            self.widget_objects_actions_edit.set_sensitive(False)
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

    # Handle Window Widget Change
    @Gtk.Template.Callback("on-clip-method-change")
    def on_clip_method_change(self, select_button):
        # Get Value From Button
        tree_iter: int = select_button.get_active_iter()
        clip_method: str = select_button.get_model()[tree_iter][1]
        clip_method = EClippingMethod(int(clip_method))
        # Check Viewport and Window
        if self.viewport is None or self.viewport.window is None:
            return
        # Update Clip Methods - Point
        self.viewport.window.cliping_methods[ObjectType.POINT_2D] = (
            clip_method if clip_method is EClippingMethod.NONE else EClippingMethod.POINT_CLIP
        )
        # Line
        self.viewport.window.cliping_methods[ObjectType.LINE_2D] = clip_method
        self.viewport.window.cliping_methods[ObjectType.BEZIER_2D] = clip_method
        # Wireframes
        self.viewport.window.cliping_methods[ObjectType.WIREFRAME_2D] = (
            EClippingMethod.POLY_WEILER_ATHERTON_WITH_CS
            if clip_method is EClippingMethod.LINE_COHEN_SUTHERLAND
            else EClippingMethod.POLY_WEILER_ATHERTON_WITH_LB
            if clip_method is EClippingMethod.LINE_LIANG_BARSKY
            else EClippingMethod.NONE
        )
        # Force Redraw
        self.widget_canvas.queue_draw()        
    
    # Handle Objects Actions
    @Gtk.Template.Callback("on-dialog-add-objects-delete-event")
    def on_dialog_objects_delete_event(self, _dialog, _event):
        # Hide Window
        self.dialog_object_add.hide()
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
                    box_coords_element_adjustment: Any = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
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
        self.dialog_object_add_tab_text_coords.set_text("")
        self.dialog_object_add_tab_text_curve_coords.set_text("")
        # Reset Color
        color_white: Any = Gdk.RGBA()
        self.dialog_object_add_object_color.set_rgba(color_white)
        self.add_object_current_color = color_white
        # Set Default Settings
        if self.add_object_current_type is None:
            self.add_object_current_type = DialogObjectType.POINT
        self.add_object_current_type_page = self.dialog_object_add_tab_point_coords
        self.add_object_filled = False
        self.dialog_object_add_object_filled.set_active(False)

        # Show Dialog
        self.dialog_object_add.show()
    
    @Gtk.Template.Callback("on-notebook-page-change-object-type")
    def on_notebook_page_change_object_type(self, _notebook, page, page_num: int):
        # Save Selected Page
        self.add_object_current_type_page = page
        # Save Selected Type Too
        self.add_object_current_type = DialogObjectType(page_num)

    @Gtk.Template.Callback("on-object-add-color-set")
    def on_object_add_color_set(self, button):
        # Get Color From Button
        self.add_object_current_color = button.get_rgba()

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
    def on_dialog_add_objects_response(self, dialog, response_id):
        # Ignore if canceling
        if response_id == Gtk.ResponseType.OK:
            # Define Object to Add
            object_to_build: GraphicalObject = None
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
                # Fill If Selected
                object_to_build.set_filled(self.add_object_filled)
            elif self.add_object_current_type is DialogObjectType.WIREFRAME_TEXT:
                # Get Text
                points_text = self.dialog_object_add_tab_text_coords.get_text()
                # Get Points
                points = parse_text_into_points_2d(points_text)
                # Check Object to Build
                points_len = len(points)
                if points_len == 1:
                    # Its a Point
                    object_to_build = Point2D(*points)
                elif points_len == 2:
                    # Its a Line
                    object_to_build = Line2D(*points)
                elif points_len >= 3:
                    # Its a Wireframe
                    object_to_build = Wireframe2D(*points)
                    # Fill If Selected
                    object_to_build.set_filled(self.add_object_filled)
                else:
                    # Error
                    return
            elif self.add_object_current_type is DialogObjectType.CURVE_TEXT:
                # Get Text
                points_text = self.dialog_object_add_tab_text_curve_coords.get_text()
                # Define Type
                # Get Value From Button
                tree_iter: int = self.dialog_object_add_tab_text_curve_type.get_active_iter()
                curve_type_str: str = self.dialog_object_add_tab_text_curve_type.get_model()[tree_iter][1]
                curve_type = ObjectType(int(curve_type_str))
                # Get Points
                points = parse_text_into_points_2d(points_text)
                # Check Object to Build
                if curve_type == ObjectType.BEZIER_2D:
                    # Its a Point
                    object_to_build = Bezier2D(0.01, *points)
                elif curve_type == ObjectType.BSPLINE_2D:
                    # Its a Line
                    object_to_build = BSpline2D(0.01, *points)
            # Get Object Name
            object_name = self.dialog_object_add_object_name.get_text()
            # Get Object Color
            object_color = gdk_rgba_as_tuple(self.add_object_current_color)
            object_to_build.set_color(object_color)
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
        object_name: str = entry.get_text()
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

    @Gtk.Template.Callback("on-window-object-add-filled")
    def on_window_object_add_filled(self, check_button):
        # Get Value
        is_active: bool = check_button.get_active()
        # Update Control
        self.add_object_filled = is_active

    
    @Gtk.Template.Callback("on-dialog-object-add-btn-add-vertex")
    def on_dialog_object_add_btn_add_vertex(self, _button):
        # Create Vertex Box
        vertex_box: Any = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 8)
        # Create Labels
        vertex_label_x: Any = Gtk.Label.new("X: ")
        vertex_label_y: Any = Gtk.Label.new("Y: ")
        # Create Spin Button Adjustments
        spin_adjustment_x: Any = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
        spin_adjustment_y: Any = Gtk.Adjustment.new(0, -float_info.max, float_info.max, 1, 10, 0)
        # Create Spin Button
        spin_button_x: Any = Gtk.SpinButton.new(spin_adjustment_x, 1, 0)
        spin_button_y: Any = Gtk.SpinButton.new(spin_adjustment_y, 1, 0)
        # Configure Spins
        spin_button_x.set_numeric(True)
        spin_button_y.set_numeric(True)
        # Add Destroy Button
        def destroy_vertex(_button):
            # Remove From List
            self.add_object_wireframe_extra_points.remove(vertex_box)
            # Destroy
            vertex_box.destroy()
        destroy_button: Any = Gtk.Button.new_with_label("🗑")
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
        self.add_object_wireframe_extra_points: List[Any] = []

    # Handle Menu Bar
    @Gtk.Template.Callback("on-global-menu-btn-about")
    def on_global_menu_btn_about(self, _button):
        # Show Dialog
        self.dialog_about.show()

    @Gtk.Template.Callback("on-window-about-delete-event")
    def on_window_about_delete_event(self, _dialog, _event):
        # Hide Window
        self.dialog_about.hide()
        # Do Not Destroy
        return True

    @Gtk.Template.Callback("on-window-about-btn-close")
    def on_window_about_btn_close(self, _button):
        # Hide Dialog
        self.dialog_about.hide()

    # Objects Edit Handlers
    @Gtk.Template.Callback("on-btn-clicked-objects-edit")
    def on_btn_clicked_objects_edit(self, _button):
        # Check Double Delete
        if self.selected_object_name is None:
            self.widget_objects_actions_remove.set_sensitive(False)
            self.widget_objects_actions_edit.set_sensitive(False)
            return
        # Prepare Fields
        self.g_adj_dialog_edit_translate_x.configure(0, -float_info.max, float_info.max, 1, 10, 0)
        self.g_adj_dialog_edit_translate_y.configure(0, -float_info.max, float_info.max, 1, 10, 0)
        self.g_adj_dialog_edit_rotate_amount.configure(0, -360, 360, 1, 15, 0)
        self.g_adj_dialog_edit_rotate_around_x.configure(0, -float_info.max, float_info.max, 1, 10, 0)
        self.g_adj_dialog_edit_rotate_around_y.configure(0, -float_info.max, float_info.max, 1, 10, 0)
        self.g_adj_dialog_edit_scale_x.configure(0, -float_info.max, float_info.max, 1, 10, 0)
        self.g_adj_dialog_edit_scale_y.configure(0, -float_info.max, float_info.max, 1, 10, 0)
        # Clear Transform List
        self.edit_object_transform_list.clear()
        self.g_adj_dialog_edit_transform_list.clear()
        # Reset Rotation Radio Buttons
        self.dialog_object_edit_rotate_around_origin.set_active(True)
        self.dialog_object_edit_rotate_x_value.set_sensitive(False)
        self.dialog_object_edit_rotate_y_value.set_sensitive(False)
        # Show Dialog
        self.dialog_object_edit.show()

    @Gtk.Template.Callback("on-object-edit-radio-rotate-point-toggled")
    def on_object_edit_radio_rotate_point_toggled(self, radio_button):
        # Disable buttons if not selected
        if not radio_button.get_active():
            self.dialog_object_edit_rotate_x_value.set_sensitive(False)
            self.dialog_object_edit_rotate_y_value.set_sensitive(False)
        else:
            self.dialog_object_edit_rotate_x_value.set_sensitive(True)
            self.dialog_object_edit_rotate_y_value.set_sensitive(True)

    @Gtk.Template.Callback("on-object-edit-radio-rotate-origin-toggled")
    def on_object_edit_radio_rotate_origin_toggled(self, radio_button):
        # Move rotate point to origin
        if radio_button.get_active():
            self.g_adj_dialog_edit_rotate_around_x.set_value(0)
            self.g_adj_dialog_edit_rotate_around_y.set_value(0)

    @Gtk.Template.Callback("on-object-edit-radio-rotate-center-toggled")
    def on_object_edit_radio_rotate_center_toggled(self, radio_button):
        # Move rotate point to object center
        if radio_button.get_active():
            # Get selected object center
            object_center = self.display_file.get_object_ref(self.selected_object_name).get_center_coords()
            current_center_transform = reduce(
                lambda acc_trans, it_trans: acc_trans * it_trans,
                self.edit_object_transform_list,
                homo_coords2_matrix_identity()
            )
            object_center = (object_center.as_vec3(1) * current_center_transform).try_into_vec2()
            # Define rotate point to the object center
            self.g_adj_dialog_edit_rotate_around_x.set_value(object_center.get_x())
            self.g_adj_dialog_edit_rotate_around_y.set_value(object_center.get_y())

    @Gtk.Template.Callback("on-dialog-objects-edit-delete-event")
    def on_dialog_objects_delete_event(self, _dialog, _event):
        # Hide Window
        self.dialog_object_edit.hide()
        # Do Not Destroy
        return True

    @Gtk.Template.Callback("on-btn-edit-objects-cancel")
    def on_btn_edit_objects_cancel(self, _button):
        # Log
        self.console_log(f"[Object Edit] [{self.selected_object_name}] Edition cancelled")
        # Hide Window
        self.dialog_object_edit.hide()
        # Emit Response
        self.dialog_object_edit.response(Gtk.ResponseType.CANCEL)

    @Gtk.Template.Callback("on-btn-edit-objects-save")
    def on_btn_edit_objects_save(self, _button):
        # Hide Window
        self.dialog_object_edit.hide()
        # Emit Response
        self.dialog_object_edit.response(Gtk.ResponseType.OK)

    @Gtk.Template.Callback("on-window-edit-add-translation")
    def on_window_edit_add_translation(self, button):
        # Get Translate Data
        translate_x = self.g_adj_dialog_edit_translate_x.get_value()
        translate_y = self.g_adj_dialog_edit_translate_y.get_value()
        # Add item into to GUI
        self.g_adj_dialog_edit_transform_list.append([
            f"Translate [X: {translate_x}] [Y: {translate_y}]"
        ])
        # Ignore if no translation
        if translate_x == 0 and translate_y == 0:
            return
        # Define Transform
        transform_matrix = homo_coords2_matrix_translate(translate_x, translate_y)
        # Apply Transform
        self.edit_object_transform_list.append(transform_matrix)
        # Log
        self.console_log(f"[Edit] Translated {self.selected_object_name} by {translate_x} units in X and {translate_y} units in Y")
    @Gtk.Template.Callback("on-window-edit-add-rotation")
    def on_window_edit_add_rotation(self, _button):
        # Get Rotation Data
        rotate_degrees = self.g_adj_dialog_edit_rotate_amount.get_value()
        rotate_degrees = fmod(rotate_degrees, 360)
        rotate_point_x = self.g_adj_dialog_edit_rotate_around_x.get_value()
        rotate_point_y = self.g_adj_dialog_edit_rotate_around_y.get_value()
        # Add item into to GUI
        self.g_adj_dialog_edit_transform_list.append([
            f"Rotate [θ: {rotate_degrees}°] [O: ({rotate_point_x},{rotate_point_y})]"
        ])
        # Ignore if no rotation
        if rotate_degrees == 0:
            return
        # Define Transform
        rotation_radians = radians(rotate_degrees)
        # Compute Rotation
        rotation_matrix = homo_coords2_matrix_translate(-rotate_point_x, -rotate_point_y)
        rotation_matrix *= homo_coords2_matrix_rotate(rotation_radians)
        rotation_matrix *= homo_coords2_matrix_translate(rotate_point_x, rotate_point_y)
        # Append Rotation
        self.edit_object_transform_list.append(rotation_matrix)
        # Log
        self.console_log(f"[Edit] Rotated {self.selected_object_name} by {rotate_degrees} around [{rotate_point_x}, {rotate_point_y}]")
    @Gtk.Template.Callback("on-window-edit-add-scaling")
    def on_window_edit_add_scaling(self, _button):
        # Get Scaling Data
        scale_x = self.g_adj_dialog_edit_scale_x.get_value()
        scale_y = self.g_adj_dialog_edit_scale_y.get_value()
        # Add item into to GUI
        self.g_adj_dialog_edit_transform_list.append([f"Scale [X: {scale_x}%] [Y: {scale_y}%]"])
        # Ignore if no Scalling
        if scale_x == 0 and scale_y == 0:
            return
        # Define Transform
        object_center = self.display_file.get_object_ref(self.selected_object_name).get_center_coords().as_vec3(1)
        current_center_transform = reduce(
            lambda acc_trans, it_trans: acc_trans * it_trans,
            self.edit_object_transform_list,
            homo_coords2_matrix_identity()
        )
        object_center *= current_center_transform
        (point_x, point_y) = object_center.try_into_vec2().as_tuple()
        # Compute Scaling
        scale_x = 1 + (scale_x / 100)
        scale_y = 1 + (scale_y / 100)
        scaling_matrix = homo_coords2_matrix_translate(-point_x, -point_y)
        scaling_matrix *= homo_coords2_matrix_scale(scale_x, scale_y)
        scaling_matrix *= homo_coords2_matrix_translate(point_x, point_y)
        # Append Scaling
        self.edit_object_transform_list.append(scaling_matrix)
        # Log
        self.console_log(f"[Edit] Scaled {self.selected_object_name} by {scale_x}% in X and {scale_y}% in Y")

    @Gtk.Template.Callback("on-dialog-edit-objects-response")
    def on_dialog_edit_objects_response(self, _dialog, response_id):
        # Ignore if canceling
        if response_id == Gtk.ResponseType.OK:
            # Skip if no transforms needed
            if len(self.edit_object_transform_list) == 0:
                return
            # Join Transforms
            transforms = reduce(
                lambda acc_trans, it_trans: acc_trans * it_trans,
                self.edit_object_transform_list,
                homo_coords2_matrix_identity()
            )
            # Make Transform
            self.display_file.transform_object_matrix(self.selected_object_name, transforms)
            # Log
            self.console_log(f"[Object Edit] [{self.selected_object_name}] Edition applied")

    # Handle Scene Open
    @Gtk.Template.Callback("on-menu-scene-open")
    def on_menu_scene_open(self, _item):
        # Set Current Directory
        self.dialog_scene_loader.set_current_folder(getcwd())
        # Reset Options
        self.dialog_scene_loader_options_filled.set_active(False)
        # Open File Chooser
        self.dialog_scene_loader.show_all()
    
    @Gtk.Template.Callback("on-window-scene-loader-delete-event")
    def on_window_scene_loader_delete_event(self, _dialog, _event):
        # Response Dialog
        self.dialog_scene_loader.hide()
        # Do Not Destroy
        return True

    @Gtk.Template.Callback("on-window-scene-loader-file-activate")
    def on_window_scene_loader_file_activate(self, _file_chooser):
        # Response Dialog
        self.dialog_scene_loader.response(Gtk.ResponseType.OK)

    @Gtk.Template.Callback("on-window-scene-loader-btn-open")
    def on_window_scene_loader_btn_open(self, _file_chooser):
        # Response Dialog
        self.dialog_scene_loader.response(Gtk.ResponseType.OK)
    
    @Gtk.Template.Callback("on-window-scene-loader-btn-cancel")
    def on_window_scene_loader_btn_cancel(self, _file_chooser):
        # Response Dialog
        self.dialog_scene_loader.response(Gtk.ResponseType.CANCEL)

    @Gtk.Template.Callback("on-window-scene-loader-file-selected")
    def on_window_scene_loader_file_selected(self, file_chooser):
        # Get Selected File
        self.scene_file_name: str = file_chooser.get_filename()
        # Print Filename

    @Gtk.Template.Callback("on-window-scene-loader-response")
    def on_window_scene_loader_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            # Check Viewport and Window
            if self.viewport is None or self.viewport.window is None:
                return
            # Fetch Options
            import_options_filled: bool = self.dialog_scene_loader_options_filled.get_active()
            # Load File
            scene_descriptor = DescriptorOBJ.parseFile(self.scene_file_name, self.viewport.window.get_width(), self.viewport.window.get_height(), import_options_filled)
            # Clear Display File
            self.display_file.clear()
            # Get Window Info
            window_center = scene_descriptor.window_center
            window_width = scene_descriptor.window_width
            window_height = scene_descriptor.window_height
            # Update Window Data
            self.viewport.window.set_width(window_width)
            self.viewport.window.set_height(window_height)
            self.viewport.window.set_center(window_center)
            # Log 
            self.console_log(f"[Window] New Dimensions: {self.viewport.window.get_width()} x {self.viewport.window.get_height()}")
            # Add Files to Display File
            for (object_name, object_graphics) in scene_descriptor.objects.items():
                self.display_file.add_object(object_name, object_graphics)
            # Sync Object Tree
            self.sync_object_tree()
        # Reset Seleceted Filename
        self.scene_file_name = None
        # Close Dialog
        dialog.hide()

    # Handle Scene Save
    @Gtk.Template.Callback("on-menu-scene-save")
    def on_menu_scene_save(self, _item):
        # Set Current Directory
        self.dialgo_scene_save.set_current_folder(getcwd())
        self.dialgo_scene_save.set_current_name("scene.obj")
        self.dialgo_scene_save.set_title("Save As (Object File)")
        # Set Current Step
        self.scene_file_name = None
        self.scene_save_step = DialogSceneSaveType.SELECT_OBJECT
        # Open File Chooser
        self.dialgo_scene_save.show_all()
    
    @Gtk.Template.Callback("on-window-scene-save-delete-event")
    def on_window_scene_save_delete_event(self, _dialog, _event):
        # Response Dialog
        self.dialgo_scene_save.hide()
        # Do Not Destroy
        return True

    @Gtk.Template.Callback("on-window-scene-save-file-activate")
    def on_window_scene_save_file_activate(self, _file_chooser):
        # Response Dialog
        self.dialgo_scene_save.response(Gtk.ResponseType.OK)

    @Gtk.Template.Callback("on-window-scene-save-btn-open")
    def on_window_scene_save_btn_open(self, _file_chooser):
        # Response Dialog
        self.dialgo_scene_save.response(Gtk.ResponseType.OK)
    
    @Gtk.Template.Callback("on-window-scene-save-btn-cancel")
    def on_window_scene_save_btn_cancel(self, _file_chooser):
        # Response Dialog
        self.dialgo_scene_save.response(Gtk.ResponseType.CANCEL)

    @Gtk.Template.Callback("on-window-scene-save-file-selected")
    def on_window_scene_save_file_selected(self, file_chooser):
        # Get Selected File
        if self.scene_save_step == DialogSceneSaveType.SELECT_OBJECT:
            self.scene_file_name: str = file_chooser.get_filename()
        elif self.scene_save_step ==  DialogSceneSaveType.SELECT_MATERIAL:
            self.material_file_name: str = file_chooser.get_filename()

    @Gtk.Template.Callback("on-window-scene-save-response")
    def on_window_scene_save_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            if self.scene_save_step == DialogSceneSaveType.SELECT_OBJECT:
                # Prepare for Next Step
                self.scene_save_step = DialogSceneSaveType.SELECT_MATERIAL
                self.dialgo_scene_save.set_current_folder(getcwd())
                self.dialgo_scene_save.set_current_name("scene.mtl")
                self.dialgo_scene_save.set_title("Save As (Material File)")
                # Close Dialog
                dialog.hide()
                # Set Dialog Title
                dialog.set_title("Save As (Material)")
                # Show Dialog
                dialog.show_all()
                return
            elif self.scene_save_step == DialogSceneSaveType.SELECT_MATERIAL:
                # Close Dialog
                dialog.hide()
                # Check Viewport and Window
                if self.viewport is None or self.viewport.window is None:
                    return
                # Serialize Scene and Save File
                DescriptorOBJ.serializeToFiles(
                    self.scene_file_name,
                    self.material_file_name,
                    self.display_file,
                    self.viewport.window
                )
        else:
            # Close Dialog
            dialog.hide()