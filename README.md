# PY-IGS - The PYthon Interactive Graphical System

<div align="center">
    <img src="./doc/images/full-screenshot2.png" alt="PY-IGS" height="400" ></img>
    <p>
        <em>The PY-IGS</em>
    </p>
</div>

## Installation
To install this software you will need these dependencies (with their thevelopment libraries):

- Numba/SciPy/NumPy Compatible Setup (`https://numba.readthedocs.io/en/stable/user/installing.html`) (Use for C matrix multiplication)
- Gtk 3.20+
- PyGOBject Dependencies (`libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0`)
- Python 3.8+
- Poetry (To install it, please visit the [official install instructions](https://python-poetry.org/docs/#installation))

After install them, install python dependencies
with:

```
poetry install
```

---

## How to Use
### Executing

In order to execute this program, run the following command:

```
poetry run python3 py_igs
```

### Navigation

To navigate through the world, you can use the mouse or the navigation widget.

To move with the mouse, simply click over the viewport and drag your cursor over the screen. The amplitude of this movement is inverse to the scale of the world, enabling a smooth view in your screen.

If you want to use the navigation widget, you need to click on the buttons that are displayed on the navigation grid in the left panel. You can configure the amplitude of this movement with the "Pan Step" field (world units).

For zooming, you can use your mouse scroll or the `+` and `-` buttons on the navigation grid. You can configure the zoom ammount with the "Zoom Step" slider (from 0,01% up to 50% each step)

You can also rotate the Window using the upper left and upper right buttons on navigation grid.

<div align="center">
    <img src="./doc/images/navigation-widget.png" alt="Navigation Widget" height="200" ></img>
    <p>
        <em>The navigation widget</em>
    </p>
</div>

### Adding Objects

To add an object, you need to click on the "Add" button located in the objects widget. A dialog will popup in your screen.

In this dialog, insert the object name (unique in the scene) then insert the points coordinates of your object. You can select the type of the object by changing the active tab of the dialog. The drawing color can also be defined in this dialog.
There is an option to fill wireframes too, just check the `filled` option when adding the object.

You can also input raw values at the "Text" tab. To use it, declare points using this format: `(x1, y1), (x2, y2), ...` (Obs: New lines are not allowed).

After that, click on the save button. The object will appear on the world at the given coordinates.

<div align="center">
    <img src="./doc/images/object-add.png" alt="Adding an object" height="200" ></img>
    <p>
        <em>Adding an object</em>
    </p>
</div>

### Editing Objects (Transforms)
Clicking in the edit button (in the objects widget) will open the editing dialog. In this window, you can define 3 transformations to apply on the object. They are: Translation, Rotation and Scaling. The translation will move the object over the world. The rotation will rotate the object around a given point that can be the world origin, the object center or a point that you specify. The scale will scale the objects in a "natural" way, i.e., based on the object center.

All transformations are stored in a list that will be merged when applying these transformations to the object.

<div align="center">
    <img src="./doc/images/object-edit.png" alt="Editing an object" height="200" ></img>
    <p>
        <em>Editing an object</em>
    </p>
</div>

### Removing Objects

Select an object of the object list and then press the remove button in the objects widget. The object will disappear.

<div align="center">
    <img src="./doc/images/objects-widget.png" alt="Objects Widget" height="150" ></img>
    <p>
        <em>The objects widget</em>
    </p>
</div>

### Window Clipping

Currently we support 3 methods for Window clipping, they are:

- None
- Cohen-Sutherland
- Liang-Barsky

To choose it, select the desired method in the `Clipping Method` option in the Window widget.

<div align="center">
    <img src="./doc/images/window-widget.png" alt="Window Widget" width="300" ></img>
    <p>
        <em>The window widget</em>
    </p>
</div>

### Import/Export Scenes (Wavefront Object)

In the menu bar, you can select the `Scene`, then select `Open` to import objects. A file chooser will pop up and the you need to select the file to import.

To export your scene, click on `Scene`, then select `Save As`. Then define were you want to save your `.obj` (Model) file and then select a location for the `.mtl` (Materials) file.

#### Example Files

In the `example/objects` folder you can find many models that were utilized to test Py-Igs functionalities.

---
## About
Made by Enzo Coelho Albornoz and Gabriel Soares Flores.

Software developed for the Computer Graphics (INE5420-2021.1)  course. This course is part of our graduation in Computer Science at the Federal University of Santa Catarina (UFSC). 

<div align="right">
    <a href="https://ufsc.br/">
        <img src="./doc/images/brasao.ufsc.svg" alt="Window Widget" width="200"></img>
    </a>
    <p>
        <em>Made in UFSC</em>
    </p>
</div>

