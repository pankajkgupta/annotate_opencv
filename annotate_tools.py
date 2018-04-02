import cv2

class Rect:
    x = None
    y = None
    w = None
    h = None

    def printit(self):
        print str(self.x) + ',' + str(self.y) + ',' + str(self.w) + ',' + str(self.h)
        
class Circle:
    x = None
    y = None
    r = 6
    # Drag in progress
    drag = False
    # already present
    active = True
    # Marker flags by positions
    hold = False
    label = ''

    def __init__(self, label):
        self.label = label

    def printit(self):
        print str(self.x) + ',' + str(self.y) + ',' + str(self.r)

# endclass

class annots:
    # Limits on the canvas
    keepWithin = Rect()

    # To store rectangle anchor point
    # Here the rect class object is used to store
    # the distance in the x and y direction from
    # the anchor point to the top-left and the bottom-right corner
    anchor = {}
    # Selection marker size
    sBlk = 2
    # Whether initialized or not
    initialized = False

    joints = {}

    # Image
    image = None

    # Window Name
    wname = ""

    # Return flag
    returnflag = False

    frame_n = 0
    joints_df = []
    colorDict = {}
    def __init__(self, label):
        self.label = label
        # To store circle
        self.joints[label] = Circle(label)
        self.anchor[label] = Circle(label)

# endclass


def init(annot_obj, joints, annots_df, windowName, windowWidth, windowHeight, colormap):
    # Image
    # annot_obj.image = Img

    # Window name
    annot_obj.wname = windowName
    annot_obj.joints_df = annots_df
    # Limit the selection box to the canvas
    annot_obj.keepWithin.x = 0
    annot_obj.keepWithin.y = 0
    annot_obj.keepWithin.w = windowWidth
    annot_obj.keepWithin.h = windowHeight

    annot_obj.colorDict = colormap
    frame_n = 0
    for jt in joints:
        annot_obj(jt)
        # Set rect to zero width and height
        annot_obj.joints[jt].x = 0
        annot_obj.joints[jt].y = 0
        annot_obj.joints[jt].r = 6
        annot_obj.active = True


# enddef

def dragcircle(event, x, y, flags, dragObj):
    if x < dragObj.keepWithin.x:
        x = dragObj.keepWithin.x
    # endif
    if y < dragObj.keepWithin.y:
        y = dragObj.keepWithin.y
    # endif
    if x > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
        x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1
    # endif
    if y > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
        y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1
    # endif

    jt = None
    for joint_name in dragObj.joints:
        joint = dragObj.joints[joint_name]

        if joint.x == 'nan':
            continue

        if pointInCircle(x, y, int(joint.x), int(joint.y), joint.r):
            jt = dragObj.joints[joint_name]
            break

    if jt is None:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        mouseDown(x, y, dragObj, jt)
    # endif
    if event == cv2.EVENT_LBUTTONUP:
        mouseUp(x, y, dragObj, jt)
    # endif
    if event == cv2.EVENT_MOUSEMOVE:
        mouseMove(x, y, dragObj, jt)
    # endif
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseDoubleClick(x, y, dragObj, jt)
    # endif

# enddef

# def pointInRect(pX, pY, rX, rY, rW, rH):
def pointInCircle(pX, pY, rX, rY, rR):
    if ((pX - rX)**2 ) + ((pY - rY)**2) < rR**2:
    # if rX <= pX <= (rX + rW) and rY <= pY <= (rY + rH):
        return True
    else:
        return False
    # endelseif

# enddef

def updateAnnots(annots_obj, frame_n, im):

    joints = annots_obj.joints.keys()
    annot_df = annots_obj.joints_df[annots_obj.joints_df.frame_n == frame_n][joints]
    if annot_df.empty:
        return
    # This has to be below all of the other conditions
    # if pointInCircle(eX, eY, dragObj.outCircle.x, dragObj.outCircle.y, dragObj.outCircle.r):
    annots_obj.image = im
    annots_obj.frame_n = frame_n
    for joint in annot_df:
        annots_obj.joints[joint].x, annots_obj.joints[joint].y = annot_df[joint].values[0].split('-')

    clearCanvasNDraw(annots_obj)
    return

def mouseDoubleClick(eX, eY, dragObj, jt):
    if jt.active:

        # if pointInCircle(eX, eY, dragObj.outCircle.x, dragObj.outCircle.y, dragObj.outCircle.r):
        dragObj.returnflag = True
        cv2.destroyWindow(dragObj.wname)
        # endif

    # endif


# enddef

def mouseDown(eX, eY, dragObj,jt):
    if jt.active:

        # This has to be below all of the other conditions
        # if pointInCircle(eX, eY, dragObj.outCircle.x, dragObj.outCircle.y, dragObj.outCircle.r):
        dragObj.anchor[jt.label].x = eX - int(jt.x)
        dragObj.anchor[jt.label].y = eY - int(jt.y)
        jt.hold = True
        # jt.drag = True
        return

    else:
        jt.x = eX
        jt.y = eY
        jt.drag = True
        jt.active = True
        return

# enddef

def mouseMove(eX, eY, dragObj, jt):
    if jt.drag & dragObj.active:
        clearCanvasNDraw(dragObj)
        return
    # endif

    if jt.hold:
        jt.x = eX - dragObj.anchor[jt.label].x
        jt.y = eY - dragObj.anchor[jt.label].y

        if jt.x < dragObj.keepWithin.x:
            jt.x = dragObj.keepWithin.x
        # endif
        if jt.y < dragObj.keepWithin.y:
            jt.y = dragObj.keepWithin.y
        # endif
        if (jt.x + jt.r) > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
            jt.x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1 - jt.r
        # endif
        if (jt.y + jt.r) > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
            jt.y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1 - jt.r
        # endif

        dragObj.joints_df.loc[dragObj.joints_df['frame_n'] == dragObj.frame_n, jt.label] = str(jt.x) + '-' + str(jt.y)
        clearCanvasNDraw(dragObj)
        return
    # endif


# enddef

def mouseUp(eX, eY, dragObj, jt):
    jt.drag = False
    disableResizeButtons(dragObj)
    jt.hold = False
    jt.active =False

    # endif

    clearCanvasNDraw(dragObj)

# enddef

def disableResizeButtons(dragObj):
    dragObj.hold = False


# enddef

def clearCanvasNDraw(dragObj):
    # Draw
    tmp = dragObj.image.copy()
    tmp1 = dragObj.image.copy()
    for joint_name in dragObj.joints:
        joint = dragObj.joints[joint_name]
        if joint.x == 'nan':
            return
        cv2.circle(tmp, (int(joint.x), int(joint.y)),
               joint.r, dragObj.colorDict[joint_name], -1)
    # apply the overlay
    cv2.addWeighted(tmp, 0.5, tmp1, 0.5, 0, tmp1)
    cv2.imshow(dragObj.wname, tmp1)
    # cv2.waitKey()


# enddef
