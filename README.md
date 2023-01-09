# Macrosteps Octoprint Plugin
A Simple Octoprint plugin that enables you to follow the steps of your big macros.
With this plugin you can keep track of what your big macros are doing. It helps also to diagnose when something went wrong.

It creates a panel on (Octoprint)[https://octoprint.org/]'s UI with every step (or GCODE command) of your MACRO and updates it on the fly:



If you don't know what MACRO means, take a look into this if you are using [Klipper](https://www.klipper3d.org/) firmware:

https://klipper.discourse.group/t/macro-creation-tutorial/30

... or this if you are using [Marlin](https://marlinfw.org/) firmware:

https://plugins.octoprint.org/plugins/gcode_macro/

https://plugins.octoprint.org/plugins/macro/

## Quick start (Klipper only):

Just add this to the begining of your macro:

```
RESPOND MSG="$MS create macroid=1 label=\"Print Start\""
RESPOND MSG="$MS addstep macroid=1 step=1 label=\"Heat Soak\""
RESPOND MSG="$MS addstep macroid=1 step=2 label=\"Homing\""
RESPOND MSG="$MS addstep macroid=1 step=8 label=\"Bed level\""
RESPOND MSG="$MS addstep macroid=1 step=6 label=\"Wipe Nozzle\""
```

and then this just before each one of your's gcode commands:

```
RESPOND MSG="$MS nextstep macroid=1"
```

## Quick start (Marlin only):

Just add this to the begining of your macro:

```
M117 $MS create macroid=1 label="Print Start"
M117 $MS addstep macroid=1 step=1 label="Heat Soak"
M117 $MS addstep macroid=1 step=2 label="Homing"
M117 $MS addstep macroid=1 step=3 label="Bed Level"
M117 $MS addstep macroid=1 step=4 label="Wipe Nozzle"
```

and then this just before each one of your's gcode commands:

```
M117 $MS nextstep macroid=1
```

And now just run your macro and have fun!

For more info and available commands, check the [Wiki](https://github.com/SinisterRj/OctoPrint-Macrosteps/wiki).
