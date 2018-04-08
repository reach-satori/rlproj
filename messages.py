import libtcodpy as libtcod
import textwrap
from sett import *

def message(new_msg, color = libtcod.white, game_msgs = None):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        game_msgs.append( (line, color) )