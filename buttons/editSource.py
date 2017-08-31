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
import bpy
import time
from mathutils import Vector
from ..functions import *
props = bpy.props

class legoizerEditSource(bpy.types.Operator):
    """ Edit Source Object Mesh """                                             # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.legoizer_edit_source"                                             # unique identifier for buttons and menu items to reference.
    bl_label = "Edit Source Object Mesh"                                        # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.cmlist_index == -1:
            return False
        cm = scn.cmlist[scn.cmlist_index]
        if not cm.modelCreated:
            return False
        if scn.name == "LEGOizer_storage (DO NOT RENAME)":
            return False
        return True

    def modal(self, context, event):
        scn = bpy.context.scene
        source = bpy.data.objects.get(self.source_name)
        if bpy.props.commitEdits or source is None or bpy.context.scene.name != "LEGOizer_storage (DO NOT RENAME)" or source.mode != "EDIT" or event.type in {"ESC"} or (event.type in {"TAB"} and event.value == "PRESS"):
            self.report({"INFO"}, "Edits Committed")
            # if LEGOizer_storage scene is not active, set to active
            sto_scn = bpy.data.scenes.get("LEGOizer_storage (DO NOT RENAME)")
            if bpy.context.scene != sto_scn:
                for screen in bpy.data.screens:
                    screen.scene = sto_scn
            # set source to object mode
            select(source, active=source)
            bpy.ops.object.mode_set(mode='OBJECT')
            setOriginToObjOrigin(toObj=source, fromLoc=self.lastSourceOrigLoc)
            # reset source origin to adjusted location
            if source["before_edit_location"] != -1:
                source.location = source["before_edit_location"]
            source.rotation_euler = source["previous_rotation"]
            source.scale = source["previous_scale"]
            scn.update()
            if bpy.context.scene.name == "LEGOizer_storage (DO NOT RENAME)":
                for screen in bpy.data.screens:
                    screen.scene = bpy.data.scenes.get(bpy.props.origScene)
            bpy.props.commitEdits = False
            bpy.context.window_manager["editingSourceInStorage"] = False
            redraw_areas("VIEW_3D")
            scn.update()
            return {"FINISHED"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        # initialize variables
        scn = context.scene
        bpy.props.origScene = scn.name
        cm = scn.cmlist[scn.cmlist_index]
        n = cm.source_name
        bpy.context.window_manager["editingSourceInStorage"] = True
        self.source_name = cm.source_name + " (DO NOT RENAME)"
        LEGOizer_bricks_gn = "LEGOizer_" + cm.source_name + "_bricks"
        LEGOizer_last_origin_on = "LEGOizer_%(n)s_last_origin" % locals()
        cm.sourceIsDirty = True

        # get LEGOizer_storage (DO NOT RENAME) scene
        sto_scn = bpy.data.scenes.get("LEGOizer_storage (DO NOT RENAME)")
        if sto_scn is None:
            self.report({"WARNING"}, "'LEGOizer_storage (DO NOT RENAME)' scene could not be found")
            return {"CANCELLED"}
        # get source object
        source = bpy.data.objects.get(self.source_name)
        if source is None:
            self.report({"WARNING"}, "Source object '" + self.source_name + "' could not be found")
            return {"CANCELLED"}

        # set cursor location of LEGOizer_storage scene to cursor loc of original scene
        sto_scn.cursor_location = tuple(scn.cursor_location)

        # set active scene as LEGOizer_storage (DO NOT RENAME)
        for screen in bpy.data.screens:
            screen.scene = sto_scn

        # make source visible and active selection
        sto_scn.layers = source.layers
        for obj in sto_scn.objects:
            obj.hide = True
        source.hide = False
        bGroup = bpy.data.groups.get(LEGOizer_bricks_gn)
        source["before_edit_location"] = -1
        self.last_origin_obj = bpy.data.objects.get(LEGOizer_last_origin_on)
        if bGroup is not None and len(bGroup.objects) > 0:
            if not cm.lastSplitModel:
                obj = bGroup.objects[0]
            else:
                obj = None
            objParent = bpy.data.objects.get("LEGOizer_%(n)s_parent" % locals())
            source["before_edit_location"] = source.location.to_tuple()
            setSourceTransform(source, obj=obj, objParent=objParent)
        select(source, active=source)

        # set sourceOrig origin to previous origin location
        scn.update()
        self.lastSourceOrigLoc = source.location.to_tuple()
        setOriginToObjOrigin(toObj=source, fromObj=self.last_origin_obj)
        scn.update()

        # enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # run modal
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        source.location = source["before_edit_location"]
        source.rotation_euler = source["previous_rotation"]
        source.scale = source["previous_scale"]
        for screen in bpy.data.screens:
            screen.scene = bpy.data.scenes.get(bpy.props.origScene)

class legoizerCommitEdits(bpy.types.Operator):
    """ Edit Source Object Mesh """                                             # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.legoizer_commit_edits"                                   # unique identifier for buttons and menu items to reference.
    bl_label = "Edit Source Object Mesh"                                        # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.name != "LEGOizer_storage (DO NOT RENAME)":
            return False
        return True

    def execute(self, context):
        print("executing")
        bpy.props.commitEdits = True
        return{"FINISHED"}
