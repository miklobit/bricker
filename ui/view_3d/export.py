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
from ...functions import *
from ... import addon_updater_ops


class VIEW3D_PT_bricker_export(Panel):
    """ Export Bricker Model """
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI" if b280() else "TOOLS"
    bl_category    = "Bricker"
    bl_label       = "Bake/Export"
    bl_idname      = "VIEW3D_PT_bricker_export"
    bl_context     = "objectmode"
    bl_options     = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if not settings_can_be_drawn():
            return False
        scn, cm, _ = get_active_context_info()
        if created_with_unsupported_version(cm):
            return False
        if not (cm.model_created or cm.animated):
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, cm, _ = get_active_context_info()

        col = layout.column(align=True)
        col.operator("bricker.bake_model", text="Bake Model" if cm.model_created else "Bake Current Frame", icon="OBJECT_DATA")
        if (cm.model_created or cm.animated) and cm.brick_type != "CUSTOM":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("bricker.export_ldraw", text="Export Ldraw", icon="EXPORT")
