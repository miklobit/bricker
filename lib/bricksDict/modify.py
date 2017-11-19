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

# Rebrickr imports
from ...functions.general import *

def addMaterialsToBricksDict(bricksDict, source):
    """ sets all matNames in bricksDict based on nearest_face_idx """
    for key in bricksDict.keys():
        nf = bricksDict[key]["nearest_face_idx"]
        nearestFaceExists = nf is not None
        if bricksDict[key]["draw"] and nearestFaceExists:
            f = source.data.polygons[nf]
            slot = source.material_slots[f.material_index]
            mat = slot.material
            matName = mat.name
            bricksDict[key]["mat_name"] = matName
    return bricksDict

def brickAvail(sourceBrick, brick):
    """ check brick is available to merge """
    scn = bpy.context.scene
    cm = scn.cmlist[scn.cmlist_index]
    n = cm.source_name
    Rebrickr_internal_mn = "Rebrickr_%(n)s_internal" % locals()
    if brick is not None:
        # This if statement ensures brick is present, brick isn't drawn already, and checks that brick materials match, or mergeInconsistentMats is True, or one of the mats is "" (internal)
        if brick["draw"] and not brick["attempted_merge"] and (sourceBrick["mat_name"] == brick["mat_name"] or sourceBrick["mat_name"] == "" or brick["mat_name"] == "" or cm.mergeInconsistentMats):
            return True
    return False

def getNextBrick(bricks, loc, x, y, z=0):
    """ get next brick at loc + (x,y,z) """
    try:
        key = listToStr([loc[0] + x, loc[1] + y, loc[2] + z])
        return bricks[key]
    except KeyError:
        return None

def plateIsBrick(brickD, bricksD, loc, x, y, h=3):
    """ check that [h-1] locations above loc are available """
    for i in range(1,h):
        if not brickAvail(brickD, getNextBrick(bricksD, loc, x, y, i)):
            return False
    return True

def canBeJoined(bricksD, loc, origIsBrick, key, i, j):
    curBrickD = bricksD[key]
    nextBrickD = getNextBrick(bricksD, loc, i, j)
    spotAvail = brickAvail(curBrickD, nextBrickD)
    canBeBrick = not origIsBrick or plateIsBrick(curBrickD, bricksD, loc, i, j)
    return spotAvail and canBeBrick

def updateBrickSizes(cm, bricksD, key, keys, loc, origIsBrick, brickSizes, zStep, maxL):
    """ update 'brickSizes' with available brick sizes surrounding bricksD[key] """
    newMax1 = maxL[1]
    breakOuter = False
    for i in range(0, maxL[0]):
        for j in range(0, maxL[1]):
            # break case 1
            if j >= newMax1:
                break
            # break case 2
            elif not canBeJoined(bricksD, loc, origIsBrick, key, i, j):
                if j == 0: breakOuter = True
                else:      newMax1 = j
                break
            # else, append current brick size to brickSizes
            else:
                if origIsBrick:
                    newSize = [i+1, j+1, 3]
                else:
                    newSize = [i+1, j+1, zStep]
                newLoc = [i + loc[0], j + loc[1], loc[2]]
                if newSize not in brickSizes and listToStr(newLoc) in keys and [newSize[0],newSize[1]] in bpy.props.Rebrickr_legal_brick_sizes:
                    brickSizes.append(newSize)
        if breakOuter: break

def attemptMerge(cm, bricksD, key, keys, loc, origIsBrick, brickSizes, zStep, randState, preferLargest=False):
    """ attempt to merge bricksD[key] with adjacent bricks """

    if cm.brickType != "Custom":
        updateBrickSizes(cm, bricksD, key, keys, loc, origIsBrick, brickSizes, zStep, [cm.maxWidth, cm.maxDepth])
        updateBrickSizes(cm, bricksD, key, keys, loc, origIsBrick, brickSizes, zStep, [cm.maxDepth, cm.maxWidth])

    order = randState.randint(0,2)
    # sort brick types from smallest to largest
    if preferLargest:
        brickSizes.sort(key=lambda x: (x[2], x[order] + x[(order+1)%2]))
    else:
        brickSizes.sort(key=lambda x: (x[2], x[order], x[(order+1)%2]))
    # grab the biggest brick type and store to bricksD
    brickSize = brickSizes[-1]
    bricksD[key]["size"] = brickSize

    # Iterate through merged bricks to set brick parents
    startingLoc = sum(loc)
    for x in range(loc[0], brickSize[0] + loc[0]):
        for y in range(loc[1], brickSize[1] + loc[1]):
            for z in range(loc[2], brickSize[2] + loc[2]):
                # TODO: figure out what this does
                if cm.brickType in ["Bricks", "Custom"] and z > loc[2]:
                    continue
                # get brick at x,y location
                k0 = listToStr([x,y,z])
                curBrick = bricksD[k0]
                curBrick["attempted_merge"] = True
                 # checks that x,y,z refer to original brick
                if (x + y + z) == startingLoc:
                    # set original brick as parent_brick
                    curBrick["parent_brick"] = "self"
                else:
                    # point deleted brick to original brick
                    curBrick["parent_brick"] = key

    return brickSize

def checkExposure(bricksD, x, y, z, direction:int=1):
    isExposed = False
    try:
        valKeysChecked = []
        k0 = listToStr([x,y,z])
        val = bricksD[k0]["val"]
        if val == 0:
            isExposed = True
        # Check bricks on Z axis [above or below depending on 'direction'] this brick until shell (1) hit. If ouside (0) hit first, [top or bottom depending on 'direction'] is exposed
        elif val > 0 and val < 1:
            zz = z
            while val > 0 and val < 1:
                zz += direction
                # NOTE: if key does not exist, we will be sent to 'except'
                k1 = listToStr([x,y,zz])
                valKeysChecked.append(k1)
                val = bricksD[valKeysChecked[-1]]["val"]
                if val == 0:
                    isExposed = True
    except KeyError:
        isExposed = True
    # if outside (0) hit before shell (1) [above or below depending on 'direction'] exposed brick, set all inside (0 < x < 1) values in-between to ouside (0)
    if isExposed and len(valKeysChecked) > 0:
        for k in valKeysChecked:
            val = bricksD[k]["val"] = 0
    return isExposed

def getBrickExposure(cm, bricksD, key, loc=None):
    topExposed = False
    botExposed = False

    if loc is None:
        # get location of brick
        loc = strToList(key)

    # get size of brick
    size = bricksD[key]["size"]

    # set z-indices
    idxZb = loc[2] - 1
    if cm.brickType == "Bricks and Plates" and size[2] == 3:
        idxZa = loc[2] + 3
    else:
        idxZa = loc[2] + 1

    # Iterate through merged bricks to check top and bottom exposure
    for x in range(loc[0], size[0] + loc[0]):
        for y in range(loc[1], size[1] + loc[1]):
            for z in range(loc[2], size[2] + loc[2]):
                # TODO: figure out what this does
                if cm.brickType in ["Bricks", "Custom"] and z > loc[2]:
                    continue
                # get brick at x,y location
                k0 = listToStr([x,y,z])
                curBrick = bricksD[k0]
                # check if brick top or bottom is exposed
                if curBrick["val"] == 1 or (cm.brickType == "Bricks and Plates" and size[2] == 3):
                    returnVal0 = checkExposure(bricksD, x, y, idxZa, 1)
                    if returnVal0: topExposed = True
                    returnVal1 = checkExposure(bricksD, x, y, idxZb, 1) # TODO: test -1 for last argument here
                    if returnVal1: botExposed = True

    return topExposed, botExposed