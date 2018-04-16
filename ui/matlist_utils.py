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

# Addon imports
from ..functions import *


def addMaterialToList(self, context):
    scn, cm, n = getActiveContextInfo()
    matObj = getMatObject(cm)
    numMats = len(matObj.data.materials)
    mat = bpy.data.materials.get(cm.targetMaterial)
    if mat is None:
        return
    elif mat.name in matObj.data.materials.keys():
        cm.targetMaterial = "Already in list!"
    elif matObj is not None:
        matObj.data.materials.append(mat)
        cm.targetMaterial = ""
    if numMats < len(matObj.data.materials) and not cm.lastSplitModel:
        cm.materialIsDirty = True
