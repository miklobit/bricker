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
import time

# Blender imports
import bpy
from bpy.types import Operator

# Module imports
from .brick import *
from .bricksdict import *
from .common import *
from .brickify_utils import create_new_bricks
from .general import *
from .logo_obj import get_logo
from ..operators.bevel import BRICKER_OT_bevel


def draw_updated_bricks(cm, bricksdict, keys_to_update, action="redrawing", select_created=True, temp_brick=False):
    if len(keys_to_update) == 0: return
    if not is_unique(keys_to_update): raise ValueError("keys_to_update cannot contain duplicate values")
    if action is not None:
        print("[Bricker] %(action)s..." % locals())
    # get arguments for create_new_bricks
    source = cm.source_obj
    source_details, dimensions = get_details_and_bounds(source, cm)
    n = source.name
    parent = cm.parent_obj
    action = "UPDATE_MODEL"
    # actually draw the bricks
    _, bricks_created = create_new_bricks(source, parent, source_details, dimensions, action, cm=cm, bricksdict=bricksdict, keys=keys_to_update, clear_existing_collection=False, select_created=select_created, print_status=False, temp_brick=temp_brick, redraw=True)
    # link new bricks to scene
    if not b280():
        for brick in bricks_created:
            safe_link(brick)
    # add bevel if it was previously added
    if cm.bevel_added and not temp_brick:
        bricks = get_bricks(cm)
        BRICKER_OT_bevel.run_bevel_action(bricks, cm)


def verify_all_brick_exposures(scn, zstep, orig_loc, bricksdict, decriment=0, z_neg=False, z_pos=False):
    dlocs = []
    if not z_neg:
        dlocs.append((orig_loc[0], orig_loc[1], orig_loc[2] + decriment))
    if not z_pos:
        dlocs.append((orig_loc[0], orig_loc[1], orig_loc[2] - 1))
    # double check exposure of bricks above/below new adjacent brick
    for dloc in dlocs:
        k = list_to_str(dloc)
        try:
            brick_d = bricksdict[k]
        except KeyError:
            continue
        parent_key = k if brick_d["parent"] == "self" else brick_d["parent"]
        if parent_key is not None:
            set_all_brick_exposures(bricksdict, zstep, parent_key)
    return bricksdict


def get_available_types(by="SELECTION", include_sizes=[]):
    items = []
    legal_bs = bpy.props.bricker_legal_brick_sizes
    scn = bpy.context.scene
    objs = bpy.context.selected_objects if by == "SELECTION" else [bpy.context.active_object]
    obj_names_dict = create_obj_names_dict(objs)
    bricksdicts = get_bricksdicts_from_objs(obj_names_dict.keys())
    invalid_items = []
    for cm_id in obj_names_dict.keys():
        cm = get_item_by_id(scn.cmlist, cm_id)
        brick_type = cm.brick_type
        bricksdict = bricksdicts[cm_id]
        obj_sizes = []
        # check that custom_objects are valid
        for idx in range(3):
            target_type = "CUSTOM " + str(idx + 1)
            warning_msg = custom_valid_object(cm, target_type=target_type, idx=idx)
            if warning_msg is not None and iter_from_type(target_type) not in invalid_items:
                invalid_items.append(iter_from_type(target_type))
        # build items list
        for obj_name in obj_names_dict[cm_id]:
            dkey = get_dict_key(obj_name)
            obj_size = bricksdict[dkey]["size"]
            if obj_size in obj_sizes:
                continue
            obj_sizes.append(obj_size)
            if obj_size[2] not in (1, 3): raise Exception("Custom Error Message: obj_size not in (1, 3)")
            # build items
            items += [iter_from_type(typ) for typ in legal_bs[3] if include_sizes == "ALL" or obj_size[:2] in legal_bs[3][typ] + include_sizes]
            if flat_brick_type(brick_type):
                items += [iter_from_type(typ) for typ in legal_bs[1] if include_sizes == "ALL" or obj_size[:2] in legal_bs[1][typ] + include_sizes]
    # uniquify items
    items = uniquify2(items, inner_type=tuple)
    # remove invalid items
    for item in invalid_items:
        remove_item(items, item)
    # sort items
    items.sort(key=lambda k: k[0])
    # return items, or null if items was empty
    return items if len(items) > 0 else [("NULL", "Null", "")]


def update_brick_size_and_dict(dimensions, source_name, bricksdict, brick_size, key, loc, dec=0, cur_height=None, cur_type=None, target_height=None, target_type=None, created_from=None):
    brick_d = bricksdict[key]
    assert target_height is not None or target_type is not None
    target_height = target_height or (1 if target_type in get_brick_types(height=1) else 3)
    assert cur_height is not None or cur_type is not None
    cur_height = cur_height or (1 if cur_type in get_brick_types(height=1) else 3)
    # adjust brick size if changing type from 3 tall to 1 tall
    if cur_height == 3 and target_height == 1:
        brick_size[2] = 1
        for x in range(brick_size[0]):
            for y in range(brick_size[1]):
                for z in range(1, cur_height):
                    new_loc = [loc[0] + x, loc[1] + y, loc[2] + z - dec]
                    new_key = list_to_str(new_loc)
                    bricksdict[new_key]["parent"] = None
                    bricksdict[new_key]["draw"] = False
                    set_cur_brick_val(bricksdict, new_loc, new_key, action="REMOVE")
    # adjust brick size if changing type from 1 tall to 3 tall
    elif cur_height == 1 and target_height == 3:
        brick_size[2] = 3
        full_d = Vector((dimensions["width"], dimensions["width"], dimensions["height"]))
        # update bricks dict entries above current brick
        for x in range(brick_size[0]):
            for y in range(brick_size[1]):
                for z in range(1, target_height):
                    new_loc = [loc[0] + x, loc[1] + y, loc[2] + z]
                    new_key = list_to_str(new_loc)
                    # create new bricksdict entry if it doesn't exist
                    if new_key not in bricksdict:
                        bricksdict = create_addl_bricksdict_entry(source_name, bricksdict, key, new_key, full_d, x, y, z)
                    # update bricksdict entry to point to new brick
                    bricksdict[new_key]["parent"] = key
                    bricksdict[new_key]["created_from"] = created_from
                    bricksdict[new_key]["draw"] = True
                    bricksdict[new_key]["mat_name"] = brick_d["mat_name"] if bricksdict[new_key]["mat_name"] == "" else bricksdict[new_key]["mat_name"]
                    bricksdict[new_key]["near_face"] = bricksdict[new_key]["near_face"] or brick_d["near_face"]
                    bricksdict[new_key]["near_intersection"] = bricksdict[new_key]["near_intersection"] or tuple(brick_d["near_intersection"])
                    if bricksdict[new_key]["val"] == 0:
                        set_cur_brick_val(bricksdict, new_loc, new_key)
    return brick_size


def create_addl_bricksdict_entry(source_name, bricksdict, source_key, key, full_d, x, y, z):
    brick_d = bricksdict[source_key]
    new_name = "Bricker_%(source_name)s__%(key)s" % locals()
    new_co = (Vector(brick_d["co"]) + vec_mult(Vector((x, y, z)), full_d)).to_tuple()
    bricksdict[key] = create_bricksdict_entry(
        name=              new_name,
        loc=               str_to_list(key),
        co=                new_co,
        near_face=         brick_d["near_face"],
        near_intersection= tuple(brick_d["near_intersection"]),
        mat_name=          brick_d["mat_name"],
    )
    return bricksdict


def get_bricksdicts_from_objs(obj_names):
    scn = bpy.context.scene
    # initialize bricksdicts
    bricksdicts = {}
    for cm_id in obj_names:
        cm = get_item_by_id(scn.cmlist, cm_id)
        if cm is None: continue
        # get bricksdict from cache
        bricksdict = get_bricksdict(cm)
        # add to bricksdicts
        bricksdicts[cm_id] = bricksdict
    return bricksdicts


def set_cur_brick_val(bricksdict, loc, key=None, action="ADD"):
    key = key or list_to_str(loc)
    adj_brick_vals = get_adj_keys_and_brick_vals(bricksdict, loc=loc)[1]
    if action == "ADD" and (0 in adj_brick_vals or len(adj_brick_vals) < 6 or min(adj_brick_vals) == 1):
        new_val = 1
    elif action == "REMOVE":
        new_val = 0 if 0 in adj_brick_vals or len(adj_brick_vals) < 6 else max(adj_brick_vals)
    else:
        new_val = max(adj_brick_vals) - 0.01
    bricksdict[key]["val"] = new_val


def get_adj_keys_and_brick_vals(bricksdict, loc=None, key=None):
    assert loc or key
    x, y, z = loc or get_dict_loc(bricksdict, key)
    adj_keys = [list_to_str((x+1, y, z)),
               list_to_str((x-1, y, z)),
               list_to_str((x, y+1, z)),
               list_to_str((x, y-1, z)),
               list_to_str((x, y, z+1)),
               list_to_str((x, y, z-1))]
    adj_brick_vals = []
    for k in adj_keys.copy():
        try:
            adj_brick_vals.append(bricksdict[k]["val"])
        except KeyError:
            remove_item(adj_keys, k)
    return adj_keys, adj_brick_vals


def get_used_sizes():
    scn = bpy.context.scene
    items = [("NONE", "None", "")]
    for cm in scn.cmlist:
        if not cm.brick_sizes_used:
            continue
        sort_by = lambda k: (str_to_list(k)[2], str_to_list(k)[0], str_to_list(k)[1])
        items += [(s, s, "") for s in sorted(cm.brick_sizes_used.split("|"), reverse=True, key=sort_by) if (s, s, "") not in items]
    return items


def get_used_types():
    scn = bpy.context.scene
    items = [("NONE", "None", "")]
    for cm in scn.cmlist:
        items += [(t.upper(), t.title(), "") for t in sorted(cm.brick_types_used.split("|")) if (t.upper(), t.title(), "") not in items]
    return items


def iter_from_type(typ):
    return (typ.upper(), typ.title().replace("_", " "), "")


def create_obj_names_dict(objs):
    scn = bpy.context.scene
    # initialize obj_names_dict
    obj_names_dict = {}
    # fill obj_names_dict with selected_objects
    for obj in objs:
        if obj is None or not obj.is_brick:
            continue
        # get cmlist item referred to by object
        cm = get_item_by_id(scn.cmlist, obj.cmlist_id)
        if cm is None: continue
        # add object to obj_names_dict
        if cm.id not in obj_names_dict:
            obj_names_dict[cm.id] = [obj.name]
        else:
            obj_names_dict[cm.id].append(obj.name)
    return obj_names_dict


def select_bricks(obj_names_dict, bricksdicts, brick_size="NULL", brick_type="NULL", all_models=False, only=False, include="EXT"):
    scn = bpy.context.scene
    if only:
        deselect_all()
    # split all bricks in obj_names_dict[cm_id]
    for cm_id in obj_names_dict.keys():
        cm = get_item_by_id(scn.cmlist, cm_id)
        if not (cm.idx == scn.cmlist_index or all_models):
            continue
        bricksdict = bricksdicts[cm_id]
        selected_something = False

        for obj_name in obj_names_dict[cm_id]:
            # get dict key details of current obj
            dkey = get_dict_key(obj_name)
            dloc = get_dict_loc(bricksdict, dkey)
            siz = bricksdict[dkey]["size"]
            typ = bricksdict[dkey]["type"]
            on_shell = is_on_shell(bricksdict, dkey, loc=dloc, zstep=cm.zstep)

            # get current brick object
            cur_obj = bpy.data.objects.get(obj_name)
            # if cur_obj is None:
            #     continue
            # select brick
            size_str = list_to_str(sorted(siz[:2]) + [siz[2]])
            if (size_str == brick_size or typ == brick_type) and (include == "BOTH" or (include == "INT" and not on_shell) or (include == "EXT" and on_shell)):
                selected_something = True
                select(cur_obj)
            # elif only:
            #     deselect(cur_obj)

        # if no brick_size bricks exist, remove from cm.brick_sizes_used or cm.brick_types_used
        remove_unused_from_list(cm, brick_type=brick_type, brick_size=brick_size, selected_something=selected_something)


def remove_unused_from_list(cm, brick_type="NULL", brick_size="NULL", selected_something=True):
    item = brick_type if brick_type != "NULL" else brick_size
    # if brick_type/brick_size bricks exist, return None
    if selected_something or item == "NULL":
        return None
    # turn brick_types_used into list of sizes
    lst = (cm.brick_types_used if brick_type != "NULL" else cm.brick_sizes_used).split("|")
    # remove unused item
    if item in lst:
        remove_item(lst, item)
    # convert bTU back to string of sizes split by '|'
    new_list = list_to_str(lst, separate_by="|")
    # store new list to current cmlist item
    if brick_size != "NULL":
        cm.brick_sizes_used = new_list
    else:
        cm.brick_types_used = new_list


def get_adj_locs(cm, bricksdict, dkey, obj):
    # initialize vars for self.adj_locs setup
    x,y,z = get_dict_loc(bricksdict, dkey)
    obj_size = bricksdict[dkey]["size"]
    sX, sY, sZ = obj_size[0], obj_size[1], obj_size[2] // cm.zstep
    adj_locs = [[],[],[],[],[],[]]
    # initialize ranges
    rgs = [range(x, x + sX),
           range(y, y + sY),
           range(z, z + sZ)]
    # set up self.adj_locs
    adj_locs[0] += [[x + sX, y0, z0] for z0 in rgs[2] for y0 in rgs[1]]
    adj_locs[1] += [[x - 1, y0, z0]  for z0 in rgs[2] for y0 in rgs[1]]
    adj_locs[2] += [[x0, y + sY, z0] for z0 in rgs[2] for x0 in rgs[0]]
    adj_locs[3] += [[x0, y - 1, z0]  for z0 in rgs[2] for x0 in rgs[0]]
    adj_locs[4] += [[x0, y0, z + sZ] for y0 in rgs[1] for x0 in rgs[0]]
    adj_locs[5] += [[x0, y0, z - 1]  for y0 in rgs[1] for x0 in rgs[0]]
    return adj_locs


def install_bricksculpt():
    if not hasattr(bpy.props, "bricksculpt_module_name"):
        return False
    addons_path = bpy.utils.user_resource("SCRIPTS", "addons")
    bricksculpt_mod_name = bpy.props.bricksculpt_module_name
    bricker_mod_name = bpy.props.bricker_module_name
    bricksculpt_path_old = "%(addons_path)s/%(bricksculpt_mod_name)s/bricksculpt_framework.py" % locals()
    bricksculpt_path_new = "%(addons_path)s/%(bricker_mod_name)s/operators/customization_tools/bricksculpt_framework.py" % locals()
    f_old = open(bricksculpt_path_old, "r")
    f_new = open(bricksculpt_path_new, "w")
    # write META commands
    lines = f_old.readlines()
    f_new.truncate(0)
    f_new.writelines(lines)
    f_old.close()
    f_new.close()
    return True
