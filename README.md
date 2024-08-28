# MacroSteps Octoprint Plugin
A Simple Octoprint plugin that enables you to follow the steps of your big macros.
With this plugin you can keep track of what your big macros are doing. It helps also to diagnose when something went wrong.

It creates a sidepanel on [Octoprint](https://octoprint.org/)'s UI with every step (or GCODE command) of your MACRO and updates it on the fly:

![MacroSteps Plugin sidebar](https://github.com/SinisterRj/OctoPrint-Macrosteps/raw/main/Pictures/MS.jpg)

If you don't know what MACRO means, take a look into this if you are using [Klipper](https://www.klipper3d.org/) firmware:

https://klipper.discourse.group/t/macro-creation-tutorial/30

... or this if you are using [Marlin](https://marlinfw.org/) firmware:

https://plugins.octoprint.org/plugins/gcode_macro/

https://plugins.octoprint.org/plugins/macro/

## Quick start:

Just add this to the begining of your macro or start gcode:

P.S.: If you're running klipper, be shure to create a **[respond]** section on your printer.cfg file to enable M118 Gcode.

```
M118 $MS create macroid=1 label="Print Start"
M118 $MS addstep macroid=1 step=1 label="Heat Soak"
M118 $MS addstep macroid=1 step=2 label="Homing"
M118 $MS addstep macroid=1 step=3 label="Bed Level"
M118 $MS addstep macroid=1 step=4 label="Wipe Nozzle"
```

and then this just before each one of your's gcode commands:

```
M118 $MS nextstep macroid=1
```

And now just run your macro and have fun!

For more info and available commands, check the [Wiki](https://github.com/SinisterRj/OctoPrint-Macrosteps/wiki).


Se você é brasileiro 🇧🇷, junte-se a nós no Discord:
https://discord.gg/3DyXfGwWJY

