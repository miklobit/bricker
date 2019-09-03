# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
from operator import itemgetter

# Blender imports
import bpy
from bpy.props import *

# Module imports
from .general import *
from .matlist_utils import *
from ..operators.bevel import BRICKER_OT_bevel
from ..subtrees.background_processing.classes.job_manager import JobManager


def uniquify_name(self, context):
    """ if Brick Model exists with name, add '.###' to the end """
    scn, cm, _ = get_active_context_info()
    name = cm.name
    while scn.cmlist.keys().count(name) > 1:
        if name[-4] == ".":
            try:
                num = int(name[-3:])+1
            except ValueError:
                num = 1
            name = name[:-3] + "%03d" % (num)
        else:
            name = name + ".001"
    if cm.name != name:
        cm.name = name


def set_default_obj_if_empty(self, context):
    scn = context.scene
    last_cmlist_index = scn.cmlist_index
    cm0 = scn.cmlist[last_cmlist_index]
    # verify model doesn't exist with that name
    if cm0.source_obj is not None:
        for i, cm1 in enumerate(scn.cmlist):
            if cm1 != cm0 and cm1.source_obj is cm0.source_obj:
                cm0.source_obj = None
                scn.cmlist_index = i


def update_bevel(self, context):
    # get bricks to bevel
    try:
        scn, cm, n = get_active_context_info()
        if cm.last_bevel_width != cm.bevel_width or cm.last_bevel_segments != cm.bevel_segments or cm.last_bevel_profile != cm.bevel_profile:
            bricks = get_bricks()
            BRICKER_OT_bevel.create_bevel_mods(cm, bricks)
            cm.last_bevel_width = cm.bevel_width
            cm.last_bevel_segments = cm.bevel_segments
            cm.last_bevel_profile = cm.bevel_profile
    except Exception as e:
        raise Exception("[Bricker] ERROR in update_bevel():", e)
        pass


def update_parent_exposure(self, context):
    scn, cm, _ = get_active_context_info()
    if not (cm.model_created or cm.animated):
        return
    parent_ob = cm.parent_obj
    if parent_ob:
        if cm.expose_parent:
            safe_link(parent_ob, protect=True)
            select(parent_ob, active=True, only=True)
        else:
            try:
                safe_unlink(parent_ob)
            except RuntimeError:
                pass


def update_model_scale(self, context):
    scn, cm, _ = get_active_context_info()
    if not (cm.model_created or cm.animated):
        return
    _, _, s = get_transform_data(cm)
    parent_ob = cm.parent_obj
    if parent_ob:
        parent_ob.scale = Vector(s) * cm.transform_scale


def update_circle_verts(self, context):
    scn, cm, _ = get_active_context_info()
    if (cm.circle_verts - 2) % 4 == 0:
        cm.circle_verts += 1
    cm.bricks_are_dirty = True


def update_job_manager_properties(self, context):
    scn, cm, _ = get_active_context_info()
    job_manager = JobManager.get_instance(cm.id)
    job_manager.timeout = cm.back_proc_timeout
    job_manager.max_workers = cm.max_workers


def update_brick_shell(self, context):
    scn, cm, _ = get_active_context_info()
    if cm.brick_shell == "CONSISTENT":
        cm.verify_exposure = True
    cm.matrix_is_dirty = True


def dirty_anim(self, context):
    scn, cm, _ = get_active_context_info()
    cm.anim_is_dirty = True


def dirty_material(self, context):
    scn, cm, _ = get_active_context_info()
    cm.material_is_dirty = True


def dirty_model(self, context):
    scn, cm, _ = get_active_context_info()
    cm.model_is_dirty = True


# NOTE: Any prop that calls this function should be added to get_matrix_settings()
def dirty_matrix(self=None, context=None):
    scn, cm, _ = get_active_context_info()
    cm.matrix_is_dirty = True


def dirty_internal(self, context):
    scn, cm, _ = get_active_context_info()
    cm.internal_is_dirty = True
    cm.build_is_dirty = True


def dirty_build(self, context):
    scn, cm, _ = get_active_context_info()
    cm.build_is_dirty = True


def dirty_bricks(self, context):
    scn, cm, _ = get_active_context_info()
    cm.bricks_are_dirty = True


def update_brick_type(self, context):
    scn, cm, _ = get_active_context_info()
    cm.zstep = get_zstep(cm)
    cm.matrix_is_dirty = True


def update_bevel_render(self, context):
    scn, cm, _ = get_active_context_info()
    show_render = cm.bevel_show_render
    for brick in get_bricks():
        bevel = brick.modifiers.get(brick.name + "_bvl")
        if bevel: bevel.show_render = show_render


def update_bevel_viewport(self, context):
    scn, cm, _ = get_active_context_info()
    show_viewport = cm.bevel_show_viewport
    for brick in get_bricks():
        bevel = brick.modifiers.get(brick.name + "_bvl")
        if bevel: bevel.show_viewport = show_viewport


def update_bevel_edit_mode(self, context):
    scn, cm, _ = get_active_context_info()
    show_in_editmode = cm.bevel_show_edit_mode
    for brick in get_bricks():
        bevel = brick.modifiers.get(brick.name + "_bvl")
        if bevel: bevel.show_in_editmode = show_in_editmode


def add_material_to_list(self, context):
    scn, cm, n = get_active_context_info()
    typ = "RANDOM" if cm.material_type == "RANDOM" else "ABS"
    mat_obj = get_mat_obj(cm, typ=typ)
    num_mats = len(mat_obj.data.materials)
    mat = bpy.data.materials.get(cm.target_material)
    if mat is None:
        return
    elif mat.name in mat_obj.data.materials.keys():
        cm.target_material = "Already in list!"
    elif typ == "ABS" and mat.name not in get_abs_mat_names():
        cm.target_material = "Not ABS Plastic material"
    elif mat_obj is not None:
        mat_obj.data.materials.append(mat)
        cm.target_material = ""
    if num_mats < len(mat_obj.data.materials) and not cm.last_split_model:
        cm.material_is_dirty = True


def select_source_model(self, context):
    """ if scn.cmlist_index changes, select and make source or brick model active """
    scn = bpy.context.scene
    obj = bpy.context.view_layer.objects.active if b280() else scn.objects.active
    # don't select source model if this property was set to True by timer
    if bpy.props.manual_cmlist_update:
        bpy.props.manual_cmlist_update = False
        return
    if scn.cmlist_index != -1:
        cm, n = get_active_context_info()[1:]
        source = cm.source_obj
        if source and cm.version[:3] != "1_0":
            if cm.model_created:
                bricks = get_bricks()
                if bricks and len(bricks) > 0:
                    select(bricks, active=True, only=True)
                    scn.bricker_last_active_object_name = obj.name if obj is not None else ""
            elif cm.animated:
                cf = get_anim_adjusted_frame(scn.frame_current, cm.last_start_frame, cm.last_stop_frame)
                brick_obj = bpy_collections().get("Bricker_%(n)s_bricks_f_%(cf)s" % locals()).objects[0]
                if brick_obj is not None and len(brick_objs) > 0:
                    select(brick_obj, active=True, only=True)
                    scn.bricker_last_active_object_name = obj.name if obj is not None else ""
                else:
                    set_active_obj(None)
                    deselect_all()
                    scn.bricker_last_active_object_name = ""
            else:
                select(source, active=True, only=True)
                scn.bricker_last_active_object_name = source.name
        else:
            for i,cm0 in enumerate(scn.cmlist):
                if get_source_name(cm0) == scn.bricker_active_object_name:
                    deselect_all()
                    break
