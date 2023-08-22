"""
------------------------------------------
camera_utils: cgm.core.lib
Author: David Bokser
email: dbokser@cgmonks.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
import pprint
import maya.cmds as mc
import cgm.core.lib.transform_utils as TRANS
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.shape_utils as SHAPE

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

def getCurrentPanel():
    panel = mc.getPanel(withFocus=True)
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                break
        
    return panel if mc.getPanel(typeOf=panel) == 'modelPanel' else None

def getCurrentCamera():   
    panel = getCurrentPanel()
        
    return mc.modelEditor(panel, query=True, camera=True) if panel else None


def autoset_clipPlane():
    _str_func = 'autoset_clipPlane'
    _cam = getCurrentCamera()
    
    _eligible = SHAPE.get_eligibleMesh()
    _sel = VALID.objStringList(mc.ls(sl=1) or _eligible,calledFrom=_str_func)
        
    _size = TRANS.bbSize_get(_sel,True,'max')
    _farSize =  TRANS.bbSize_get(_eligible,True,'max')
    
    _near =  _size*0.1
    _far = _farSize*10
    
    log.info(log_msg(_str_func,"near: {} || far: {}".format(_near,_far)))
    mc.setAttr(_cam + '.nearClipPlane', _near)
    mc.setAttr(_cam + '.farClipPlane', _far)    
    
def worldToScreen(point):
    # # convert world space position to screen space
    #
    # # Usage example
    # world_point = mc.xform('locator1', query=True, worldSpace=True, translation=True)
    # print(world_to_screen(world_point))

    # Get world space position
    world_point = om.MPoint(point[0], point[1], point[2])

    # Get active view
    active_view = omui.M3dView.active3dView()

    # Get camera
    camera = om.MDagPath()
    active_view.getCamera(camera)

    # Get camera's world matrix (this is the model view matrix)
    camera_matrix = camera.inclusiveMatrix()

    # Create a transformation matrix from camera's world matrix
    camera_transform = om.MTransformationMatrix(camera_matrix)

    # Get camera's translation (position)
    camera_point = camera_transform.getTranslation(om.MSpace.kWorld)

    # Get camera's forward direction (negative z-axis)
    local_forward_vector = om.MVector(0, 0, -1)
    world_forward_vector = local_forward_vector * camera_matrix.inverse()

    # Calculate the vector from the camera to the point
    camera_to_point_vector = om.MVector(world_point) - om.MVector(camera_point)

    # If the dot product is negative, the point is behind the camera, so return None
    if camera_to_point_vector * world_forward_vector < 0:
        return None

    # Get camera function set
    camera_fn = om.MFnCamera(camera)

    # Get projection matrix
    projection_matrix = om.MMatrix(camera_fn.projectionMatrix().matrix)

    # Multiply point by model view and projection matrices
    homogenous_point = world_point * camera_matrix.inverse() * projection_matrix

    # Normalize x and y by w if w is not zero
    if abs(homogenous_point.w) > 1e-6:  # avoid division by a very small number
        normalized_point = om.MPoint(homogenous_point.x / homogenous_point.w,
                                     homogenous_point.y / homogenous_point.w)
    else:
        return [None, None]

    # Get viewport size
    viewport_width = active_view.portWidth()
    viewport_height = active_view.portHeight()

    # Convert normalized coordinates to screen space
    screen_point = om.MPoint((normalized_point.x + 1.0) / 2.0 * viewport_width,
                             (normalized_point.y + 1.0) / 2.0 * viewport_height)

    return [screen_point.x / viewport_width, screen_point.y / viewport_height]

def screenToWorld(screen_pos, distance, asEuclid=False, camera_shape=None):
    # Get view and camera based on camera_name
    active_view = omui.M3dView.active3dView()        

    # Get viewport size
    viewport_width = active_view.portWidth()
    viewport_height = active_view.portHeight()

    # Convert screen space coordinates to normalized device coordinates
    normalized_point = om.MPoint(screen_pos[0] * viewport_width,
                                 screen_pos[1] * viewport_height)

    # Convert normalized device coordinates to clip space
    clip_space_point = om.MPoint((normalized_point.x / viewport_width) * 2.0 - 1.0,
                                 (normalized_point.y / viewport_height) * 2.0 - 1.0,
                                 -1 + 2 * distance)  # z in clip space is between -1 and 1

    # Get camera
    camera = om.MDagPath()
    active_view.getCamera(camera)

    # Get camera's world matrix (this is the model view matrix)
    camera_matrix = camera.inclusiveMatrix()

    # Get camera function set
    camera_fn = om.MFnCamera(camera)

    # Get projection matrix
    projection_matrix = om.MMatrix(camera_fn.projectionMatrix().matrix)

    # Multiply point by inverse projection and model view matrices
    homogenous_world_point = clip_space_point * projection_matrix.inverse() * camera_matrix


    returnPos = [world_point.x, world_point.y, world_point.z]
    
    if asEuclid:
        returnPos = VALID.euclidVector3Arg(returnPos)
    return returnPos

def get3dViewFromCamera(camera_shape):
    """Return the M3dView associated with the given camera name."""
    
    # First, get the MDagPath of the provided camera name
    sel_list = om.MSelectionList()
    sel_list.add(camera_shape)
    camera_path = om.MDagPath()
    sel_list.getDagPath(0, camera_path)

    # Loop through available 3D views to find the one using the specified camera
    for i in range(omui.M3dView.numberOf3dViews()):  
        temp_view = omui.M3dView()
        omui.M3dView.get3dView(i, temp_view)
        temp_camera = om.MDagPath()
        temp_view.getCamera(temp_camera)
        if temp_camera == camera_path:
            return temp_view

    raise ValueError(f"No 3D view found associated with camera {camera_shape}.")
