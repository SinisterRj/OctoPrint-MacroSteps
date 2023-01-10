/*
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
 */

$(function() {


    function StepType(stepid, label, icon, color , warningMsg, warning) {
        var self = this;
        self.stepid = ko.observable(stepid);
        self.label = ko.observable(label);
        self.icon = ko.observable(icon);
        self.color = ko.observable(color);
        self.warningMsg = ko.observable(warningMsg);
        self.warning = ko.observable(warning);
    }

    function MacroType(macroid, label, steps, icon, color) {
        var self = this;
        self.macroid = ko.observable(macroid);
        self.label = ko.observable(label);
        self.steps = ko.observableArray(steps);
        self.icon = ko.observable(icon);
        self.color = ko.observable(color);
    }

    function MacroStepsViewModel(parameters) {

        var self = this;
        self.debug = false;//true;  

        self.macros = ko.observableArray();

        self.icons = ['','fas fa-play','fas fa-check','fas fa-times', 'fas fa-fast-forward'];
        self.colors = ['','orange','green','red','gray'];

        // ************* Notifications :

        // Popup Messages
        self.showPopup = function(message_type, title, text){
            if (self.popup !== undefined){
                self.closePopup();
            }
            self.popup = new PNotify({
                title: gettext(title),
                text: text,
                type: message_type,
                hide: false
            });
         };

        self.closePopup = function() {
            if (self.popup !== undefined) {
                self.popup.remove();
            }
        };

        self.onStartupComplete = function() {
            if (self.debug) {console.log("MacroSteps: onStartupComplete")};
            OctoPrint.simpleApiCommand("MacroSteps", "forceRenew"); 
        };

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "MacroSteps") {
                return;
            }

            if (self.debug) {
                console.log("onDataUpdaterPluginMessage: " + data.type);
                console.log(data);
            }

            if (data.cmd == "message") {
                for (let i in self.macros()) {
                    if (self.macros()[i].macroid() == parseInt(data.macroid)) {
                        for (let j in self.macros()[i].steps()) {
                            if (self.macros()[i].steps()[j].stepid() == parseInt(data.stepid)) {
                                if (data.msg != "") {
                                    self.macros()[i].steps()[j].warning(true);
                                    self.macros()[i].steps()[j].warningMsg(data.msg);
                                }
                                else {
                                    self.macros()[i].steps()[j].warning(false);
                                    self.macros()[i].steps()[j].warningMsg("");                                    
                                }
                                break;
                            }
                        }
                        break;
                    }    
                }
                if (data.msgtype == 1) {
                    self.showPopup("info","@MS Info:",data.msg)   
                }
                else if (data.msgtype == 2) {
                    self.showPopup("notice","@MS Warning:",data.msg)   
                }
                else if (data.msgtype == 3) {
                    self.showPopup("error","@MS Error:",data.msg)   
                }
                else if (data.msgtype == 4) {
                    self.showPopup("success","@MS Success:",data.msg)   
                }
            }
            else if (data.cmd == "error") {
                self.showPopup("error","Macrosteps Plugin ERROR:",data.msg)                
            }
            else if (data.cmd == "addmacro") {
                self.macros.push(new MacroType(parseInt(data.macroid), data.label, []));
                self.macros.sort(function (l, r) { return l.macroid() > r.macroid() ? 1 : -1 });
            }
            else if (data.cmd == "addstep") {
                for (let i in self.macros()) {
                    if (self.macros()[i].macroid() == parseInt(data.macroid)) {
                        self.macros()[i].steps.push(new StepType(parseInt(data.stepid), data.label, self.icons[data.status], self.colors[data.status], false, ""));
                        self.macros()[i].steps.sort(function (l, r) { return l.stepid() > r.stepid() ? 1 : -1 });
                        break;
                    }
                }
            }
            else if (data.cmd == "updatemacro") {
                for (let i in self.macros()) {
                    if (self.macros()[i].macroid() == parseInt(data.macroid)) {
                        self.macros()[i].label(data.label);
                        break;
                    }
                }
            }
            else if (data.cmd == "updatestep") {
                for (let i in self.macros()) {
                    if (self.macros()[i].macroid() == parseInt(data.macroid)) {
                        for (let j in self.macros()[i].steps()) {
                            if (self.macros()[i].steps()[j].stepid() == parseInt(data.stepid)) {
                                self.macros()[i].steps()[j].label(data.label);
                                self.macros()[i].steps()[j].icon(self.icons[data.status]);
                                self.macros()[i].steps()[j].color(self.colors[data.status]);
                                self.macros()[i].steps()[j].warningMsg("");    
                                self.macros()[i].steps()[j].warning(false);
                                self.macros()[i].icon(self.icons[data.status]);
                                self.macros()[i].color(self.colors[data.status]);
                            }
                        }
                    }
                }
            }
            else if (data.cmd == "status") {
                for (let i in self.macros()) {
                    if (self.macros()[i].macroid() == parseInt(data.macroid)) {
                        for (let j in self.macros()[i].steps()) {
                            if (self.macros()[i].steps()[j].stepid() == parseInt(data.stepid)) {
                                self.macros()[i].steps()[j].icon(self.icons[data.status]);
                                self.macros()[i].steps()[j].color(self.colors[data.status]);
                                if ((j == self.macros()[i].steps().length -1) && (data.status == "4")) {
                                    self.macros()[i].icon(self.icons[2]);
                                    self.macros()[i].color(self.colors[2]);
                                } else {
                                    self.macros()[i].icon(self.icons[data.status]);
                                    self.macros()[i].color(self.colors[data.status]);
                                }

                                break;
                            }
                        }
                        break;
                    }    
                }
            }
            else if (data.cmd == "clearall") {
                self.macros.removeAll();
            }
        }
    }

   OCTOPRINT_VIEWMODELS.push({
        construct: MacroStepsViewModel,
        elements: ["#sidebar_plugin_MacroSteps"]
    });
});
