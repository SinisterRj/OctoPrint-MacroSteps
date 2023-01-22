
'''
 * MacroSteps Octoprint Plugin
 * Copyright (c) 2022 Rodrigo C. C. Silva [https://github.com/SinisterRj/Octoprint_MacroSteps]
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 * 
 * 
 *  Change log:
 *
 * Version 0.1.1
 * 01/22/2023
 * 1) Fix a bug that duplicate steps when a new Octoprint instance is opened;
 * 2) Fix plugin name on setup.py.
 *
 * Version 0.1.0 - Initial Release
 * 01/13/2023
'''

# coding=utf-8
from __future__ import absolute_import
import logging
import logging.handlers
import octoprint.plugin
import re

class MacrostepsPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.TemplatePlugin
):
    
    class macro:
        def __init__(self,idnum,label,runningstep):
            self.idnum = idnum
            self.label = label
            self.runningstep = runningstep

    class step:
        def __init__(self,macroid,stepid,label,status,msg):
            self.macroid = macroid
            self.stepid = stepid
            self.label = label
            self.status = status
            self.msg = msg

    def __init__(self):
        self._console_logger = logging.getLogger("octoprint.plugins.macrosteps")
        self.macros = []
        self.steps = []

    def on_after_startup(self):
        self._logger.info("Macro Steps Plugin started.") #Octoprint logger 

    ##~~ AssetPlugin mixin
    def get_template_configs(self):
        return [
            dict(type="sidebar", name="Macro Steps", custom_bindings=False, icon="list"),
        ]

    def get_assets(self):
        return {
            "js": ["js/MacroSteps.js"],
            "css": ["css/MacroSteps.css"]
        }

    def custom_gcode_handler(self, comm, line, *args, **kwargs):
        if "$MS" not in line:
            return line

        self.command = ""
        self.arg_label = ""
        self.arg_macroid = 0
        self.arg_stepid = 0
        self.arg_status = 0
        self.arg_type = 0
        self.arg_string = ""
        self.error = False

        self.originalParameters = line

        # remove comments
        parameters = line.split(';')[0] 

        # remove strings from command before interpret it
        self.arg_string = re.search(r'"(.*)"|$', parameters)[0]
        parameters = parameters.replace(self.arg_string, "")
        parameters = parameters.strip()

        parameters = parameters.upper()
        parameters = parameters.split(' ')

        if "ECHO:" in parameters: parameters.remove("ECHO:")
        if "$MS" in parameters: parameters.remove("$MS")
        if "ECHO:$MS" in parameters: parameters.remove("ECHO:$MS")

        self._console_logger.debug("Received Command:")
        self._console_logger.debug(parameters)
        self._console_logger.debug(self.arg_string)

        for parameter in parameters:
            subparameters = parameter.split('=')
            if (
                subparameters[0] == "RESET" or
                subparameters[0] == "CREATE" or
                subparameters[0] == "ADDSTEP" or 
                subparameters[0] == "CLEARALL" or 
                subparameters[0] == "NEXTSTEP" or 
                subparameters[0] == "MSG" or 
                subparameters[0] == "SKIP" or 
                subparameters[0] == "FAIL"
            ):
                self.command = subparameters[0]
            elif subparameters[0] == "MACROID":
                try:
                    self.arg_macroid = int(subparameters[1])
                except ValueError as error:
                    self.error = True
            elif subparameters[0] == "LABEL":
                if self.arg_string == "":
                    self.arg_label = subparameters[1]
                else:
                    self.arg_label = self.arg_string.replace('"','')

            elif subparameters[0] == "STEP":
                try:
                    self.arg_stepid = int(subparameters[1])
                except ValueError as error:
                    self.error = True
                
            elif subparameters[0] == "STATUS":
                self.command = subparameters[0]
                if subparameters[1] == "RUN":
                    self.arg_status = 1
                elif subparameters[1] == "DONE":
                    self.arg_status = 2
                elif subparameters[1] == "FAIL":
                    self.arg_status = 3
                elif subparameters[1] == "SKIP":
                    self.arg_status = 4

            elif subparameters[0] == "TYPE":
                if subparameters[1] == "INFO":
                    self.arg_type = 1
                elif subparameters[1] == "WARNING":
                    self.arg_type = 2
                elif subparameters[1] == "ERROR":
                    self.arg_type = 3
                elif subparameters[1] == "SUCCESS":
                    self.arg_type = 4

            else:
                self.popupError("Unknown command")
        
        if self.command == "CREATE" and self.arg_macroid > 0 and not self.error:

            macroFiltered = self.findMacro(self.arg_macroid)
            if (macroFiltered == None):
                self.macros.append(self.macro(int(self.arg_macroid),self.arg_label,0))
                self.macros.sort(key=lambda x: x.idnum)
                self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "addmacro", "macroid": self.arg_macroid, "label":self.arg_label})
            else:
                macroFiltered.label = self.arg_label
                macroFiltered.runningstep = 0
                self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "updatemacro", "macroid": self.arg_macroid, "label":self.arg_label})

        elif self.command == "ADDSTEP" and self.arg_stepid > 0 and not self.error:

            if (self.findMacro(self.arg_macroid) != None):
                stepFiltered = self.findStep(self.arg_macroid,self.arg_stepid)
                if (stepFiltered == None):
                    self.steps.append(self.step(int(self.arg_macroid),int(self.arg_stepid),self.arg_label,0,""))
                    self.steps.sort(key=lambda x: x.stepid)
                    self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "addstep", "macroid": self.arg_macroid, "stepid": self.arg_stepid, "label":self.arg_label, "status":0})
                else:
                    stepFiltered.label = self.arg_label
                    stepFiltered.status = 0
                    self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "updatestep", "macroid": self.arg_macroid, "stepid": self.arg_stepid, "label":self.arg_label, "status":0})
            else:
                self.popupError("Macro ID not found")

        elif self.command == "MSG" and self.arg_macroid > 0 and self.arg_stepid > 0 and self.arg_string != "" and self.arg_type != 0 and not self.error:

            stepFiltered = self.findStep(self.arg_macroid,self.arg_stepid)
            if (stepFiltered != None):
                stepFiltered.msg = self.arg_string                    
                self.arg_string = self.arg_string.replace('"','')                  
                self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "message", "msgtype": self.arg_type, "macroid": self.arg_macroid, "stepid": self.arg_stepid, "msg": self.arg_string})
            else:
                self.popupError("Macro or Step ID not found")            

        elif self.command == "RESET" and self.arg_macroid > 0 and not self.error:

            stepsFiltered = self.filterSteps(self.arg_macroid)
            if (stepsFiltered != None):
                macroFiltered = self.findMacro(self.arg_macroid)
                macroFiltered.runningstep = 0
                for step in stepsFiltered:
                    if step.status != 0:
                        step.status = 0
                        self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "status", "macroid": self.arg_macroid, "stepid": step.stepid, "status": 0})                
                    if step.msg != "":
                        step.msg = ""
                        self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "message", "macroid": self.arg_macroid, "stepid": step.stepid, "msg": ""})
            else:
                self.popupError("Macro ID not found")

        elif self.command == "STATUS" and self.arg_macroid != 0 and self.arg_stepid != 0 and self.arg_status != 0 and not self.error:
            
            stepFiltered = self.findStep(self.arg_macroid,self.arg_stepid)
            if (stepFiltered != None):
                stepFiltered.status = self.arg_status
                self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "status", "macroid": self.arg_macroid, "stepid": stepFiltered.stepid, "status": self.arg_status})                
                if self.arg_status == 1:
                    macroFiltered = self.findMacro(self.arg_macroid)
                    if (macroFiltered != None):
                        macroFiltered.runningstep = self.arg_stepid
            else:
                self.popupError("Macro or Step ID not found")

        elif self.command == "CLEARALL" and not self.error:
            self.macros.clear()
            self.steps.clear()
            self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "clearall"})

        elif (self.command == "NEXTSTEP" or self.command == "SKIP" or self.command == "FAIL") and self.arg_macroid > 0 and not self.error:
            macroFiltered = self.findMacro(self.arg_macroid)
            if (macroFiltered != None):
                actualRunningStep = macroFiltered.runningstep
                stepsFiltered = self.filterSteps(self.arg_macroid)
                found = False
                runNextStep = False
                for step in stepsFiltered:
                    if runNextStep:
                        step.status = 1
                        macroFiltered.runningstep = step.stepid
                        self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "status", "macroid": step.macroid, "stepid": step.stepid, "status": step.status})
                        break
                    if step.stepid == actualRunningStep:
                        found = True
                        if step.status == 1 or 3:                                
                            if self.command == "NEXTSTEP": 
                                if step.status == 1:
                                    step.status = 2
                                runNextStep = True
                            elif self.command == "FAIL":
                                step.status = 3
                            elif self.command == "SKIP":
                                step.status = 4
                                runNextStep = True
                            self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "status", "macroid": step.macroid, "stepid": step.stepid, "status": step.status})
                            if not runNextStep:
                                break
                if not found:
                     for step in stepsFiltered:
                        if self.command == "FAIL":
                            step.status = 3
                        elif self.command == "SKIP":
                            step.status = 4
                        else:
                            step.status = 1
                        macroFiltered.runningstep = step.stepid
                        self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "status", "macroid": step.macroid, "stepid": step.stepid, "status": step.status})
                        break

            else:
                self.popupError("Macro ID not found")

        else:
            self.popupError("Invalid Argument")

    def findMacro (self,macroid):
        if (macroid != None):
            for macro in self.macros:
                if macro.idnum == macroid:
                    return macro
            return None
        else:
            return None 

    def filterSteps (self,macroid):
        filteredSteps = []
        if (macroid != None):
            for step in self.steps:
                if step.macroid == macroid:
                    filteredSteps.append(step)
            return filteredSteps
        else:
            return None

    def findStep (self,macroid, stepid):
        if (macroid != None and stepid != None):
            for step in self.steps:
                if step.macroid == macroid and step.stepid == stepid:
                    return step
            return None
        else:
            return None

    def popupError (self,msg):
        self.error = True
        self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "error", "msg": msg + " in: " + self.originalParameters})  
        self._console_logger.info("ERROR: " + msg + " in: " + self.originalParameters) 

    # Simple API commands. Deal with UI commands

    def get_api_commands(self):
        return dict(
            forceRenew=[],
        )

    def on_api_command(self, command, data):
        try:
            if command == "forceRenew":
                self.forceRenew()
        except Exception as e:
            error = str(e)
            self._console_logger.info("Exception message: %s" % str(e))
            return flask.jsonify(error=error, status=500), 500

    def forceRenew(self):
        if len(self.macros) > 0:
            self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "clearall"})
            for macro in self.macros:
                self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "addmacro", "macroid": macro.idnum, "label":macro.label})
            
            if len(self.steps) > 0:
                for step in self.steps:
                    self._plugin_manager.send_plugin_message(self._identifier, {"cmd": "addstep", "macroid": step.macroid, "stepid": step.stepid, "label":step.label, "status":step.status})

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "MacroSteps": {
                "displayName": "Macro Steps",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "SinisterRj",
                "repo": "OctoPrint-Macrosteps",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/SinisterRj/OctoPrint-Macrosteps/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Macro Steps"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = MacrostepsPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.custom_gcode_handler
    }
