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
# NONE!

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
        return bricks[str(loc[0] + x) + "," + str(loc[1] + y) + "," + str(loc[2] + z)]
    except KeyError:
        return None

def plateIsBrick(brickD, bricksD, loc, x, y, h=3):
    for i in range(1,h):
        if not brickAvail(brickD, getNextBrick(bricksD, loc, x, y, i)):
            return False
    return True

def attemptMerge(cm, bricksD, key, loc, isBrick, brickSizes, bt2, randState):
    brickD = bricksD[key]

    nextBrick0 = getNextBrick(bricksD, loc, 1, 0)
    canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 1, 0)
    if brickAvail(brickD, nextBrick0) and canBeBrick and cm.maxBrickScale1 > 1 and cm.brickType != "Custom":
        nextBrick = getNextBrick(bricksD, loc, 2, 0)
        canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 2, 0)
        if brickAvail(brickD, nextBrick) and canBeBrick and cm.maxBrickScale1 > 2:
            if isBrick:
                brickSizes.append([3,1,3])
            else:
                brickSizes.append([3,1,bt2])
            nextBrick = getNextBrick(bricksD, loc, 3, 0)
            canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 3, 0)
            if brickAvail(brickD, nextBrick) and canBeBrick and cm.maxBrickScale1 > 3:
                if isBrick:
                    brickSizes.append([4,1,3])
                else:
                    brickSizes.append([4,1,bt2])
                nextBrick0 = getNextBrick(bricksD, loc, 4, 0)
                nextBrick1 = getNextBrick(bricksD, loc, 5, 0)
                canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 4, 0) and plateIsBrick(brickD, bricksD, loc, 5, 0)
                if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale1 > 5:
                    if isBrick:
                        brickSizes.append([6,1,3])
                    else:
                        brickSizes.append([6,1,bt2])
                    nextBrick0 = getNextBrick(bricksD, loc, 6, 0)
                    nextBrick1 = getNextBrick(bricksD, loc, 7, 0)
                    canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 6, 0) and plateIsBrick(brickD, bricksD, loc, 7, 0)
                    if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale1 > 7:
                        if isBrick:
                            brickSizes.append([8,1,3])
                        else:
                            brickSizes.append([8,1,bt2])
    nextBrick1 = getNextBrick(bricksD, loc, 0, 1)
    canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 0, 1)
    if brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale1 > 1 and cm.brickType != "Custom":
        if isBrick:
            brickSizes.append([1,2,3])
        else:
            brickSizes.append([1,2,bt2])
        nextBrick = getNextBrick(bricksD, loc, 0, 2)
        canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 0, 2)
        if brickAvail(brickD, nextBrick) and canBeBrick and cm.maxBrickScale1 > 2:
            if isBrick:
                brickSizes.append([1,3,3])
            else:
                brickSizes.append([1,3,bt2])
            nextBrick = getNextBrick(bricksD, loc, 0, 3)
            canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 0, 3)
            if brickAvail(brickD, nextBrick) and canBeBrick and cm.maxBrickScale1 > 3:
                if isBrick:
                    brickSizes.append([1,4,3])
                else:
                    brickSizes.append([1,4,bt2])
                nextBrick0 = getNextBrick(bricksD, loc, 0, 4)
                nextBrick1 = getNextBrick(bricksD, loc, 0, 5)
                canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 4) and plateIsBrick(brickD, bricksD, loc, 0, 5))
                if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale1 > 5:
                    if isBrick:
                        brickSizes.append([1,6,3])
                    else:
                        brickSizes.append([1,6,bt2])
                    nextBrick0 = getNextBrick(bricksD, loc, 0, 6)
                    nextBrick1 = getNextBrick(bricksD, loc, 0, 7)
                    canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 6) and plateIsBrick(brickD, bricksD, loc, 0, 7))
                    if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale1 > 7:
                        if isBrick:
                            brickSizes.append([1,8,3])
                        else:
                            brickSizes.append([1,8,bt2])
    nextBrick2 = getNextBrick(bricksD, loc, 1, 1)
    canBeBrick = not isBrick or plateIsBrick(brickD, bricksD, loc, 1, 1)
    if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and canBeBrick and cm.maxBrickScale2 > 1 and cm.brickType != "Custom":
        if isBrick:
            brickSizes.append([2,2,3])
        else:
            brickSizes.append([2,2,bt2])
        nextBrick0 = getNextBrick(bricksD, loc, 0, 2)
        nextBrick1 = getNextBrick(bricksD, loc, 1, 2)
        canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 2) and plateIsBrick(brickD, bricksD, loc, 1, 2))
        if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale2 > 2:
            if isBrick:
                brickSizes.append([2,3,3])
            else:
                brickSizes.append([2,3,bt2])
            nextBrick0 = getNextBrick(bricksD, loc, 0, 3)
            nextBrick1 = getNextBrick(bricksD, loc, 1, 3)
            canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 3) and plateIsBrick(brickD, bricksD, loc, 1, 3))
            if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale2 > 3:
                if isBrick:
                    brickSizes.append([2,4,3])
                else:
                    brickSizes.append([2,4,bt2])
                nextBrick0 = getNextBrick(bricksD, loc, 0, 4)
                nextBrick1 = getNextBrick(bricksD, loc, 1, 4)
                nextBrick2 = getNextBrick(bricksD, loc, 0, 5)
                nextBrick3 = getNextBrick(bricksD, loc, 1, 5)
                canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 4) and plateIsBrick(brickD, bricksD, loc, 1, 4) and plateIsBrick(brickD, bricksD, loc, 0, 5) and plateIsBrick(brickD, bricksD, loc, 1, 5))
                if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and brickAvail(brickD, nextBrick3) and canBeBrick and cm.maxBrickScale2 > 5:
                    if isBrick:
                        brickSizes.append([2,6,3])
                    else:
                        brickSizes.append([2,6,bt2])
                    nextBrick0 = getNextBrick(bricksD, loc, 0, 6)
                    nextBrick1 = getNextBrick(bricksD, loc, 1, 6)
                    nextBrick2 = getNextBrick(bricksD, loc, 0, 7)
                    nextBrick3 = getNextBrick(bricksD, loc, 1, 7)
                    canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 6) and plateIsBrick(brickD, bricksD, loc, 1, 6) and plateIsBrick(brickD, bricksD, loc, 0, 7) and plateIsBrick(brickD, bricksD, loc, 1, 7))
                    if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and brickAvail(brickD, nextBrick3) and canBeBrick and cm.maxBrickScale2 > 7:
                        if isBrick:
                            brickSizes.append([2,8,3])
                        else:
                            brickSizes.append([2,8,bt2])
                        nextBrick0 = getNextBrick(bricksD, loc, 0, 8)
                        nextBrick1 = getNextBrick(bricksD, loc, 1, 8)
                        nextBrick2 = getNextBrick(bricksD, loc, 0, 9)
                        nextBrick3 = getNextBrick(bricksD, loc, 1, 9)
                        canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 0, 8) and plateIsBrick(brickD, bricksD, loc, 1, 8) and plateIsBrick(brickD, bricksD, loc, 0, 9) and plateIsBrick(brickD, bricksD, loc, 1, 9))
                        if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and brickAvail(brickD, nextBrick3) and canBeBrick and cm.maxBrickScale2 > 9:
                            if isBrick:
                                brickSizes.append([2,10,3])
                            else:
                                brickSizes.append([2,10,bt2])
        nextBrick0 = getNextBrick(bricksD, loc, 2, 0)
        nextBrick1 = getNextBrick(bricksD, loc, 2, 1)
        canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 2, 0) and plateIsBrick(brickD, bricksD, loc, 2, 1))
        if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale2 > 2:
            if isBrick:
                brickSizes.append([3,2,3])
            else:
                brickSizes.append([3,2,bt2])
            nextBrick0 = getNextBrick(bricksD, loc, 3, 0)
            nextBrick1 = getNextBrick(bricksD, loc, 3, 1)
            canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 3, 0) and plateIsBrick(brickD, bricksD, loc, 3, 1))
            if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and canBeBrick and cm.maxBrickScale2 > 3:
                if isBrick:
                    brickSizes.append([4,2,3])
                else:
                    brickSizes.append([4,2,bt2])
                nextBrick0 = getNextBrick(bricksD, loc, 4, 0)
                nextBrick1 = getNextBrick(bricksD, loc, 4, 1)
                nextBrick2 = getNextBrick(bricksD, loc, 5, 0)
                nextBrick3 = getNextBrick(bricksD, loc, 5, 1)
                canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 4, 0) and plateIsBrick(brickD, bricksD, loc, 4, 1) and plateIsBrick(brickD, bricksD, loc, 5, 0) and plateIsBrick(brickD, bricksD, loc, 5, 1))
                if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and brickAvail(brickD, nextBrick3) and canBeBrick and cm.maxBrickScale2 > 5:
                    if isBrick:
                        brickSizes.append([6,2,3])
                    else:
                        brickSizes.append([6,2,bt2])
                    nextBrick0 = getNextBrick(bricksD, loc, 6, 0)
                    nextBrick1 = getNextBrick(bricksD, loc, 6, 1)
                    nextBrick2 = getNextBrick(bricksD, loc, 7, 0)
                    nextBrick3 = getNextBrick(bricksD, loc, 7, 1)
                    canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 6, 0) and plateIsBrick(brickD, bricksD, loc, 6, 1) and plateIsBrick(brickD, bricksD, loc, 7, 0) and plateIsBrick(brickD, bricksD, loc, 7, 1))
                    if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and brickAvail(brickD, nextBrick3) and canBeBrick and cm.maxBrickScale2 > 7:
                        if isBrick:
                            brickSizes.append([8,2,3])
                        else:
                            brickSizes.append([8,2,bt2])
                        nextBrick0 = getNextBrick(bricksD, loc, 8, 0)
                        nextBrick1 = getNextBrick(bricksD, loc, 8, 1)
                        nextBrick2 = getNextBrick(bricksD, loc, 9, 0)
                        nextBrick3 = getNextBrick(bricksD, loc, 9, 1)
                        canBeBrick = not isBrick or (plateIsBrick(brickD, bricksD, loc, 8, 0) and plateIsBrick(brickD, bricksD, loc, 8, 1) and plateIsBrick(brickD, bricksD, loc, 9, 0) and plateIsBrick(brickD, bricksD, loc, 9, 1))
                        if brickAvail(brickD, nextBrick0) and brickAvail(brickD, nextBrick1) and brickAvail(brickD, nextBrick2) and brickAvail(brickD, nextBrick3) and canBeBrick and cm.maxBrickScale2 > 9:
                            if isBrick:
                                brickSizes.append([10,2,3])
                            else:
                                brickSizes.append([10,2,bt2])

    # sort brick types from smallest to largest
    order = randState.randint(1,2)
    if cm.brickType == "Bricks and Plates":
        brickSizes.sort(key=lambda x: (x[2], x[order-1]))
    else:
        brickSizes.sort(key=lambda x: x[order-1])
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
                curBrick = bricksD["%(x)s,%(y)s,%(z)s" % locals()]
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
        val = bricksD["%(x)s,%(y)s,%(z)s" % locals()]["val"]
        if val == 0:
            isExposed = True
        # Check bricks on Z axis [above or below depending on 'direction'] this brick until shell (2) hit. If ouside (0) hit first, [top or bottom depending on 'direction'] is exposed
        elif val < 1 and val > 0:
            zz = z
            while val < 1 and val > 0:
                zz += direction
                # NOTE: if key does not exist, we will be sent to 'except'
                valKeysChecked.append("%(x)s,%(y)s,%(zz)s" % locals())
                val = bricksD[valKeysChecked[-1]]["val"]
                if val == 0:
                    isExposed = True
    except KeyError:
        isExposed = True
    # if outside (0) hit before shell (2) [above or below depending on 'direction'] exposed brick, set all inside (0 < x < 1) values in-between to ouside (0)
    if isExposed and len(valKeysChecked) > 0:
        for k in valKeysChecked:
            val = bricksD[k]["val"] = 0
    return isExposed

def getBrickExposure(cm, bricksD, key, loc=None):
    topExposed = False
    botExposed = False

    if loc is None:
        # get location of brick
        loc = key.split(",")
        for j in range(len(loc)):
            loc[j] = int(loc[j])

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
                curBrick = bricksD["%(x)s,%(y)s,%(z)s" % locals()]
                # check if brick top or bottom is exposed
                if curBrick["val"] == 2 or (cm.brickType == "Bricks and Plates" and size[2] == 3):
                    returnVal0 = checkExposure(bricksD, x, y, idxZa, 1)
                    if returnVal0: topExposed = True
                    returnVal1 = checkExposure(bricksD, x, y, idxZb, 1) # TODO: test -1 for last argument here
                    if returnVal1: botExposed = True

    return topExposed, botExposed
