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
# NONE!

# Blender imports
import bpy
from addon_utils import check, paths, enable
from bpy.types import Panel
from bpy.props import *

# Module imports
from ..created_model_uilist import *
from ..matslot_uilist import *
from ...lib.caches import cache_exists
from ...operators.revert_settings import *
from ...operators.brickify import *
from ...operators.customization_tools.bricksculpt import *
from ...functions import *
from ... import addon_updater_ops


class VIEW3D_PT_bricker_model_settings(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Model Settings"
    bl_idname      = "VIEW3D_PT_bricker_model_settings"
    bl_context     = "objectmode"

    @classmethod
    def poll(self, context):
        if not settings_can_be_drawn():
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = get_active_context_info()
        source = cm.source_obj

        col = layout.column(align=True)
        # draw Brick Model dimensions to UI
        if source:
            r = get_model_resolution(source, cm)
            if cm.brick_type == "CUSTOM" and r is None:
                col.label(text="[Custom object not found]")
            else:
                split = layout_split(col, factor=0.5)
                col1 = split.column(align=True)
                col1.label(text="Dimensions:")
                col2 = split.column(align=True)
                col2.alignment = "RIGHT"
                col2.label(text="{}x{}x{}".format(int(r.x), int(r.y), int(r.z)))
        row = col.row(align=True)
        row.prop(cm, "brick_height")
        row = col.row(align=True)
        row.prop(cm, "gap")

        row = col.row(align=True)
        # if not cm.use_animation:
        col = layout.column()
        row = col.row(align=True)
        right_align(row)
        row.active = not cm.use_animation
        row.prop(cm, "split_model")

        col = layout.column()
        row = col.row(align=True)
        row.active = cm.calc_internals
        row.prop(cm, "shell_thickness")

        col = layout.column()
        row = col.row(align=True)
        row.label(text="Randomize:")
        row = col.row(align=True)
        split = layout_split(row, factor=0.5)
        col1 = split.column(align=True)
        col1.prop(cm, "random_loc", text="Loc")
        col2 = split.column(align=True)
        col2.prop(cm, "random_rot", text="Rot")
