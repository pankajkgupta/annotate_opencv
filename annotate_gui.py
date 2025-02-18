#!/usr/bin/env python

import cv2, numpy as np
import sys
from time import sleep

import annotate_tools
import pandas as pd
import colorsys

from tkinter import *
#import ttk
from tkinter import ttk
import os
import glob
from configparser import ConfigParser

def get_filenames():
    path = root_path + "*.avi"
    return [os.path.basename(x) for x in sorted(glob.glob(path))]

def onselect(evt):
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    print('You selected item %d: "%s"' % (index, value))
    show_video(root_path+value)

def show_video(v_path):

    basepath = os.path.split(v_path)
    player_wname = basepath[1][:-4]
    cv2.destroyAllWindows()
    cv2.namedWindow(player_wname, cv2.WINDOW_GUI_NORMAL)
    cv2.moveWindow(player_wname, 400, 150)
    cv2.namedWindow(control_wname)
    cv2.moveWindow(control_wname, 400, 50)

    # video = sys.argv[1]
    # video = '/media/clpsshare/pgupta/0f4db67a-4533-45ff-b2e3-86cef598973d/0f4db67a-4533-45ff-b2e3-86cef598973d_0000.mp4'
    cap = cv2.VideoCapture(v_path)

    playerwidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    playerheight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    annot_file = basepath[0] + '/pose_' + basepath[1][:-4] + '.csv'
    annots = pd.read_csv(annot_file)
    if 'quality' in annots: 
        annots['quality'] = annots['quality'].fillna(0)
    annotate_tools.init(annotate_tools.annots, joints, joint_radius, annots, player_wname, playerwidth, playerheight, colorDict, multiframe)
    cv2.setMouseCallback(player_wname, annotate_tools.dragcircle, annotate_tools.annots)
    controls = np.zeros((50, int(playerwidth*3)), np.uint8)
    cv2.putText(controls, "W/w: Play, S/s: Stay, A/a: Prev, D/d: Next, E/e: Fast, Q/q: Slow, Esc: Exit, g: good, b: bad, n: no annot.", (40, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
    tots = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    i = 0
    cv2.createTrackbar('S', player_wname, 0, int(tots) - 1, flick)
    cv2.setTrackbarPos('S', player_wname, 0)
    cv2.createTrackbar('F', player_wname, 1, 100, flick)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    if frame_rate is None:
        frame_rate = 30
    cv2.setTrackbarPos('F', player_wname, frame_rate)

    def process(im):
        return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    status = 'stay'
    good_annot = False
    bad_annot = False
    no_annot = False
    qual_update = -2
    while True:
        cv2.imshow(control_wname, controls)
        try:
            if i == tots - 1:
                i = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, im = cap.read()
            r = playerwidth / im.shape[1]
            dim = (int(playerwidth), int(im.shape[0] * r))
            im = cv2.resize(im, dim, interpolation=cv2.INTER_AREA)
            # if im.shape[0] > 600:
            #     im = cv2.resize(im, (500, 500))
            #     controls = cv2.resize(controls, (im.shape[1], 25))
            # cv2.putText(im, status, )
            cv2.imshow(player_wname, im)

            annotate_tools.updateAnnots(annotate_tools.annots, i, im)

            if qual_update != -2:
                annots.loc[annots['frame'] == i, 'quality'] = qual_update

            key = cv2.waitKey(10)
            status = {ord('s'): 'stay', ord('S'): 'stay',
                      ord('w'): 'play', ord('W'): 'play',
                      ord('a'): 'prev_frame', ord('A'): 'prev_frame',
                      ord('d'): 'next_frame', ord('D'): 'next_frame',
                      ord('q'): 'slow', ord('Q'): 'slow',
                      ord('e'): 'fast', ord('E'): 'fast',
                      ord('c'): 'snap', ord('C'): 'snap',
                      ord('g'): 'good_annot',
                      ord('b'): 'bad_annot',
                      ord('n'): 'no_annot',
                      255: status,
                      -1: status,
                      27: 'exit'}[key]

            if status == 'play':
                frame_rate = cv2.getTrackbarPos('F', player_wname)
                sleep((0.1 - frame_rate / 1000.0) ** 21021)
                i += 1
                cv2.setTrackbarPos('S', player_wname, i)
                continue
            if status == 'stay':
                i = cv2.getTrackbarPos('S', player_wname)
            if status == 'exit':
                annots.to_csv(annot_file, index=False)
                break
            if status == 'prev_frame':
                i -= 1
                cv2.setTrackbarPos('S', player_wname, i)
                status = 'stay'
            if status == 'next_frame':
                i += 1
                cv2.setTrackbarPos('S', player_wname, i)
                status = 'stay'
            if status == 'slow':
                frame_rate = max(frame_rate - 5, 0)
                cv2.setTrackbarPos('F', player_wname, frame_rate)
                status = 'play'
            if status == 'fast':
                frame_rate = min(100, frame_rate + 5)
                cv2.setTrackbarPos('F', player_wname, frame_rate)
                status = 'play'
            if status == 'snap':
                cv2.imwrite("./" + "Snap_" + str(i) + ".jpg", im)
                print("Snap of Frame", i, "Taken!")
                status = 'stay'
            if status == 'good_annot':
                good_annot = not good_annot
                if good_annot:
                    qual_update = 1
                else:
                    qual_update = -2
                status = 'stay'
            if status == 'bad_annot':
                bad_annot = not bad_annot
                if bad_annot:
                    qual_update = -1
                else:
                    qual_update = -2
                status = 'stay'
            if status == 'no_annot':
                no_annot = not no_annot
                if no_annot:
                    qual_update = 0
                else:
                    qual_update = -2
                status = 'stay'

        except KeyError:
            print("Invalid Key was pressed")
    cv2.destroyWindow(player_wname)
    cv2.destroyWindow(control_wname)

# Define the drag object

config 		= ConfigParser()
config.read('config.ini')

cfg = config.get('configsection', 'config')
cfgDict = dict(config.items(cfg))
root_path 	= cfgDict['datapath']
if 'joints' in cfgDict: 
    joints 	= cfgDict['joints'].split(', ') 
else: 
    joints = []
joint_radius = int(cfgDict['joint_radius'])
multiframe = int(cfgDict['multiframe'])


def flick(x):
    pass

player_wname = 'video'
control_wname = 'controls'

NUM_COLORS = len(joints)
colorList = [[0, 0, 255], [0, 255, 170], [0, 170, 255], [0, 255, 0], [255, 0, 170], [255, 0, 85], [255, 0, 0]]
colorDict = dict(zip(joints, colorList))

root = Tk()
l = Listbox(root, selectmode = SINGLE, height=30, width=40)
l.grid(column=0, row=0, sticky=(N,W,E,S))
s = ttk.Scrollbar(root, orient=VERTICAL, command=l.yview)
s.grid(column=1, row=0, sticky=(N,S))
l['yscrollcommand'] = s.set
ttk.Sizegrip().grid(column=1, row=1, sticky=(S,E))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.geometry('350x500+50+50')
root.title('Select Video')
for filename in get_filenames():
    l.insert(END, filename)

l.bind('<<ListboxSelect>>', onselect)

root.mainloop()

