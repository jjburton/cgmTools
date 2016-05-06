import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
import Red9.core.Red9_Meta as r9Meta
from cgm.core.rigger import RigFactory as Rig
#======================================================================

cgmPM.cgmSimpleBSFace(name = 'm1_face')

face1 = cgmMeta.cgmNode('m1_face_part')#...creation
face1.__verify__()
#...connecting stuff
face1.rigNull.geo_bridgeHead = 'M1_Head_bridge_geo'
face1.rigNull.geo_head = 'M1_Head_geo'
face1.rigNull.bsNode_bridge = 'faceBridge_bsNode'
face1.rigNull.gui_cam = 'faceCam'
face1.rigNull.gui_main = 'facialRig_gui'
face1.rigNull.bsNode_bridge = 'faceBridge_bsNode'

face1.templateNull.rigBlock_eye_left = 'l_eye_rigHelper'
face1.templateNull.rigBlock_eye_right = 'r_eye_rigHelper'
face1.templateNull.rigBlock_face_lwr = 'mouthNose_rigHelper'
face1.templateNull.rigBlock_face_upr = 'brow_rigHelper'


face1.rigNull.msgList_connect(mc.ls(sl=True),'bsNodes','driving')
face1.rigNull.msgList_connect(mc.ls(sl=True),'controlsAll')

#mirroring
from Red9.core import Red9_AnimationUtils as r9Anim
r9Anim.MirrorHierarchy().makeSymmetrical(face1.rigNull.msgList_get('controlsAll',False),mode = '',primeAxis = 'Left')
r9Anim.MirrorHierarchy().mirrorData(face1.rigNull.msgList_get('controlsAll',False),mode = '')

#...setup
for obj in face1.rigNull.msgList_get('controlsAll',False):
    mi_obj = cgmMeta.validateObjArg(obj,'cgmControl',setClass = True)
    mi_obj._verifyMirrorable()

#do centre, left, right
for i,mi_obj in enumerate(cgmMeta.validateObjListArg(mc.ls(sl=True))):
    mi_obj.mirrorSide = 'Right'
    mi_obj.mirrorIndex = i
    



