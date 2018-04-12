"""
    Copyright (C) 2017 Bricks Brought to Life
    http://bblanimation.com/
    chris@bblanimation.com

    Created by Christopher Gearhart

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """

# system imports
import time

# Blender imports
import bpy
from bpy.props import StringProperty

# Addon imports
from ..functions import *
from ..buttons.customize.functions import *


class BrickerRedrawCustomBricks(bpy.types.Operator):
    """Redraw custom bricks with current custom object"""
    bl_idname = "bricker.redraw_custom"
    bl_label = "Redraw Custom Bricks"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        try:
            cm = scn.cmlist[scn.cmlist_index]
        except IndexError:
            return False
        n = cm.source_name
        if cm.matrixIsDirty:
            return False
        return cm.modelCreated or cm.animated

    def execute(self, context):
        try:
            self.redrawCustomBricks()
        except:
            handle_exception()
        return{"FINISHED"}

    ###################################################
    # class variables

    target_prop = StringProperty(default="")

    #############################################
    # class methods

    @staticmethod
    def redrawCustomBricks():
        cm = getActiveContextInfo()[1]
        bricksDict, _ = getBricksDict(cm=cm)
        if bricksDict is None:
            return
        keysToUpdate = [k for k in bricksDict if "CUSTOM" in bricksDict[k]["type"]]
        if len(keysToUpdate) != 0:
            drawUpdatedBricks(cm, bricksDict, keysToUpdate)

    #############################################