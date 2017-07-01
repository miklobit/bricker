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
import bmesh
import math
from .crossSection import slices, drawBMesh
from .mesh_generate import *
from .common_functions import *
from mathutils import Vector, geometry
props = bpy.props

def writeBinvox(obj):
    ''' creates binvox file and returns filepath '''

    scn = bpy.context.scene
    binvoxPath = props.binvoxPath
    projectName = bpy.path.display_name_from_filepath(bpy.data.filepath).replace(" ", "_")

    # export obj to obj_exports_folder
    objExportPath = None # TODO: Write this code

    # send
    resolution = props.voxelResolution
    outputFilePath = props.final_output_folder + "/" + projectName + "_" + scn.voxelResolution + ".obj"
    binvoxCall = "'%(binvoxPath)s' -pb -d %(resolution)s '%(objExportPath)s'" % locals()

    subprocess.call()

    return binvoxPath

def confirmList(objList):
    """ if single object passed, convert to list """
    if type(objList) != list:
        objList = [objList]
    return objList

def getBrickDimensions(height):
    scale = height/9.6
    brick_dimensions = {}
    brick_dimensions["height"] = scale*9.6
    brick_dimensions["width"] = scale*8
    brick_dimensions["stud_height"] = scale*1.8
    brick_dimensions["stud_diameter"] = scale*4.8
    brick_dimensions["stud_radius"] = scale*2.4
    brick_dimensions["stud_offset"] = (brick_dimensions["height"] / 2) + (brick_dimensions["stud_height"] / 2)
    brick_dimensions["logo_width"] = scale*3.74
    brick_dimensions["logo_offset"] = (brick_dimensions["height"] / 2) + (brick_dimensions["stud_height"])
    return brick_dimensions

def bounds(obj, local=False):

    local_coords = obj.bound_box[:]
    om = obj.matrix_world

    if not local:
        worldify = lambda p: om * Vector(p[:])
        coords = [worldify(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])

    push_axis = []
    for (axis, _list) in zip('xyz', rotated):
        info = lambda: None
        info.max = max(_list)
        info.min = min(_list)
        info.mid = (info.min + info.max) / 2
        info.distance = info.max - info.min
        push_axis.append(info)

    import collections

    originals = dict(zip(['x', 'y', 'z'], push_axis))

    o_details = collections.namedtuple('object_details', 'x y z')
    return o_details(**originals)

def is_inside(face, co):
    return bmesh.geometry.intersect_face_point(face, co)

def getMatrix(z, obj, dimensions):
    # get obj mesh details
    source_details = bounds(obj)
    # initialize variables
    # xScale = math.floor((source_details.x.distance * obj.scale[0])/dimensions["width"])
    # yScale = math.floor((source_details.y.distance * obj.scale[1])/dimensions["width"])
    xScale = math.floor((source_details.x.distance)/dimensions["width"])
    yScale = math.floor((source_details.y.distance)/dimensions["width"])
    matrix = [[None for y in range(yScale+1)] for x in range(xScale+1)]
    # set matrix values
    for x in range(xScale+1):
        for y in range(yScale+1):
            xLoc = ((x)/(xScale/2)) + source_details.x.min# * obj.matrix_world)
            yLoc = ((y)/(yScale/2)) + source_details.y.min
            matrix[x][y] = (xLoc, yLoc, z)
    return matrix

def add_vertex_to_intersection(e1, e2):
    edges = [e for e in bm.edges if e.select]

    if len(edges) == 2:
        [[v1, v2], [v3, v4]] = [[v.co for v in e.verts] for e in edges]

        iv = geometry.intersect_line_line(v1, v2, v3, v4)
        iv = (iv[0] + iv[1]) / 2
        bm.verts.new(iv)
        bmesh.update_edit_mesh(me)

def ccw(A,B,C):
    return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def getIntersectedEdgeVerts(bm_tester, bm_subject):
    intersectedEdgeVertInts = []
    for e1 in bm_tester.edges:
        for e2 in bm_subject.edges:
            v1 = e1.verts[0].co
            v2 = e1.verts[1].co
            v3 = e2.verts[0].co
            v4 = e2.verts[1].co
            if intersect(v1, v2, v3, v4):
                for v in e2.verts:
                    co = []
                    # convert co float values to ints
                    for i in v.co.to_tuple():
                        co.append(int(i*100000))
                    intersectedEdgeVertInts.append(tuple(co))
    # remove duplicates in intersectedEdgeVerts
    uniquify(intersectedEdgeVertInts)
    # convert co int values back to floats
    uniquifiedEdgeVertFloats = []
    for co in intersectedEdgeVertInts:
        co = list(co)
        for i in range(len(co)):
            co[i] = co[i]/100000
        uniquifiedEdgeVertFloats.append(tuple(co))
    return uniquifiedEdgeVertFloats

def addItemToCMList(name):
    scn = bpy.context.scene
    for item in scn.cmlist:
        if scn.cmlist[scn.cmlist_index].source_object == item.name:
            return False
    item = scn.cmlist.add()
    item.id = len(scn.cmlist)
    item.name = name # assign name of selected object
    item.source_object = name
    scn.cmlist_index = (len(scn.cmlist)-1)
    return True

def importLogo():
    """ import logo object from legoizer addon folder """
    addonsPath = bpy.utils.user_resource('SCRIPTS', "addons")
    legoizer = props.addon_name
    logoObjPath = "%(addonsPath)s/%(legoizer)s/lego_logo.obj" % locals()
    bpy.ops.import_scene.obj(filepath=logoObjPath)
    logoObj = bpy.context.selected_objects[0]
    return logoObj

def merge(bricks):
    return

def makeBricks(slices, refBrick, dimensions, source):
    """ Make bricks """
    scn = bpy.context.scene
    # initialize temporary object
    tempMesh = bpy.data.meshes.new('tempM')
    tempObj = bpy.data.objects.new('temp', tempMesh)

    # # assemble coordinates for each layer into coList
    # coList = []
    # for bm in slices:
    #     drawBMesh(bm)
    #     bm.verts.ensure_lookup_table()
    #     if len(bm.verts) > 2:
    #         z = bm.verts[0].co.z
    #         matrix = getMatrix(z, source, dimensions)
    #         face = bm.faces.new(bm.verts)
    #         for i in range(len(matrix)):
    #             for co in matrix[i]:
    #                 if is_inside(face, co):
    #                     coList.append(co)
    #     else:
    #         # TODO: If the layer has less than three verts, figure out a way to still do the calculations without creating a face
    #         pass
    #
    # bpy.data.objects.remove(tempObj)

    # get source details
    source_details = bounds(source)
    res = max([source_details.x.distance, source_details.y.distance])
    lScale = res // dimensions["width"]
    # for each slice
    coList = []
    for bm in slices:
        # drawBMesh(bm) # draw the slice (for testing purposes)
        bm.verts.ensure_lookup_table()
        z = bm.verts[0].co.z
        # create lattice bmesh
        # TODO: lattice BM can be created outside of for loop and transformed each time, if that's more efficient
        latticeBM = make2DLattice(int(lScale), res - (lScale % 1), (source_details.x.mid, source_details.y.mid, z))
        # drawBMesh(latticeBM) # draw the slice (for testing purposes)
        coListNew = getIntersectedEdgeVerts(bm, latticeBM)
        print("len(coListNew): " + str(len(coListNew)))
        coList += coListNew

    # make bricks at determined locations
    bricks = []
    # coList = [(0.1,0.1,0.1),(-0.1,-0.1,-0.1)]
    for i,co in enumerate(coList):
        brickMesh = bpy.data.meshes.new('LEGOizer_brickMesh_' + str(i+1))
        brick = bpy.data.objects.new('LEGOizer_brick_' + str(i+1), brickMesh)
        brick.location = Vector(co)
        brick.data = refBrick.data
        bpy.context.scene.objects.link(brick)
        bricks.append(brick)
    bpy.context.scene.update()
    # add bricks to LEGOizer_bricks group
    select(bricks, active=bricks[0])
    n = scn.cmlist[scn.cmlist_index].source_object
    LEGOizer_bricks = 'LEGOizer_%(n)s_bricks' % locals()
    if not groupExists(LEGOizer_bricks):
        bpy.ops.group.create(name=LEGOizer_bricks)
    else:
        bpy.data.groups.remove(group=bpy.data.groups[LEGOizer_bricks], do_unlink=True)
        bpy.ops.group.create(name=LEGOizer_bricks)
    # return list of created objects
    return bricks
