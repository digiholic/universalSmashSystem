# coding: ascii
# optimize_dirty_rects
"""Optimize a list of dirty rects so that there are no overlapping rects

    File version: 1.1

    Minimum Python version: 2.4

    Inspirations:

        "It turns out, that there are quite many combinations...
         To represent all cases we use a table."
        Detect Overlapping Subrectangles by Herbert Glarner
        http://gandraxa.com/detect_overlapping_subrectangles.xml

        A way to process rectangle collisions is to categorize them
        based on edge inclusion.

        "Use wide, shallow graphic elements in preference to tall,
         narrow ones. (There are more raster lines, and therefore more
         pointer arithmetic, in tall graphics.)"
        Fast Blit Strategies: A Mac Programmer's Guide by Kas Thomas
        http://www.mactech.com/articles/mactech/Vol.15/15.06/FastBlitStrategies/index.html

        The optimized rectangles will tend to be wide and shallow.

    Return: new list

The MIT License (MIT)

Copyright (c) 2013 Jason Marshall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
from pygame import Rect
from bisect import bisect_left, insort
from collections import deque
#####import os
import sys

PYTHON_VERSION = sys.version_info[0]

#####DEBUG = int(os.environ.get('DEBUG', '1'))
#####if DEBUG:
#####    debug_output = sys.stderr.write
#####    debug = lambda x: debug_output(x + '\n')
#####else:
#####    debug = lambda x: None

try:
    Inf = float('inf')
except ValueError:
    #####debug('using fallback infinity')
    import decimal
    Inf = decimal.Decimal('Infinity')
negInf = -Inf

def optimize_dirty_rects(dirty_rects):
    """remove overlapping areas from a list of dirty rectangles"""
    #####debug("INPUT: " + str(dirty_rects))

    # Put good rects in a queue
    queue = deque()
    append_to_queue = queue.append
    for r in dirty_rects:
        if r:
            r.normalize()
            append_to_queue(r)

    # If there aren't multiple rectangles in the input queue, then more
    # optimization is not possible.
    if len(queue) <= 1:
        #####debug('shortcut 0\n')
        return list(queue)

    # Get the first rect
    append_to_queue = queue.appendleft
    pop_from_queue = queue.popleft
    r = pop_from_queue()

    # Determine the maximum possible size of all the rects combined
    extent_of_all_r = r.unionall(queue)

    # If any input rectangle covers the maximum possible size of all the rects
    # combined, then that rectangle is optimal.
    if r == extent_of_all_r:
        #####debug('shortcut 1\n')
        return [r]
    for r2 in queue:
        if r2 == extent_of_all_r:
            #####debug('shortcut 2\n')
            return [r2]

    # Create lists that will always be sorted by left edge position,
    # right edge position, top edge position and bottom edge position.
    # Rects are referenced by unique IDs for compatibility with set.
    # These unique IDs are mapped to rects by r_dict.
    r_id = id(r)
    r_dict = {r_id: r}
    edges_l = [(r.left, r_id)]
    edges_r = [(r.right, r_id)]
    edges_t = [(r.top, r_id)]
    edges_b = [(r.bottom, r_id)]

    while queue:

        r = pop_from_queue()
        r_id = id(r)

        ### Use bisect_left and set to get potential collisions ###
        # Get rect IDs with left edges <= r's right edge
        collisions = set(_get_rects_left_of_right_edge_inclusive(r, edges_l))
        collisions_update = collisions.intersection_update

        # Get rect IDs with right edges >= r's left edge
        collisions_update(_get_rects_right_of_left_edge_inclusive(r, edges_r))

        # Get rect IDs with top edges < rect's bottom edge
        collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

        # Get rect IDs with bottom edges > rect's top edge
        collisions_update(_get_rects_below_top_edge_exclusive(r, edges_b))

        # Handle collisions with existing optimized rects
        while collisions:

            r2_id = collisions.pop()
            r2 = r_dict[r2_id]

            if r.top == r2.top:
                if r.bottom == r2.bottom:
                    if r.left == r2.left:

                        if r.right <= r2.right:
                            #####debug('p001|p002')
                            # 1: RBTLRBTL: r is not outside of r2; forget r
                            # .....    .....
                            # .+++.    .---.
                            # .+++. -> .---.
                            # .+++.    .---.
                            # .....    .....
                            # 2: RBTL-BTL:
                            # .....    .....
                            # .++-.    .---.
                            # .++-. -> .---.
                            # .++-.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p003')
                            # 3: -BTLRBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .++|.    .|||.
                            # .++|. -> .|||.
                            # .++|.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

            #r.top == r2.top:
                #r.bottom == r2.bottom:
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p004|p005')
                            # 4: RBT-RBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .|++.    .|||.
                            # .|++. -> .|||.
                            # .|++.    .|||.
                            # .....    .....
                            # 5: -BT-RBTL:
                            # .....    .....
                            # .|+|.    .|||.
                            # .|+|. -> .|||.
                            # .|+|.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: #r.right < r2.right:
                            #####debug('p006|p007')
                            # 6: RBT--BTL: expand r to encompass r2; delete r2
                            # .....    .....
                            # .|+-.    .|||.
                            # .|+-. -> .|||.
                            # .|+-.    .|||.
                            # .....    .....
                            # 7: -BT--BT-a:
                            # .....    .....
                            # .|--.    .|||.
                            # .|--. -> .|||.
                            # .|--.    .|||.
                            # .....    .....
                            r.union_ip(r2)
                            if r == extent_of_all_r:
                                #####debug('shortcut 2a\n')
                                return [r]
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

            #r.top == r2.top:
                #r.bottom == r2.bottom:
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p008|p009')
                            # 8: RBTLRBT-: r is not outside of r2; forget r
                            # .....    .....
                            # .-++.    .---.
                            # .-++. -> .---.
                            # .-++.    .---.
                            # .....    .....
                            # 9: RBTL-BT-:
                            # .....    .....
                            # .-+-.    .---.
                            # .-+-. -> .---.
                            # .-+-.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p010|p011')
                            # 10: -BTLRBT-: expand r to encompass r2; delete r2
                            # .....    .....
                            # .-+|.    .|||.
                            # .-+|. -> .|||.
                            # .-+|.    .|||.
                            # .....    .....
                            # 11: -BT--BT-b:
                            # .....    .....
                            # .--|.    .|||.
                            # .--|. -> .|||.
                            # .--|.    .|||.
                            # .....    .....
                            r.union_ip(r2)
                            if r == extent_of_all_r:
                                #####debug('shortcut 2b\n')
                                return [r]
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

            #r.top == r2.top:
                elif r.bottom < r2.bottom:
                    if r.left == r2.left:

                        if r.right <= r2.right:
                            #####debug('p012|p013')
                            # 12: RBTLR-TL: r is not outside of r2; forget r
                            # .....    .....
                            # .+++.    .---.
                            # .---. -> .---.
                            # .---.    .---.
                            # .....    .....
                            # 13: RBTL--TL:
                            # .....    .....
                            # .++-.    .---.
                            # .++-. -> .---.
                            # .---.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p014')
                            # 14: -BTLR-TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # .+||.    .|||.
                            # .-... -> .-...
                            # .-...    .-...
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height -= r.height
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))

            #r.top == r2.top:
                #r.bottom < r2.bottom:
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p015|p018')
                            # 15: RBT-R-TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # .|++.    .|||.
                            # .|++. -> .|||.
                            # ..--.    ..--.
                            # .....    .....
                            # 18: -BT-R-TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # .|+|.    .|||.
                            # .|+|. -> .|||.
                            # ..-..    ..-..
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height -= r.height
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))

                        else: #r.right < r2.right
                            #####debug('p016|p017')
                            # 16: RBT---TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # Expand r to reach r2's right edge.
                            # .....    .....
                            # .|+-.    .|||.
                            # .|+-. -> .|||.
                            # ..--.    ..--.
                            # .....    .....
                            # 17: -BT---T-a:
                            # .....    .....
                            # .|--.    .|||.
                            # .|--. -> .|||.
                            # ..--.    ..--.
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height -= r.height
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))
                            r.width = r2.right - r.left

            #r.top == r2.top:
                #r.bottom < r2.bottom:
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p019|p020')
                            # 19: RBTLR-T-: r is not outside of r2; forget r
                            # .....    .....
                            # .-++.    .---.
                            # .-++. -> .---.
                            # .---.    .---.
                            # .....    .....
                            # 20: RBTL--T-:
                            # .....    .....
                            # .-+-.    .---.
                            # .-+-. -> .---.
                            # .---.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p021|p022')
                            # 21: -BTLR-T-:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # Expand r to reach r2's left edge.
                            # .....    .....
                            # .-+|.    .|||.
                            # .-+|. -> .|||.
                            # .--..    .--..
                            # .....    .....
                            # 22: -BT---T-b:
                            # .....    .....
                            # .--|.    .|||.
                            # .--|. -> .|||.
                            # .--..    .--..
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height -= r.height
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))
                            r.width = r.right - r2.left
                            r.left = r2.left

            #r.top == r2.top:
                else: #r.bottom > r2.bottom
                    if r.left == r2.left:

                        if r.right >= r2.right:
                            #####debug('p023|p025')
                            # 23: R-TLRBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .+++.    .|||.
                            # .+++. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            # 25: --TLRBTL:
                            # .....    .....
                            # .++|.    .|||.
                            # .++|. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: #r.right < r2.right:
                            #####debug('p024')
                            # 24: R-TL-BTL: crop r to the part that is below r2
                            # .....    .....
                            # .++-.    .---.
                            # .++-. -> .---.
                            # .||..    .||..
                            # .....    .....
                            r.height -= r2.height
                            r.top = r2.bottom

            #r.top == r2.top:
                #r.bottom > r2.bottom
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p026|p029')
                            # 26: R-T-RBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .|++.    .|||.
                            # .|++.    .|||.
                            # .|||.    .|||.
                            # .....    .....
                            # 29: --T-RBTL:
                            # .....    .....
                            # .|+|.    .|||.
                            # .|+|.    .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: #r.right < r2.right
                            #####debug('p027|p028')
                            # 27: R-T--BTL:
                            # Split r into r & r3 at the bottom of r2.
                            # Expand r to encompass r2; delete r2.
                            # Enqueue the on-bottom parts.  Remove r_id
                            # numbers from the collisions set if their
                            # rects collide with only r3 or are beside
                            # only r3.
                            # .....    .....
                            # .|+-.    .|||.
                            # .|+-. -> .|||.
                            # .||..    .==..
                            # .....    .....
                            # 28: --T--BT-b:
                            # .....    .....
                            # .||-.    .|||.
                            # .||-. -> .|||.
                            # .||..    .==..
                            # .....    .....
                            r3 = Rect(r.left, r2.bottom, r.width, r.height - r2.height)
                            append_to_queue(r3)
                            r.height = r2.height
                            r.union_ip(r2)
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

            #r.top == r2.top:
                #r.bottom > r2.bottom
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p030|p031')
                            # 30: R-TLRBT-: crop r to the part that is below r2
                            # .....    .....
                            # .-++.    .---.
                            # .-++. -> .---.
                            # ..||.    ..||.
                            # .....    .....
                            # 31: R-TL-BT-:
                            # .....    .....
                            # .-+-.    .---.
                            # .-+-. -> .---.
                            # ..|..    ..|..
                            # .....    .....
                            r.height -= r2.height
                            r.top = r2.bottom

                        else: #r.right > r2.right
                            #####debug('p032|p033')
                            # 32: --TLRBT-
                            # Split r into r & r3 at the bottom of r2.
                            # Expand r to encompass r2; delete r2.
                            # Enqueue the on-bottom parts.  Remove r_id
                            # numbers from the collisions set if their
                            # rects collide with only r3 or are beside
                            # only r3.
                            # .....    .....
                            # .-+|.    .|||.
                            # .-+|. -> .|||.
                            # ..||.    ..==.
                            # .....    .....
                            # 33: --T--BT-a:
                            # .....    .....
                            # .-||.    .|||.
                            # .-||. -> .|||.
                            # ..||.    ..==.
                            # .....    .....
                            r3 = Rect(r.left, r2.bottom, r.width, r.height - r2.height)
                            append_to_queue(r3)
                            r.height = r2.height
                            r.union_ip(r2)
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

            elif r.top < r2.top:
                if r.bottom == r2.bottom:
                    if r.left == r2.left:

                        if r.right >= r2.right:
                            #####debug('p034|p036')
                            # 34: RB-LRBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .|||.    .|||.
                            # .+++. -> .|||.
                            # .+++.    .|||.
                            # .....    .....
                            # 36: -B-LRBTL:
                            # .....    .....
                            # .|||.    .|||.
                            # .++|. -> .|||.
                            # .++|.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: # r.right < r2.right:
                            #####debug('p035')
                            # 35: RB-L-BTL: crop r to the part that is above r2
                            # .....    .....
                            # .||..    .||..
                            # .++-. -> .---.
                            # .++-.    .---.
                            # .....    .....
                            r.height -= r2.height

            #r.top < r2.top:
                #r.bottom == r2.bottom:
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p037|p040')
                            # 37: RB--RBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .|||.    .|||.
                            # .|++. -> .|||.
                            # .|++.    .|||.
                            # .....    .....
                            # 40: -B--RBTL:
                            # .....    .....
                            # .|||.    .|||.
                            # .|+|. -> .|||.
                            # .|+|.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: # r.right < r2.right:
                            #####debug('p038|p039')
                            # 38: RB---BTL:
                            # Split r into r & r3 at the top of r2.
                            # Expand r to encompass r2; delete r2.
                            # Enqueue the on-top parts.  Remove r_id
                            # numbers from the collisions set if their
                            # rects collide with only r3 or are beside
                            # only r3.
                            # .....    .....
                            # .||..    .==..
                            # .|+-. -> .|||.
                            # .|+-.    .|||.
                            # .....    .....
                            # 39: -B---BT-b:
                            # .....    .....
                            # .||..    .==..
                            # .||-. -> .|||.
                            # .||-.    .|||.
                            # .....    .....
                            r3 = Rect(r.left, r.top, r.width, r.height - r2.height)
                            append_to_queue(r3)
                            r.height = r2.height
                            r.top = r2.top
                            r.union_ip(r2)
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)
                            collisions_update(_get_rects_below_top_edge_exclusive(r, edges_b))

            #r.top < r2.top:
                #r.bottom == r2.bottom:
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p041|p042')
                            # 41: RB-LRBT-: crop r to the part that is above r2
                            # .....    .....
                            # ..||.    ..||.
                            # .-++. -> .---.
                            # .-++.    .---.
                            # .....    .....
                            # 42: RB-L-BT-:
                            # .....    .....
                            # ..|..    ..|..
                            # .-+-. -> .---.
                            # .-+-.    .---.
                            # .....    .....
                            r.height -= r2.height

                        else: #r.right > r2.right
                            #####debug('p043|p044')
                            # 43: -B-LRBT-:
                            # Split r into r & r3 at the top of r2.
                            # Expand r to encompass r2; delete r2.
                            # Enqueue the on-top parts.  Remove r_id
                            # numbers from the collisions set if their
                            # rects collide with only r3 or are beside
                            # only r3.
                            # .....    .....
                            # ..||.    ..==.
                            # .-+|. -> .|||.
                            # .-+|.    .|||.
                            # .....    .....
                            # 44: -B---BT-a:
                            # .....    .....
                            # ..||.    ..==.
                            # .-||. -> .|||.
                            # .-||.    .|||.
                            # .....    .....
                            r3 = Rect(r.left, r.top, r.width, r.height - r2.height)
                            append_to_queue(r3)
                            r.height = r2.height
                            r.top = r2.top
                            r.union_ip(r2)
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)
                            collisions_update(_get_rects_below_top_edge_exclusive(r, edges_b))

            #r.top < r2.top:
                elif r.bottom < r2.bottom:
                    if r.left == r2.left:

                        if r.right == r2.right:
                            #####debug('p045')
                            # 45: RB-LR-TL: expand r to encompass r2; delete r2
                            # .....    .....
                            # .|||.    .|||.
                            # .+++. -> .|||.
                            # .---.    .|||.
                            # .....    .....
                            r.union_ip(r2)
                            if r == extent_of_all_r:
                                #####debug('shortcut 2b\n')
                                return [r]
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        elif r.right < r2.right:
                            #####debug('p046')
                            # 46: RB-L--TL: crop r to the part that is above r2
                            # .....    .....
                            # .||..    .||..
                            # .++-. -> .---.
                            # .---.    .---.
                            # .....    .....
                            r.height = r2.top - r.top

                        else: #r.right > r2.right
                            #####debug('p047')
                            # 47: -B-LR-TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # .|||.    .|||.
                            # .++|. -> .|||.
                            # .--..    .--..
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height = r2.bottom - r.bottom
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))

            #r.top < r2.top:
                #r.bottom < r2.bottom:
                    elif r.left < r2.left:

                        if r.right == r2.right:
                            #####debug('p048')
                            # 48: RB--R-TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # .|||.    .|||.
                            # .|++. -> .|||.
                            # ..--.    ..--.
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height = r2.bottom - r.bottom
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))

                        elif r.right < r2.right:
                            #####debug('p049|p050')
                            # 49: RB----TL:
                            # Create r3 to cover the area of r that is in
                            # line with r2 and the area of r2 that is in
                            # line with r. Enqueue r3. Crop r to the part
                            # that is above r3. Crop r2 to the part that
                            # is below r3. Remove r_id numbers from the
                            # collisions set if their rects no longer either
                            # collide with r or are beside r. Update r2's
                            # position in edges_t.
                            # .....    .....
                            # .||..    .||..
                            # .|+-. -> .===.
                            # ..--.    ..--.
                            # .....    .....
                            # 50: -B----T-a:
                            # .....    .....
                            # .||..    .||..
                            # .||-. -> .===.
                            # ...-.    ...-.
                            # .....    .....
                            r3 = Rect(r.left, r2.top, r2.right - r.left, r.bottom - r2.top)
                            append_to_queue(r3)
                            r.height -= r3.height
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height -= r3.height
                            r2.top = r3.bottom
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))
                            insort(edges_t, (r2.top, r2_id))

                        else: #r.right > r2.right
                            #####debug('p051')
                            # 51: -B--R-TL:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # .|||.    .|||.
                            # .|+|. -> .|||.
                            # ..-..    ..-..
                            # .....    .....
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height = r2.bottom - r.bottom
                            r2.top = r.bottom
                            insort(edges_t, (r2.top, r2_id))

            #r.top < r2.top:
                #r.bottom < r2.bottom:
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p052|p053')
                            # 52: RB-LR-T-: crop r to the part that is above r2
                            # .....    .....
                            # ..||.    ..||.
                            # .-++. -> .---.
                            # .---.    .---.
                            # .....    .....
                            # 52: RB-L--T-:
                            # .....    .....
                            # ..|..    ..|..
                            # .-+-. -> .---.
                            # .---.    .---.
                            # .....    .....
                            r.height = r2.top - r.top

                        else: #r.right > r2.right
                            #####debug('p054|p055')
                            # 54: -B-LR-T-:
                            # Create r3 to cover the area of r that is in
                            # line with r2 and the area of r2 that is in
                            # line with r. Enqueue r3. Crop r to the part
                            # that is above r3. Crop r2 to the part that
                            # is below r3. Remove r_id numbers from the
                            # collisions set if their rects no longer either
                            # collide with r or are beside r. Update r2's
                            # position in edges_t.
                            # .....    .....
                            # ..||.    ..||.
                            # .-+|. -> .===.
                            # .--..    .--..
                            # .....    .....
                            # 55: -B----T-b:
                            # .....    .....
                            # ..||.    ..||.
                            # .-||. -> .===.
                            # .-...    .-...
                            # .....    .....
                            r3 = Rect(r2.left, r2.top, r.right - r2.left, r.bottom - r2.top)
                            append_to_queue(r3)
                            r.height -= r3.height
                            _remove_r_from_edges_t(r2, r2_id, edges_t)
                            r2.height -= r3.height
                            r2.top = r3.bottom
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))
                            insort(edges_t, (r2.top, r2_id))

            #r.top < r2.top:
                else: #r.bottom > r2.bottom
                    if r.left == r2.left:

                        if r.right >= r2.right:
                            #####debug('p056|p058')
                            # 56: R--LRBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .|||.    .|||.
                            # .+++. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            # 58: ---LRBTL:
                            # .....    .....
                            # .|||.    .|||.
                            # .++|. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: #r.right < r2.right:
                            #####debug('p057')
                            # 57: R--L-BTL:
                            # Separate r into on-top & on-bottom parts.
                            # Lose the middle; it is not outside of r2.
                            # Enqueue the on-bottom parts.  Remove r_id
                            # numbers from the collisions set if their
                            # rects no longer either collide with r1 or
                            # are beside r1.
                            # .....    .....
                            # .||..    .||..
                            # .++-. -> .---.
                            # .||..    .==..
                            # .....    .....
                            r3 = Rect(r.left, r2.bottom, r.width, r.bottom - r2.bottom)
                            append_to_queue(r3)
                            r.height = r2.top - r.top
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

            #r.top < r2.top:
                #r.bottom > r2.bottom
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p059|p061')
                            # 59: R---RBTL: r2 is not outside of r; delete r2
                            # .....    .....
                            # .|||.    .|||.
                            # .|++. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            # 61: ----RBTL:
                            # .....    .....
                            # .|||.    .|||.
                            # .|+|. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        else: #r.right < r2.right:
                            #####debug('p060|p066')
                            # 60: R----BTL:
                            # Separate r into on-top & on-bottom parts.
                            # Lose the middle. Extend r2 and return it
                            # to the queue. Enqueue the on-bottom parts.
                            # Remove r_id numbers from the collisions
                            # set if their rects no longer either
                            # collide with r1 or are beside r1.
                            # .....    .....
                            # .||..    .||..
                            # .|+-. -> .---.
                            # .||..    .==..
                            # .....    .....
                            # 66: -----BT-b:
                            # .....    .....
                            # .|...    .|...
                            # .|--. -> .---.
                            # .|...    .=...
                            # .....    .....
                            r3 = Rect(r.left, r2.bottom, r.width, r.bottom - r2.bottom)
                            append_to_queue(r3)
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)
                            r2.width = r2.right - r.left
                            r2.left = r.left
                            append_to_queue(r2)
                            r.height = r2.top - r.top
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

            #r.top < r2.top:
                #r.bottom > r2.bottom
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p062|p063')
                            # 62: R--LRBT-:
                            # Separate r into on-top & on-bottom parts.
                            # Lose the middle; it is not outside of r2.
                            # Enqueue the on-bottom parts.  Remove r_id
                            # numbers from the collisions set if their
                            # rects no longer either collide with r1 or
                            # are beside r1.
                            # .....    .....
                            # ..||.    ..||.
                            # .-++. -> .---.
                            # ..||.    ..==.
                            # .....    .....
                            # 63: R--L-BT-:
                            # .....    .....
                            # ..|..    ..|..
                            # .-+-. -> .---.
                            # ..|..    ..=..
                            # .....    .....
                            r3 = Rect(r.left, r2.bottom, r.width, r.bottom - r2.bottom)
                            append_to_queue(r3)
                            r.height = r2.top - r.top
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

                        else: #r.right > r2.right
                            #####debug('p064|p065')
                            # 64: ---LRBT-
                            # Separate r into on-top & on-bottom parts.
                            # Lose the middle. Extend r2 and return it
                            # to the queue. Enqueue the on-bottom parts.
                            # Remove r_id numbers from the collisions
                            # set if their rects no longer either
                            # collide with r1 or are beside r1.
                            # .....    .....
                            # ..||.    ..||.
                            # .-+|. -> .---.
                            # ..||.    ..==.
                            # .....    .....
                            # 65: -----BT-a:
                            # .....    .....
                            # ...|.    ...|.
                            # .--|. -> .---.
                            # ...|.    ...=.
                            # .....    .....
                            r3 = Rect(r.left, r2.bottom, r.width, r.bottom - r2.bottom)
                            append_to_queue(r3)
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)
                            r2.width = r.right - r2.left
                            append_to_queue(r2)
                            r.height = r2.top - r.top
                            collisions_update(_get_rects_above_bottom_edge_exclusive(r, edges_t))

            else: #r.top > r2.top
                if r.bottom == r2.bottom:
                    if r.left == r2.left:

                        if r.right <= r2.right:
                            #####debug('p067|p068')
                            # 67: RBTLRB-L: r is not outside of r2; forget r
                            # .....    .....
                            # .---.    .---.
                            # .+++. -> .---.
                            # .+++.    .---.
                            # .....    .....
                            # 68: RBTL-B-L:
                            # .....    .....
                            # .---.    .---.
                            # .++-. -> .---.
                            # .++-.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p069')
                            # 69: -BTLRB-L:
                            # Crop r2 to the part that is above r.
                            # Update r2's location in edges_b.
                            # .....    .....
                            # .-...    .-...
                            # .-... -> .-...
                            # .+||.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height -= r.height
                            insort(edges_b, (r2.bottom, r2_id))

            #r.top > r2.top
                #r.bottom == r2.bottom:
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p070|p073')
                            # 70: RBT-RB-L:
                            # Crop r2 to the part that is above r.
                            # Update r2's location in edges_b.
                            # .....    .....
                            # ...-.    ...-.
                            # ...-. -> ...-.
                            # .||+.    .|||.
                            # .....    .....
                            # 73: -BT-RB-L:
                            # .....    .....
                            # ..-..    ..-..
                            # ..-.. -> ..-..
                            # .|+|.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height -= r.height
                            insort(edges_b, (r2.bottom, r2_id))

                        else: #r.right < r2.right:
                            #####debug('p071|p072')
                            # 71: RBT--B-L:
                            # Crop r2 to the part that is above r.
                            # Update r2's location in edges_b.
                            # Expand r to reach r2's right edge.
                            # .....    .....
                            # ..--.    ..--.
                            # .|+-. -> .|||.
                            # .|+-.    .|||.
                            # .....    .....
                            # 72: -BT--B--a:
                            # .....    .....
                            # ..--.    ..--.
                            # .|--. -> .|||.
                            # .|--.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height -= r.height
                            insort(edges_b, (r2.bottom, r2_id))
                            r.width = r2.right - r.left

            #r.top > r2.top
                #r.bottom == r2.bottom:
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p074|p075')
                            # 74: RBTLRB--: r is not outside of r2; forget r
                            # .....    .....
                            # .---.    .---.
                            # .-++. -> .---.
                            # .-++.    .---.
                            # .....    .....
                            # 75: RBTL-B--:
                            # .....    .....
                            # .---.    .---.
                            # .-+-. -> .---.
                            # .-+-.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p076|p077')
                            # 76: -BTLRB--:
                            # Crop r2 to the part that is above r.
                            # Update r2's location in edges_b.
                            # Expand r to reach r2's left edge.
                            # .....    .....
                            # .--..    .--..
                            # .-+|. -> .|||.
                            # .-+|.    .|||.
                            # .....    .....
                            # 77: -BT--B--b:
                            # .....    .....
                            # .--..    .--..
                            # .--|. -> .|||.
                            # .--|.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height -= r.height
                            insort(edges_b, (r2.bottom, r2_id))
                            r.width = r.right - r2.left
                            r.left = r2.left

            #r.top > r2.top
                elif r.bottom < r2.bottom:
                    if r.left == r2.left:

                        if r.right <= r2.right:
                            #####debug('p078|p079')
                            # 78: RBTLR--L: r is not outside of r2; forget r
                            # .....    .....
                            # .---.    .---.
                            # .+++. -> .---.
                            # .---.    .---.
                            # .....    .....
                            # 79: RBTL---L:
                            # .....    .....
                            # .---.    .---.
                            # .+--. -> .---.
                            # .---.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p080')
                            # 80: -BTLR--L:
                            # Separate r2 into on-top & on-bottom parts.
                            # Lose the middle. Put r3 in edges lists.
                            # Update r2's location in edges_b.
                            # .....    .....
                            # .-...    .-...
                            # .+||. -> .|||.
                            # .-...    .=...
                            # .....    .....
                            r3 = Rect(r.left, r.bottom, r2.width, r2.bottom - r.bottom)
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            _add_r(r3, id(r3), r_dict, edges_l, edges_r, edges_t, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))

            #r.top > r2.top
                #r.bottom < r2.bottom:
                    elif r.left < r2.left:

                        if r.right >= r2.right:
                            #####debug('p081|p084')
                            # 81: RBT-R--L:
                            # Separate r2 into on-top & on-bottom parts.
                            # Lose the middle. Put r3 in edges lists.
                            # Update r2's location in edges_b.
                            # .....    .....
                            # ...-.    ...-.
                            # .||+. -> .|||.
                            # ...-.    ...=.
                            # .....    .....
                            # 84: -BT-R--L:
                            # .....    .....
                            # ..-..    ..-..
                            # .|+|. -> .|||.
                            # ..-..    ..=..
                            # .....    .....
                            r3 = Rect(r2.left, r.bottom, r2.width, r2.bottom - r.bottom)
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            _add_r(r3, id(r3), r_dict, edges_l, edges_r, edges_t, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))

                        else: #r.right < r2.right:
                            #####debug('p082|p083')
                            # 82: RBT----L:
                            # Separate r2 into on-top & on-bottom parts.
                            # Lose the middle. Put r3 in edges lists.
                            # Update r2's location in edges_b. Extend r
                            # to cover what was the middle of r2.
                            # .....    .....
                            # ..--.    ..--.
                            # .|+-. -> .|||.
                            # ..--.    ..==.
                            # .....    .....
                            # 83: -BT-----a:
                            # .....    .....
                            # ..--.    ..--.
                            # .|--. -> .|||.
                            # ..--.    ..==.
                            # .....    .....
                            r3 = Rect(r2.left, r.bottom, r2.width, r2.bottom - r.bottom)
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            _add_r(r3, id(r3), r_dict, edges_l, edges_r, edges_t, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))
                            r.width = r2.right - r.left

            #r.top > r2.top
                #r.bottom < r2.bottom:
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p085|p086')
                            # 85: RBTLR---: r is not outside of r2; forget r
                            # .....    .....
                            # .---.    .---.
                            # .-++. -> .---.
                            # .---.    .---.
                            # .....    .....
                            # 86: RBTL----:
                            # .....    .....
                            # .---.    .---.
                            # .-+-. -> .---.
                            # .---.    .---.
                            # .....    .....
                            break

                        else: #r.right > r2.right
                            #####debug('p087|p088')
                            # 87: -BTLR---:
                            # Separate r2 into on-top & on-bottom parts.
                            # Lose the middle. Put r3 in edges lists.
                            # Update r2's location in edges_b. Extend r
                            # to cover what was the middle of r2.
                            # .....    .....
                            # .--..    .--..
                            # .-+|. -> .|||.
                            # .--..    .==..
                            # .....    .....
                            # 88: -BT-----b:
                            # .....    .....
                            # .--.    .--..
                            # .--| -> .|||.
                            # .--.    .==..
                            # .....    .....
                            r3 = Rect(r2.left, r.bottom, r2.width, r2.bottom - r.bottom)
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            _add_r(r3, id(r3), r_dict, edges_l, edges_r, edges_t, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))
                            r.width = r.right - r2.left
                            r.left = r2.left

            #r.top > r2.top
                else: #r.bottom > r2.bottom
                    if r.left == r2.left:

                        if r.right == r2.right:
                            #####debug('p089')
                            # 89: R-TLRB-L: expand r to encompass r2; delete r2
                            # .....    .....
                            # .---.    .|||.
                            # .+++. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            r.union_ip(r2)
                            if r == extent_of_all_r:
                                #####debug('shortcut 2b\n')
                                return [r]
                            _del_r(r2, r2_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                        elif r.right < r2.right:
                            #####debug('p090')
                            # 90: R-TL-B-L: crop r to the part that is below r2
                            # .....    .....
                            # .---.    .---.
                            # .++-. -> .---.
                            # .||..    .||..
                            # .....    .....
                            r.height = r.bottom - r2.bottom
                            r.top = r2.bottom

                        else: #r.right > r2.right
                            #####debug('p091')
                            # 91: --TLRB-L:
                            # Crop r2 to the part that is above r.
                            # Update r2's location in edges_b.
                            # .....    .....
                            # .--..    .--..
                            # .++|. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))

            #r.top > r2.top
                #r.bottom > r2.bottom
                    elif r.left < r2.left:

                        if r.right == r2.right:
                            #####debug('p092')
                            # 92: R-T-RB-L:
                            # Crop r2 to the part that is below r.
                            # Update r2's location in edges_t.
                            # .....    .....
                            # ..--.    ..--.
                            # .|++. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))

                        elif r.right < r2.right:
                            #####debug('p093|p094')
                            # 93: R-T--B-L:
                            # Create r3 to cover the area of r that is in
                            # line with r2 and the area of r2 that is in
                            # line with r. Enqueue r3. Crop r to the part
                            # that is above r3. Crop r2 to the part that
                            # is below r3. Remove r_id numbers from the
                            # collisions set if their rects no longer either
                            # collide with r or are beside r. Update r2's
                            # position in edges_b.
                            # .....    .....
                            # ..--.    ..--.
                            # .|+-. -> .===.
                            # .||..    .||..
                            # .....    .....
                            # 94: --T--B--b:
                            # .....    .....
                            # ...-.    ...-.
                            # .||-. -> .===.
                            # .||..    .||..
                            # .....    .....
                            r3 = Rect(r.left, r.top, r2.right - r.left, r2.bottom - r.top)
                            append_to_queue(r3)
                            r.height -= r3.height
                            r.top = r3.bottom
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height -= r3.height
                            collisions_update(_get_rects_below_top_edge_exclusive(r, edges_b))
                            insort(edges_b, (r2.bottom, r2_id))

                        else: #r.right > r2.right
                            #####debug('p095')
                            # 95: --T-RB-L:
                            # Crop r2 to the part that is above r.
                            # Update r2's location in edges_b.
                            # .....    .....
                            # ..-..    ..-..
                            # .|+|. -> .|||.
                            # .|||.    .|||.
                            # .....    .....
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height = r.top - r2.top
                            insort(edges_b, (r2.bottom, r2_id))

            #r.top > r2.top
                #r.bottom > r2.bottom
                    else: #r.left > r2.left

                        if r.right <= r2.right:
                            #####debug('p096|p097')
                            # 96: R-TLRB--: crop r to the part that is below r2
                            # .....    .....
                            # .---.    .---.
                            # .-++. -> .---.
                            # . ||.    ..||.
                            # .....    .....
                            # 97: R-TL-B--: crop r to the part that is below r2
                            # .....    .....
                            # .---.    .---.
                            # .-+-. -> .---.
                            # . |..    ..|..
                            # .....    .....
                            r.height = r.bottom - r2.bottom
                            r.top = r2.bottom

                        else: #r.right > r2.right
                            #####debug('p098|p099')
                            # 99: R-T--B-L:
                            # Create r3 to cover the area of r that is in
                            # line with r2 and the area of r2 that is in
                            # line with r. Enqueue r3. Crop r to the part
                            # that is above r3. Crop r2 to the part that
                            # is below r3. Remove r_id numbers from the
                            # collisions set if their rects no longer either
                            # collide with r or are beside r. Update r2's
                            # position in edges_b.
                            # .....    .....
                            # .--..    .--.
                            # .-+|. -> .===.
                            # ..||.    ..||.
                            # .....    .....
                            # 98: --T--B--b:
                            # .....    .....
                            # .-...    .-...
                            # .-||. -> .===.
                            # ..||.    ..||.
                            # .....    .....
                            r3 = Rect(r2.left, r.top, r.right - r2.left, r2.bottom - r.top)
                            append_to_queue(r3)
                            r.height -= r3.height
                            r.top = r3.bottom
                            _remove_r_from_edges_b(r2, r2_id, edges_b)
                            r2.height -= r3.height
                            collisions_update(_get_rects_below_top_edge_exclusive(r, edges_b))
                            insort(edges_b, (r2.bottom, r2_id))

        # No r2 rectangles either collided with r or were beside r, so
        # add r to r_dict and the edge position lists.
        else:

            # If r is as wide as extent_of_all_r, then try to expand r's
            # height to the height of extent_of_all_r. If r is both as
            # wide and as tall as extent_of_all_r, then no further
            # optimization is possible; return r.
            if r.width == extent_of_all_r.width:

                # If there is a rect as wide as extent_of_all_r that is
                # directly above r, then r2 will refer to it.
                r2, r2_id = _get_full_width_r_above(r, extent_of_all_r, r_dict, edges_b)

                # If there is a rect as wide as extent_of_all_r that is
                # directly below r, then r3 will refer to it.
                r3, r3_id = _get_full_width_r_below(r, extent_of_all_r, r_dict, edges_t)

                if r2 and r3:

                    # Expand r2 to encompass r and r3; delete r3; forget r
                    # ----------
                    # ||||||||||
                    # ==========
                    #####debug('shortcut 3')
                    _remove_r_from_edges_b(r2, r2_id, edges_b)
                    r2.union_ip(r3)
                    if r2 == extent_of_all_r:
                        #####debug('shortcut 3a\n')
                        return [r2]
                    insort(edges_b, (r2.bottom, r2_id))
                    _del_r(r3, r3_id, r_dict, edges_l, edges_r, edges_t, edges_b)

                    continue

                elif r2:

                    # Expand r2 to encompass r; forget r
                    # ----------
                    # ||||||||||
                    #####debug('shortcut 4')
                    _remove_r_from_edges_b(r2, r2_id, edges_b)
                    r2.union_ip(r)
                    if r2 == extent_of_all_r:
                        #####debug('shortcut 4a\n')
                        return [r2]
                    insort(edges_b, (r2.bottom, r2_id))

                    continue

                elif r3:

                    # Expand r3 to encompass r; forget r
                    # ||||||||||
                    # ==========
                    #####debug('shortcut 5')
                    _remove_r_from_edges_t(r3, r3_id, edges_t)
                    r3.union_ip(r)
                    if r3 == extent_of_all_r:
                        #####debug('shortcut 5a\n')
                        return [r3]
                    insort(edges_t, (r3.top, r3_id))

                    continue

            # Add r to r_dict and edges lists
            _add_r(r, r_id, r_dict, edges_l, edges_r, edges_t, edges_b)

    # Done optimizing!
    if PYTHON_VERSION >= 3:
        return_list = list(r_dict.values())
    else:
        return_list = r_dict.values()

    #####debug('OUTPUT: ' + str(return_list) + '\n')
    return return_list

def _get_rects_left_of_right_edge_inclusive(r, edges_l):
    """helper for optimize_dirty_rects func"""
    index_l = bisect_left(edges_l, (r.right, Inf))
    return (t[1] for t in edges_l[:index_l])

def _get_rects_right_of_left_edge_inclusive(r, edges_r):
    """helper for optimize_dirty_rects func"""
    index_r = bisect_left(edges_r, (r.left, negInf))
    return (t[1] for t in edges_r[index_r:])

def _get_rects_above_bottom_edge_exclusive(r, edges_t):
    """helper for optimize_dirty_rects func"""
    index_t = bisect_left(edges_t, (r.bottom, negInf))
    return (t[1] for t in edges_t[:index_t])

def _get_rects_below_top_edge_exclusive(r, edges_b):
    """helper for optimize_dirty_rects func"""
    index_b = bisect_left(edges_b, (r.top, Inf))
    return (t[1] for t in edges_b[index_b:])

def _get_full_width_r_above(r, extent_of_all_r, r_dict, edges_b):
    """helper for optimize_dirty_rects func"""

    if r.top != extent_of_all_r.top:
        index_b = bisect_left(edges_b, (r.top, negInf))
        if index_b < len(edges_b):
            r2_id = edges_b[index_b][1]
            r2 = r_dict[r2_id]
            if r2.bottom == r.top and r2.width == extent_of_all_r.width:
                return r2, r2_id
    return None, None

def _get_full_width_r_below(r, extent_of_all_r, r_dict, edges_t):
    """helper for optimize_dirty_rects func"""

    if r.bottom != extent_of_all_r.bottom:
        index_t = bisect_left(edges_t, (r.bottom, negInf))
        if index_t < len(edges_t):
            r2_id = edges_t[index_t][1]
            r2 = r_dict[r2_id]
            if r2.top == r.bottom and r2.width == extent_of_all_r.width:
                return r2, r2_id
    return None, None

def _add_r(r, r_id, r_dict, edges_l, edges_r, edges_t, edges_b):
    """helper for optimize_dirty_rects func"""

    r_dict[r_id] = r
    insort(edges_l, (r.left, r_id))
    insort(edges_r, (r.right, r_id))
    insort(edges_t, (r.top, r_id))
    insort(edges_b, (r.bottom, r_id))

def _del_r(r, r_id, r_dict, edges_l, edges_r, edges_t, edges_b):
    """helper for optimize_dirty_rects func"""

    del r_dict[r_id]
    _remove_r_from_edges_l(r, r_id, edges_l)
    _remove_r_from_edges_r(r, r_id, edges_r)
    _remove_r_from_edges_t(r, r_id, edges_t)
    _remove_r_from_edges_b(r, r_id, edges_b)

def _remove_r_from_edges_l(r, r_id, edges_l):
    """helper for optimize_dirty_rects func"""

    index_l = bisect_left(edges_l, (r.left, r_id))
    assert edges_l[index_l] == (r.left, r_id), 'algorithm err: left del'
    del edges_l[index_l]

def _remove_r_from_edges_r(r, r_id, edges_r):
    """helper for optimize_dirty_rects func"""

    index_r = bisect_left(edges_r, (r.right, r_id))
    assert edges_r[index_r] == (r.right, r_id), 'algorithm err: right del'
    del edges_r[index_r]

def _remove_r_from_edges_t(r, r_id, edges_t):
    """helper for optimize_dirty_rects func"""

    index_t = bisect_left(edges_t, (r.top, r_id))
    assert edges_t[index_t] == (r.top, r_id), 'algorithm err: top del'
    del edges_t[index_t]

def _remove_r_from_edges_b(r, r_id, edges_b):
    """helper for optimize_dirty_rects func"""

    index_b = bisect_left(edges_b, (r.bottom, r_id))
    assert edges_b[index_b] == (r.bottom, r_id), 'algorithm err: bottom del'
    del edges_b[index_b]
