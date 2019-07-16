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
import bpy

# Blender imports
# NONE!

# Addon imports
from .mesh_generators import *
from .get_brick_dimensions import *
from ...functions.common import *
from ...functions.general import *
from ...functions.make_bricks_utils import *


class BRICKER_OT_test_brick_generators(bpy.types.Operator):
    """Draws some test bricks for testing of brick generators"""
    bl_idname = "bricker.test_brick_generators"
    bl_label = "Test Brick Generators"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            test_brick_generators()
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    @staticmethod
    def draw_ui_button():
        return False


def new_objFromBmesh(layer, bme, mesh_name, objName=None, loc=(0,0,0), edge_split=True):
    scn = bpy.context.scene
    # if only one name given, use it for both names
    objName = objName or mesh_name

    # create mesh and object
    me = bpy.data.meshes.new(mesh_name)
    ob = bpy.data.objects.new(objName, me)
    # move object to target location
    ob.location = loc
    # link and select object
    link_object(ob)
    depsgraph_update()

    # send bmesh data to object data
    bme.to_mesh(me)
    ob.data.update()

    # add edge split modifier
    if edge_split:
        add_edge_split_mod(ob)

    if not b280():
        # move to appropriate layer
        layer_list = [i == layer - 1 for i in range(20)]
        ob.layers = layer_list

    return ob


def test_brick_generators():
    # try to delete existing objects
    # delete(bpy.data.objects)

    # create objects
    scn, cm, _ = get_active_context_info()
    last_brick_type = cm.brick_type
    cm.brick_type = "BRICKS AND PLATES"
    dimensions = get_brick_dimensions(height=0.5, z_scale=cm.zstep)
    offset = -1.875
    for detail in ("FLAT", "LOW", "MEDIUM", "HIGH"):
        offset += 0.75
        # # STANDARD BRICKS
        # new_objFromBmesh(1,  make_standard_brick(dimensions, brick_size=[1,1,3], type=cm.brick_type, circle_verts=16, detail=detail), "1x1 " + detail, loc=(offset,   0,0))
        # new_objFromBmesh(2,  make_standard_brick(dimensions, brick_size=[1,2,3], type=cm.brick_type, circle_verts=16, detail=detail), "1x2 " + detail, loc=(offset,   0,0))
        # new_objFromBmesh(3,  make_standard_brick(dimensions, brick_size=[3,1,3], type=cm.brick_type, circle_verts=16, detail=detail), "3x1 " + detail, loc=(0, offset,  0))
        # new_objFromBmesh(4,  make_standard_brick(dimensions, brick_size=[1,8,3], type=cm.brick_type, circle_verts=16, detail=detail), "1x8 " + detail, loc=(offset,   0,0))
        # new_objFromBmesh(5,  make_standard_brick(dimensions, brick_size=[2,2,3], type=cm.brick_type, circle_verts=16, detail=detail), "2x2 " + detail, loc=(offset*2, 0,0))
        # new_objFromBmesh(11,  make_standard_brick(dimensions, brick_size=[2,6,3], type=cm.brick_type, circle_verts=16, detail=detail), "2x6 " + detail, loc=(offset*2, 0,0))
        # new_objFromBmesh(12,  make_standard_brick(dimensions, brick_size=[6,2,3], type=cm.brick_type, circle_verts=15, detail=detail), "6x2 " + detail, loc=(0, offset*2,0))
        # # ROUND BRICKS
        # new_objFromBmesh(6,  make_round_1x1(dimensions, circle_verts=16, type="CYLINDER",    detail=detail), "1x1 Round " + detail,  loc=(offset, 1.5,0))
        # new_objFromBmesh(6,  make_round_1x1(dimensions, circle_verts=16, type="CONE",        detail=detail), "1x1 Cone "  + detail,  loc=(offset, 0.5,0))
        # new_objFromBmesh(6,  make_round_1x1(dimensions, circle_verts=16, type="STUD",        detail=detail), "1x1 Stud "  + detail,  loc=(offset,-0.5,0))
        # new_objFromBmesh(6,  make_round_1x1(dimensions, circle_verts=16, type="STUD_HOLLOW", detail=detail), "1x1 Stud2 "  + detail, loc=(offset,-1.5,0))
        # # SLOPE BRICKS
        # i = 0
        # for posNeg in ("+", "-"):
        #     for j in (-1, 1):
        #         direction = ("X" if j == 1 else "Y") + posNeg
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[1,1][::j] + [3], direction=direction, circle_verts=16, detail=detail), "1x1 Slope "  + detail, loc=[-6,   offset][::j]               + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[2,1][::j] + [3], direction=direction, circle_verts=16, detail=detail), "2x1 Slope "  + detail, loc=[-5.5, offset][::j]               + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[3,1][::j] + [3], direction=direction, circle_verts=16, detail=detail), "3x1 Slope "  + detail, loc=[-4,   offset][::j]               + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[4,1][::j] + [3], direction=direction, circle_verts=16, detail=detail), "4x1 Slope "  + detail, loc=[-2,   offset][::j]               + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[2,2][::j] + [3], direction=direction, circle_verts=16, detail=detail), "2x2 Slope "  + detail, loc=[0.25, offset * 1.5 - 0.25][::j]  + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[3,2][::j] + [3], direction=direction, circle_verts=16, detail=detail), "3x2 Slope "  + detail, loc=[1.75, offset * 1.5 - 0.25][::j]  + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[4,2][::j] + [3], direction=direction, circle_verts=16, detail=detail), "4x2 Slope "  + detail, loc=[3.75, offset * 1.5 - 0.25][::j]  + [0])
        #         new_objFromBmesh(16 + i, make_slope(dimensions, brick_size=[3,4][::j] + [3], direction=direction, circle_verts=16, detail=detail), "4x3 Slope "  + detail, loc=[6.25, offset * 2.5 - 0.625][::j] + [0])
        #         i += 1
        # INVERTED SLOPE BRICKS
        i = 0
        for posNeg in ("+", "-"):
            for j in (-1, 1):
                direction = ("X" if j == 1 else "Y") + posNeg
                new_objFromBmesh(16 + i, make_inverted_slope(dimensions, brick_size=[2,1][::j] + [3], brick_type=cm.brick_type, direction=direction, circle_verts=16, detail=detail), "2x1 Inverted Slope "  + detail, loc=[-3,   offset][::j]              + [0])
                new_objFromBmesh(16 + i, make_inverted_slope(dimensions, brick_size=[3,1][::j] + [3], brick_type=cm.brick_type, direction=direction, circle_verts=16, detail=detail), "3x1 Inverted Slope "  + detail, loc=[-1.5, offset][::j]              + [0])
                new_objFromBmesh(16 + i, make_inverted_slope(dimensions, brick_size=[2,2][::j] + [3], brick_type=cm.brick_type, direction=direction, circle_verts=16, detail=detail), "2x2 Inverted Slope "  + detail, loc=[0.25, offset * 1.5 - 0.25][::j] + [0])
                new_objFromBmesh(16 + i, make_inverted_slope(dimensions, brick_size=[3,2][::j] + [3], brick_type=cm.brick_type, direction=direction, circle_verts=16, detail=detail), "3x2 Inverted Slope "  + detail, loc=[1.75, offset * 1.5 - 0.25][::j] + [0])
                i += 1
        # # TILES
        # new_objFromBmesh(7, make_tile(dimensions, brick_size=[1,2,1], circle_verts=16, type="TILE", detail=detail), "1x2 Tile "  + detail, loc=(offset, 6.4, 0))
        # new_objFromBmesh(7, make_tile(dimensions, brick_size=[1,2,1], circle_verts=16, type="TILE_GRILL", detail=detail), "1x2 Tile Grill "  + detail, loc=(offset, 5.3, 0))
        # new_objFromBmesh(7, make_tile(dimensions, brick_size=[2,1,1], circle_verts=16, type="TILE_GRILL", detail=detail), "1x2 Tile Grill "  + detail, loc=(offset * 1.5, 4.2, 0))
        # new_objFromBmesh(7, make_tile(dimensions, brick_size=[1,4,1], circle_verts=16, type="TILE", detail=detail), "1x4 Tile "  + detail, loc=(offset, 2, 0))
        # new_objFromBmesh(7, make_tile(dimensions, brick_size=[2,4,1], circle_verts=16, type="TILE", detail=detail), "2x4 Tile "  + detail, loc=(offset*1.5, -0.2, 0))
        # new_objFromBmesh(7, make_tile(dimensions, brick_size=[1,8,1], circle_verts=16, type="TILE", detail=detail), "1x8 Tile "  + detail, loc=(offset, -4.4, 0))

    if not b280():
        open_layer(17)

    cm.brick_type = last_brick_type