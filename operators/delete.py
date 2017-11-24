bl_info = {
    "name"        : "Rebrickr",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 0, 1),
    "blender"     : (2, 78, 0),
    "description" : "Turn any mesh into a 3D brick sculpture or simulation with the click of a button",
    "location"    : "View3D > Tools > Rebrickr",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "https://www.blendermarket.com/creator/products/rebrickr/",
    "tracker_url" : "https://github.com/bblanimation/rebrickr/issues",
    "category"    : "Object"}

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

# System imports
# NONE!

# Blender imports
import bpy
from bpy.types import Operator
from bpy.props import *

# Rebrickr imports
from ..lib.bricksDict import *
from ..functions.common import *
from ..functions.general import *
from ..buttons.customize.functions import getAdjKeysAndBrickVals, drawUpdatedBricks, createObjsD
from ..buttons.customize.undo_stack import *
from ..buttons.delete import RebrickrDelete
from ..lib.Brick import Bricks
from ..lib.bricksDict.functions import getDictKey


class delete_override(Operator):
    """OK?"""
    bl_idname = "object.delete"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'INTERNAL'}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        # return context.active_object is not None
        return True

    def execute(self, context):
        try:
            ct = time.time()
            for obj in self.objsToDelete:
                if obj.isBrick:
                    self.undo_stack.undo_push('delete_override')
                    self.undo_pushed = True
                    break
            stopWatch("1", time.time()-ct)
            ct = time.time()
            self.runDelete(context)
            stopWatch("2", time.time()-ct)
            ct = time.time()
        except:
            handle_exception()
        return {'FINISHED'}

    def invoke(self, context, event):
        # Run confirmation popup for delete action
        confirmation_returned = context.window_manager.invoke_confirm(self, event)
        if confirmation_returned != {'FINISHED'}:
            return confirmation_returned
        else:
            try:
                if bpy.props.rebrickr_initialized:
                    for obj in self.objsToDelete:
                        if obj.isBrick:
                            self.undo_stack.undo_push('delete_override')
                            self.undo_pushed = True
                            break
                self.runDelete(context)
            except:
                handle_exception()
            return {'FINISHED'}

    ################################################
    # initialization method

    def __init__(self):
        self.undo_stack = UndoStack.get_instance()
        self.iteratedStatesAtLeastOnce = False
        self.objsToDelete = bpy.context.selected_objects
        self.warnInitialize = False
        self.undo_pushed = False

    ###################################################
    # class variables

    use_global = BoolProperty(default=False)

    ################################################
    # class methods

    def runDelete(self, context):
        if not bpy.props.rebrickr_initialized:
            # initialize objsD (key:cm_idx, val:list of brick objects)
            objsD = createObjsD(self.objsToDelete)
            # remove brick type objects from selection
            for val in objsD.values():
                if len(val) > 0:
                    for obj in val:
                        self.objsToDelete.remove(obj)
                    if not self.warnInitialize:
                        self.report({"WARNING"}, "Please initialize the Rebrickr [shift+i] before attempting to delete bricks")
                        self.warnInitialize = True
        # run deleteUnprotected
        protected = self.deleteUnprotected(context, self.use_global)
        # alert user of protected objects
        if len(protected) > 0:
            self.report({"WARNING"}, "Rebrickr is using the following object(s): " + str(protected)[1:-1])
        # push delete action to undo stack
        bpy.ops.ed.undo_push(message="Delete")

    def deleteUnprotected(self, context, use_global=False):
        scn = context.scene
        protected = []
        objNamesToDelete = []
        for obj in self.objsToDelete:
            objNamesToDelete.append(obj.name)

        # initialize objsD (key:cm_idx, val:list of brick objects)
        objsD = createObjsD(self.objsToDelete)

        # update matrix
        for i,cm_idx in enumerate(objsD.keys()):
            cm = scn.cmlist[cm_idx]
            lastBlenderState = cm.blender_undo_state
            # get bricksDict from cache
            bricksDict,loadedFromCache = getBricksDict("UPDATE_MODEL", cm=cm, restrictContext=True)
            if not loadedFromCache:
                self.report({"WARNING"}, "Adjacent bricks in '" + cm.name + "' could not be updated (matrix not cached)")
                continue
            keysToUpdate = []
            zStep = getZStep(cm)

            for obj in objsD[cm_idx]:
                # get dict key details of current obj
                dictKey, dictLoc = getDictKey(obj.name)
                x0,y0,z0 = dictLoc
                # get size of current brick (e.g. [2, 4, 1])
                objSize = bricksDict[dictKey]["size"]

                # for all locations in bricksDict covered by current obj
                for x in range(x0, x0 + objSize[0]):
                    for y in range(y0, y0 + objSize[1]):
                        for z in range(z0, z0 + (objSize[2]//zStep)):
                            curKey = listToStr([x,y,z])
                            # set 'draw' to false
                            bricksDict[curKey]["draw"] = False
                            bricksDict[curKey]["val"] = 0
                            # make adjustments to adjacent bricks
                            adjKeys, adjBrickVals = getAdjKeysAndBrickVals(bricksDict, key=curKey)
                            if min(adjBrickVals) == 0 and cm.autoUpdateExposed and cm.lastSplitModel:
                                # set adjacent bricks to shell if deleted brick was on shell
                                for k0 in adjKeys:
                                    if bricksDict[k0]["val"] != 0: # if adjacent brick not outside
                                        bricksDict[k0]["val"] = 1
                                        if not bricksDict[k0]["draw"]:
                                            bricksDict[k0]["draw"] = True
                                            bricksDict[k0]["size"] = [1,1,zStep]
                                            bricksDict[k0]["parent_brick"] = "self"
                                            bricksDict[k0]["mat_name"] = bricksDict[curKey]["mat_name"]
                                            if k0 not in keysToUpdate:
                                                # add key to simple bricksDict for drawing
                                                keysToUpdate.append(k0)
                                # top of bricks below are now exposed
                                k0 = listToStr([x, y, z - 1])
                                if k0 in bricksDict and bricksDict[k0]["draw"]:
                                    if bricksDict[k0]["parent_brick"] == "self":
                                        k1 = k0
                                    else:
                                        k1 = bricksDict[k0]["parent_brick"]
                                    if not bricksDict[k1]["top_exposed"]:
                                        bricksDict[k1]["top_exposed"] = True
                                        if k1 not in keysToUpdate:
                                            # add key to simple bricksDict for drawing
                                            keysToUpdate.append(k1)
                                # bottom of bricks above are now exposed
                                k0 = listToStr([x, y, z + 1])
                                if k0 in bricksDict and bricksDict[k0]["draw"]:
                                    if bricksDict[k0]["parent_brick"] == "self":
                                        k1 = k0
                                    else:
                                        k1 = bricksDict[k0]["parent_brick"]
                                    if not bricksDict[k1]["bot_exposed"]:
                                        bricksDict[k1]["bot_exposed"] = True
                                        if k1 not in keysToUpdate:
                                            # add key to simple bricksDict for drawing
                                            keysToUpdate.append(k1)
            # dirtyBuild if it wasn't already
            lastBuildIsDirty = cm.buildIsDirty
            if not lastBuildIsDirty: cm.buildIsDirty = True
            # draw modified bricks
            if len(keysToUpdate) > 0:
                # delete bricks that didn't get deleted already
                newKeysToUpdate = keysToUpdate.copy()
                for k in keysToUpdate:
                    splitKeys = Bricks.split(bricksDict, k, cm=cm)
                    # append new splitKeys to newKeysToUpdate
                    for k in splitKeys:
                        if k not in newKeysToUpdate:
                            newKeysToUpdate.append(k)
                for k in newKeysToUpdate:
                    brick = bpy.data.objects.get(bricksDict[k]["name"])
                    delete(brick)
                # create new bricks at all keysToUpdate locations
                drawUpdatedBricks(cm, bricksDict, newKeysToUpdate)
                iteratedStates = True
            if not lastBuildIsDirty: cm.buildIsDirty = False
            # if undo states not iterated above
            if lastBlenderState == cm.blender_undo_state:
                # iterate undo states
                self.undo_stack.iterateStates(cm)
            self.iteratedStatesAtLeastOnce = True
            # store bricksDict to cache
            cacheBricksDict("UPDATE_MODEL", cm, bricksDict)

        # if nothing was done worth undoing but state was pushed
        if not self.iteratedStatesAtLeastOnce and self.undo_pushed:
            # pop pushed value from undo stack
            self.undo_stack.undo_pop_clean()

        # delete bricks
        for obj_name in objNamesToDelete:
            obj = bpy.data.objects.get(obj_name)
            if obj is None: continue
            if obj.isBrickifiedObject or obj.isBrick:
                cm = None
                for cmCur in scn.cmlist:
                    n = cmCur.source_name
                    if obj.isBrickifiedObject:
                        cm = cmCur
                        break
                    elif obj.isBrick:
                        bGroup = bpy.data.groups.get("Rebrickr_%(n)s_bricks" % locals())
                        if bGroup is not None and len(bGroup.objects) < 2:
                            cm = cmCur
                            break
                if cm is not None:
                    RebrickrDelete.runFullDelete(cm=cm)
                    scn.objects.active.select = False
                    return protected
                else:
                    obj_users_scene = len(obj.users_scene)
                    scn.objects.unlink(obj)
                    if use_global or obj_users_scene == 1:
                        bpy.data.objects.remove(obj, True)
            elif not obj.protected:
                obj_users_scene = len(obj.users_scene)
                scn.objects.unlink(obj)
                if use_global or obj_users_scene == 1:
                    bpy.data.objects.remove(obj, True)
            else:
                print(obj.name +' is protected')
                protected.append(obj.name)

        return protected

    ################################################
