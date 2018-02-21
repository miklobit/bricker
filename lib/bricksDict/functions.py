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
from mathutils.interpolate import poly_3d_calc
import math
import colorsys

# Blender imports
import bpy

# Rebrickr imports
from ...functions import *
from ..Brick import Bricks


def getMatAtFaceIdx(obj, face_idx):
    """ get material at target face index of object """
    if len(obj.material_slots) == 0:
        return ""
    face = obj.data.polygons[face_idx]
    slot = obj.material_slots[face.material_index]
    mat = slot.material
    matName = mat.name if mat else ""
    return matName


def getUVCoord(mesh, face, point, image):
    """ returns UV coordinate of target point in source mesh image texture
    mesh  -- mesh data from source object
    face  -- face object from mesh
    point -- coordinate of target point on source mesh
    image -- image texture for source mesh
    """
    # get active uv layer data
    uv_layer = mesh.uv_layers.active
    if uv_layer is None:
        return None
    uv = uv_layer.data
    # get 3D coordinates of face's vertices
    lco = [mesh.vertices[i].co for i in face.vertices]
    # get uv coordinates of face's vertices
    luv = [uv[i].uv for i in face.loop_indices]
    # calculate barycentric weights for point
    lwts = poly_3d_calc(lco, point)
    # multiply barycentric weights by uv coordinates
    uv_loc = sum((p*w for p,w in zip(luv,lwts)), Vector((0,0)))
    # ensure uv_loc is in range(0,1)
    # TODO: possibly approach this differently? currently, uv verts that are outside the image are wrapped to the other side
    uv_loc = Vector((uv_loc[0] % 1, uv_loc[1] % 1))
    # convert uv_loc in range(0,1) to uv coordinate
    image_size_x, image_size_y = image.size
    x_co = round(uv_loc.x * (image_size_x - 1))
    y_co = round(uv_loc.y * (image_size_y - 1))
    uv_coord = (x_co, y_co)

    # return resulting uv coordinate
    return Vector(uv_coord)


def getUVTextureData(obj):
    """ returns data of active uv texture for object """
    if len(obj.data.uv_textures) == 0:
        return None
    active_uv = obj.data.uv_textures.active
    if active_uv is None and len(obj.data.uv_textures) > 0:
        obj.data.uv_textures.active = obj.data.uv_textures[0]
        active_uv = obj.data.uv_textures.active
    return active_uv.data


def getFirstImgTexNode(obj):
    """ return first image texture found in object's material slots """
    img = None
    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        if not mat.use_nodes:
            return None
        active_node = mat.node_tree.nodes.active
        nodes_to_check = [active_node] + list(mat.node_tree.nodes)
        for node in nodes_to_check:
            if node and node.type == "TEX_IMAGE":
                img = node.image
                break
    return img


# reference: https://svn.blender.org/svnroot/bf-extensions/trunk/py/scripts/addons/uv_bake_texture_to_vcols.py
def getUVImages(obj):
    """ returns dictionary with duplicate pixel arrays for all UV textures in object """
    scn, cm, _ = getActiveContextInfo()
    # get list of images to store
    uv_tex_data = getUVTextureData(obj)
    images = [uv_tex.image for uv_tex in uv_tex_data] if uv_tex_data else []
    images.append(bpy.data.images.get(cm.uvImageName))
    images.append(getFirstImgTexNode(obj))
    # store images
    uv_images = {}
    for img in images:
        if not img or img.name in uv_images or not img.pixels:
            continue
        uv_images[img.name] = (img.size[0],
                               img.size[1],
                               img.pixels[:]
                               # Accessing pixels directly is far too slow.
                               #Copied to new array for massive performance-gain.
                               )
    return uv_images


# reference: https://svn.blender.org/svnroot/bf-extensions/trunk/py/scripts/addons/uv_bake_texture_to_vcols.py
def getPixel(pixels, uv_coord):
    """ get RGBA value for specified coordinate in UV image
    pixels    -- list of pixel data from UV texture image
    uv_coord  -- UV coordinate of desired pixel value
    """
    image_size_x, image_size_y, uv_pixels = uv_images[image.name]
    pixelNumber = (image_size_x * int(uv_coord.y)) + int(uv_coord.x)
    r = uv_pixels[pixelNumber*4 + 0]
    g = uv_pixels[pixelNumber*4 + 1]
    b = uv_pixels[pixelNumber*4 + 2]
    a = uv_pixels[pixelNumber*4 + 3]
    # gamma correct RGB value
    r, g, b, a = gammaCorrect([r, g, b, a], 2)
    return (r, g, b, a)


def getAverage(rgba0:Vector, rgba1:Vector, weight:float):
    """ returns weighted average of two rgba values """
    return (rgba1 * weight + rgba0) / (weight + 1)


def getFirstNode(mat, type="BSDF_DIFFUSE"):
    """ get first node in material of specified type """
    diffuse = None
    mat_nodes = mat.node_tree.nodes
    for node in mat_nodes:
        if node.type == type:
            diffuse = node
            break
    return diffuse


def createNewMaterial(model_name, rgba, rgba_vals):
    """ create new material with specified rgba values """
    scn, cm, _ = getActiveContextInfo()
    # get or create material with unique color
    min_diff = float("inf")
    r0, g0, b0, a0 = rgba
    for i in range(len(rgba_vals)):
        diff = distance(rgba, rgba_vals[i])
        if diff < min_diff and diff < cm.colorSnapAmount:
            min_diff = diff
            r0, g0, b0, a0 = rgba_vals[i]
            break
    mat_name = "Rebrickr_{}_mat_{}-{}-{}-{}".format(model_name, round(r0, 5), round(g0, 5), round(b0, 5), round(a0, 5))
    mat = bpy.data.materials.get(mat_name)
    mat_is_new = mat is None
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
    # set diffuse and transparency of material
    if scn.render.engine == "CYCLES":
        if mat_is_new:
            mat.use_nodes = True
            mat_nodes = mat.node_tree.nodes
            mat_links = mat.node_tree.links
            # a new material node tree already has a diffuse and material output node
            output = mat_nodes['Material Output']
            diffuse = mat_nodes['Diffuse BSDF']
            diffuse.inputs[0].default_value = rgba
        else:
            if not mat.use_nodes:
                mat.use_nodes = True
            diffuse = getFirstNode(mat, type="BSDF_DIFFUSE")
            if diffuse:
                rgba1 = diffuse.inputs[0].default_value
                newRGBA = getAverage(Vector(rgba), Vector(rgba1), mat.num_averaged)
                # if diffuse.inputs[0].is_linked:
                #     # TODO: read different types of input to the diffuse node
                diffuse.inputs[0].default_value = newRGBA
    else:
        if mat_is_new:
            mat.diffuse_color = rgba[:3]
            mat.diffuse_intensity = 1.0
            if a < 1.0:
                mat.use_transparency = True
                mat.alpha = rgba[3]
        else:
            if mat.use_nodes:
                mat.use_nodes = False
            r1, g1, b1 = mat.diffuse_color
            a1 = mat.alpha
            r2, g2, b2, a2 = getAverage(rgba, [r1, g1, b1, a1], mat.num_averaged)
            mat.diffuse_color = [r2, g2, b2]
            mat.alpha = a2
    mat.num_averaged += 1
    return mat_name


def getUVImage(obj, face_idx):
    """ returns UV image (priority to user settings, then face index, then first one found in object """
    scn, cm, _ = getActiveContextInfo()
    image = bpy.data.images.get(cm.uvImageName)
    if image is None and obj.data.uv_textures.active:
        image = obj.data.uv_textures.active.data[face_idx].image
    if image is None:
        image = getFirstImgTexNode(obj)
    return image


def getUVPixelColor(obj, face_idx, point, uv_images):
    """ get RGBA value for point in UV image at specified face index """
    if face_idx is None:
        return None
    # get closest material using UV map
    scn, cm, _ = getActiveContextInfo()
    face = obj.data.polygons[face_idx]
    # get uv_texture image for face
    image = getUVImage(obj, face_idx)
    if image is None:
        return None
    # get uv coordinate based on nearest face intersection
    uv_coord = getUVCoord(obj.data, face, point, image)
    # retrieve rgba value at uv coordinate
    rgba = getPixel(uv_images[image.name], uv_coord)
    return rgba


def getMaterialColor(matName):
    """ get RGBA value of material """
    mat = bpy.data.materials.get(matName)
    if mat is None:
        return None
    if mat.use_nodes:
        diffuse = getFirstNode(mat, type="BSDF_DIFFUSE")
        if diffuse:
            r, g, b, a = diffuse.inputs[0].default_value
        else:
            return None
    else:
        r, g, b = mat.diffuse_color
        intensity = mat.diffuse_intensity
        r = r * intensity
        g = g * intensity
        b = b * intensity
        a = mat.alpha if mat.use_transparency else 1.0
    return [r, g, b, a]


def getBrickRGBA(obj, face_idx, point, uv_images):
    """ returns RGBA value for brick """
    scn, cm, _ = getActiveContextInfo()
    if face_idx is None:
        return None
    # get material based on rgba value of UV image at face index
    if uv_images:
        origMatName = ""
        rgba = getUVPixelColor(obj, face_idx, Vector(point), uv_images)
    else:
        # get closest material using material slot of face
        origMatName = getMatAtFaceIdx(obj, face_idx)
        rgba = getMaterialColor(origMatName) if origMatName is not None else None
    return rgba, origMatName


def getDictKey(name):
    """ get dict key details of obj """
    dictKey = name.split("__")[1]
    dictLoc = strToList(dictKey)
    return dictKey, dictLoc


def getDetailsAndBounds(source):
    """ returns dimensions and bounds of source object """
    scn, cm, _ = getActiveContextInfo()
    source_details = bounds(source)
    zStep = getZStep(cm)
    dimensions = Bricks.get_dimensions(cm.brickHeight, zStep, cm.gap)
    return source_details, dimensions


def getArgumentsForBricksDict(cm, source=None, source_details=None, dimensions=None):
    """ returns arguments for makeBricksDict function """
    if source is None:
        source = bpy.data.objects.get(cm.source_name)
        if source is None: source = bpy.data.objects.get(cm.source_name + " (DO NOT RENAME)")
    if source_details is None or dimensions is None:
        source_details, dimensions = getDetailsAndBounds(source)
    if cm.brickType == "Custom":
        scn = bpy.context.scene
        customObj = bpy.data.objects[cm.customObjectName]
        oldLayers = list(scn.layers) # store scene layers for later reset
        setLayers(customObj.layers)
        select(customObj, active=customObj)
        bpy.ops.object.duplicate()
        customObj0 = scn.objects.active
        select(customObj0, active=customObj0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        customObj_details = bounds(customObj0)
        customData = customObj0.data
        bpy.data.objects.remove(customObj0, True)
        scale = cm.brickHeight/customObj_details.z.dist
        brickScale = Vector((scale * customObj_details.x.dist + dimensions["gap"],
                    scale * customObj_details.y.dist + dimensions["gap"],
                    scale * customObj_details.z.dist + dimensions["gap"]))
        setLayers(oldLayers)
    else:
        customData = None
        customObj_details = None
        brickScale = Vector((dimensions["width"] + dimensions["gap"],
                    dimensions["width"] + dimensions["gap"],
                    dimensions["height"]+ dimensions["gap"]))
    return source, source_details, dimensions, brickScale, customData, customObj_details
