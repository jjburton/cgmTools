import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST
from cgm.core import cgm_General as cgmGEN

import maya.cmds as mc
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


"""
mc.delete(mc.ls(type='positionMarker'))
mBlock.moduleTarget.rigNull.msgList_get('moduleJoints')
mBlock.atUtils('skeletonized_query')
l_startSnap = [[-0.00018139342393015353, 7.605513570170998, -66.5626329131333], [-0.00018139342392977642, 10.684854532060829, -59.775072715719574], [-0.00018139342392956887, 12.379601233577182, -51.42832399692508], [0.5210297752251732, 15.19091061410884, -40.06570333283602]]
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    for i,p in enumerate(l_startSnap):
        POS.set("{0}.cv[{1}]".format(mObj.mNode,i), p)

mc.ls(sl=1)
mWheel = cgmMeta.asMeta('socket_wheel')
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    mObj.doSnapTo(mWheel)
    
cgmMeta.asMeta(sl=1)[0].dagLock(False)
l_sl = []    
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    l_sl.append(mObj.mNode)
    mPath = cgmMeta.asMeta(mc.listConnections(mObj.mNode, type='motionPath')[0])
    l_sl.append(mPath.mNode)
mc.select(l_sl)

mc.listConnections('outro_stuff_rework|exit_p2c1|exit_p2c1Shape->|orientationMarker94|orientationMarkerShape94')
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    print mc.listConnections(mObj.getShapes()[0],type='positionMarker')

l_startSnap = [[-0.00018139342393015353, 7.605513570170998, -66.5626329131333], [-0.00018139342392977642, 10.684854532060829, -59.775072715719574], [-0.00018139342392956887, 12.379601233577182, -51.42832399692508], [0.5210297752251732, 15.19091061410884, -40.06570333283602]]
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    for i,p in enumerate(l_startSnap):
        POS.set("{0}.cv[{1}]".format(mObj.mNode,i), p)
cgmGEN.__mayaVersion__
reload(ATTR)
#Snap pivot 1 to match targets...
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    mMatch = mObj.getMessageAsMeta('cgmMatchTarget')
    ml_space = mObj.msgList_get('spacePivots')
    print mMatch
    print ml_space
    mc.parentConstraint([mMatch.mNode],ml_space[0].mNode,maintainOffset = False)
    
#Snap  
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    ml_space = mObj.msgList_get('spacePivots')
    mc.parentConstraint(['holdem_sockets:startScoket'],ml_space[1].mNode,maintainOffset = False) 
    
for mObj in cgmMeta.asMeta(sl=1):
    print mObj

for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    print mObj
    
    
mLoc = cgmMeta.asMeta(mc.spaceLocator()[0])
mLoc2 = cgmMeta.asMeta(mc.spaceLocator()[0])

mLoc.doConnectOut('ty',"{0}.ty".format(mLoc2.mNode))
mLoc.doConnectIn('tx',"{0}.tx".format(mLoc2.mNode))



"""
size_hide = .001
size_enter = .5

d_snapTargets = {'start':{'to':'holdem_sockets:socket_start','s':.001},
                'deal':{'to':'holdem_sockets:socket_deal_1','s':.5},
                'deal2':{'to':'holdem_sockets:socket_deal_2','s':.5},
                'dealRev':{'to':'holdem_sockets:socket_deal_rev_1','s':.5},
                'dealRev2':{'to':'holdem_sockets:socket_deal_rev_2','s':.5},                
                'collect':{'to':'holdem_sockets:socket_collect_1','s':.5},
                'collect2':{'to':'holdem_sockets:socket_collect_2','s':.001}}

def cards_snapTo(nodes = None, mode='start'):
    _mode = d_snapTargets
    
    if not nodes:
        mNodes = cgmMeta.asMeta(sl=1)
    else:
        mNodes = cgmMeta.asMeta(nodes)
        
    _d = _mode.get(mode)
    for mObj in mNodes:
        mObj.doSnapTo(_d['to'])
        mObj.scaleY = _d['s']
        mc.setKeyframe(mObj.mNode)


def cards_snap(nodes = None, mode='collect', hold = 2):
    if not nodes:
        mNodes = cgmMeta.asMeta(sl=1)
    else:
        mNodes = cgmMeta.asMeta(nodes)
        
    _current = mc.currentTime(q=True)
    _cnt = 0
    
    _d_start = d_snapTargets.get('start')
    
    for mObj in mNodes:
        if mode == 'collect':
            _d = d_snapTargets.get('collect')
            mc.currentTime(_current)
            
            mObj.doSnapTo(_d['to'],rotation=False)
            mObj.scaleY = size_enter
            mc.setKeyframe(mObj.mNode)
            
            _rot = mObj.rotate
            
            _cnt = 1
            _d = d_snapTargets.get('collect2')
            
            for i in range(hold+4):
                mc.currentTime(_current+_cnt)
                if i>hold:
                    mObj.doSnapTo(_d_start['to'],rotation=False)
                else:                
                    mObj.doSnapTo(_d['to'],rotation=False)
                    
                mObj.scaleY = size_hide
                    
                mObj.rotate = _rot
                mc.setKeyframe(mObj.mNode)
                _cnt+=1
                
            mc.currentTime(_current+_cnt)
            _d = d_snapTargets.get('start')
            
            mObj.doSnapTo(_d['to'])
            mObj.scaleY = _d['s']
            mc.setKeyframe(mObj.mNode)            

        elif mode == 'deal':
            _d = d_snapTargets.get('deal')
            
            mc.currentTime(_current)
            
            mObj.doSnapTo(_d['to'],rotation=1)
            mObj.scaleY = size_enter
            mc.setKeyframe(mObj.mNode)
            
            _cnt = 1
            
            _d = d_snapTargets.get('deal2')
            for i in range(hold):
                mc.currentTime(_current-_cnt)
                mObj.doSnapTo(_d['to'],rotation=1)
                if i:
                    mObj.scaleY = size_hide
                else:
                    mObj.scaleY = size_enter
                    
                mc.setKeyframe(mObj.mNode)
                _cnt+=1
                
            #mc.currentTime(_current-_cnt)
            
            #mObj.doSnapTo(_d_start['to'])
            #mObj.scaleY = _d_start['s']
            ##mc.setKeyframe(mObj.mNode)
        else:#...deal reverse
            _d = d_snapTargets.get('dealRev')
            
            mc.currentTime(_current)
            
            mObj.doSnapTo(_d['to'],rotation=1)
            mObj.scaleY = size_enter
            mc.setKeyframe(mObj.mNode)
            
            _cnt = 1
            
            _d = d_snapTargets.get('dealRev2')
            for i in range(hold):
                mc.currentTime(_current-_cnt)
                mObj.doSnapTo(_d['to'],rotation=1)
                if i:
                    mObj.scaleY = size_hide
                else:
                    mObj.scaleY = size_enter
                    
                mc.setKeyframe(mObj.mNode)
                _cnt+=1            
        
    mc.currentTime(_current)
    log.info(_cnt)

def cards_constrainToSockects():
    _str_func = cards_constrainToSockects
    _d = {'p1c1':'seating:seat1_root|seating:card1_socket',
          'p1c2':'seating:seat1_root|seating:card2_socket',
          'p2c1':'seating:seat2_root|seating:card1_socket',
          'p2c2':'seating:seat2_root|seating:card2_socket',
          'p3c1':'seating:seat3_root|seating:card1_socket',
          'p3c2':'seating:seat3_root|seating:card2_socket',
          'p4c1':'seating:seat4_root|seating:card1_socket',
          'p4c2':'seating:seat4_root|seating:card2_socket',
          'p5c1':'seating:seat5_root|seating:card1_socket',
          'p5c2':'seating:seat5_root|seating:card2_socket',
          'p6c1':'seating:seat6_root|seating:card1_socket',
          'p6c2':'seating:seat6_root|seating:card2_socket',
          'p7c1':'seating:seat7_root|seating:card1_socket',
          'p7c2':'seating:seat7_root|seating:card2_socket',
          'flop1':'holdem_sockets:socket_table1',
          'flop2':'holdem_sockets:socket_table2',
          'flop3':'holdem_sockets:socket_table3',
          'turn':'holdem_sockets:socket_table4',
          'river':'holdem_sockets:socket_table5',}
    
    
    
    for k,t in _d.iteritems():
        mObj = cgmMeta.asMeta("{0}:rootMotion_anim".format(k))
        if not mObj:
            log.error("Failed to find: {0}".format(k))
            continue
        
        l_constraints = mObj.getConstraintsTo()
        if l_constraints:
            mc.delete(l_constraints)
            
        
        mc.parentConstraint(t, mObj.mNode, maintainOffset = 0)
        
        

'''
Rest
brow_dn
brow_thicken
brow_up
eye_dn
eye_left
eye_open
eye_right
eye_up
jaw_back
jaw_close
jaw_dn
jaw_fwd
jaw_right
lid_arcDn
lid_arcUp
lid_lwrOpen
lid_uprOpen
lips_close_left
lips_close_right
lips_frown_left
lips_frown_right
lips_narrow_left
lips_narrow_right
lips_smile_left
lips_smile_right
lips_sneer_left
lips_sneer_right
lips_teethLip_left
lips_teethLip_right
lips_wide_left
lips_wide_right
mouth_dn
mouth_left
mouth_right
mouth_up
orb_angry
orb_arcDn
orb_arcUp
orb_blink
orb_bottomSqueeze
orb_surprise
orb_frustrated
orb_sad
hide_smirk_lwr
hide_smirk_left
hide_smirk_right
hide_tusk_left
hide_tusk_right
'''


_d_faceWiring = {
    'Grag':{
    'orb':{'control':'orb_anim',
           'wiringDict':{'orb_surprise':{'driverAttr':'ty'},
                         'orb_frustrated':{'driverAttr':'-ty'},
                         'orb_angry':{'driverAttr':'-tx'},
                         'orb_sad':{'driverAttr':'tx'},
                         }},
    'eyebrow':{'control':'brow_anim',
           'wiringDict':{'brow_dn':{'driverAttr':'-ty'},
                         'brow_up':{'driverAttr':'ty'},
                         'brow_thicken':{'driverAttr':'-tx'},
                         }},
    'eye':{'control':'eye_anim',
           'wiringDict':{'eye_up':{'driverAttr':'ty'},
                         'eye_dn':{'driverAttr':'-ty'},
                         'eye_right':{'driverAttr':'-tx'},
                         'eye_left':{'driverAttr':'tx'},
                         }},
    'lidLwr':{'control':'lidLwr_open_anim',
           'wiringDict':{'lid_lwrOpen':{'driverAttr':'ty'},
                         }},
    'lidUpr':{'control':'lidUpr_open_anim',
           'wiringDict':{'lid_uprOpen':{'driverAttr':'ty'},
                         }},
    'blink':{'control':'blink_anim',
           'wiringDict':{'orb_blink':{'driverAttr':'ty'},
                         }},
    'blinkArc':{'control':'blinkArc_anim',
           'wiringDict':{'orb_arcUp':{'driverAttr':'ty'},
                         'orb_arcDn':{'driverAttr':'-ty'},
                         }},
    'lidArc':{'control':'lidArc_anim',
           'wiringDict':{'lid_arcUp':{'driverAttr':'ty'},
                         'lid_arcDn':{'driverAttr':'-ty'},
                         }},
    'orbUp':{'control':'orbUp_anim',
           'wiringDict':{'orb_bottomSqueeze':{'driverAttr':'ty'}}},
    
    
    'jaw_stuff':{'control':'jaw_anim',
           'wiringDict':{'jaw_close':{'driverAttr':'ty'},
                         'jaw_dn':{'driverAttr':'-ty'},
                         'jaw_left':{'driverAttr':'tx'},
                         'jaw_right':{'driverAttr':'-tx'},
                         }},
    
    'jaw_fwdBack':{'control':'jaw_fwdBck_anim',
           'wiringDict':{'jaw_fwd':{'driverAttr':'tx'},
                         'jaw_back':{'driverAttr':'-tx'},
                         }},
    
    #Lips--------------------
    'sneer':{'control':'sneer_anim',
           'wiringDict':{'lips_sneer_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lips_sneer_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    'lipClose':{'control':'lipClose_anim',
           'wiringDict':{'lips_close_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lips_close_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},

    'mouth':{'control':'mouth_anim',
           'wiringDict':{'mouth_up':{'driverAttr':'ty'},
                         'mouth_dn':{'driverAttr':'-ty'},
                         'mouth_left':{'driverAttr':'tx'},
                         'mouth_right':{'driverAttr':'-tx'},
                         }},    
    
    
    
    
    'lipCorner_left':{'control':'l_lipCorner_anim',
                      'wiringDict':{'lips_smile_left':{'driverAttr':'ty'},
                                    'lips_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_left':{'driverAttr':'-tx'},
                                    'lips_wide_left':{'driverAttr':'tx'}}},
    'lipCorner_right':{'control':'r_lipCorner_anim',
                      'wiringDict':{'lips_smile_right':{'driverAttr':'ty'},
                                    'lips_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_right':{'driverAttr':'-tx'},
                                    'lips_wide_right':{'driverAttr':'tx'}}},    
    
    'lipTeeth_right':{'control':'r_lipTeeth_anim',
           'wiringDict':{'lips_teethLip_right':{'driverAttr':'ty'}}},    
    'hide_tusk_right':{'control':'r_hideTusk_anim',
           'wiringDict':{'hide_tusk_right':{'driverAttr':'ty'}}},
    
    'lipTeeth_left':{'control':'l_lipTeeth_anim',
           'wiringDict':{'lips_teethLip_left':{'driverAttr':'ty'}}},    
    'hide_tusk_left':{'control':'l_hideTusk_anim',
           'wiringDict':{'hide_tusk_left':{'driverAttr':'ty'}}},    
    
    #Hide stuff ....
    'hide_smirk':{'control':'hide_smirkLw_anim',
           'wiringDict':{'hide_smirk_lwr':{'driverAttr':'-ty'}}},
    'hide_smirk_left':{'control':'hide_smirk_left_anim',
           'wiringDict':{'hide_smirk_left':{'driverAttr':'-ty'}}},
    'hide_smirk_right':{'control':'hide_smirk_right_anim',
           'wiringDict':{'hide_smirk_right':{'driverAttr':'-ty'}}},    
    
    },
    'test':{
                      
    'inner_brow_left':{'control':'l_inner_brow_anim',
                       'wiringDict':{'brow_inr_up_left':{'driverAttr':'ty'},
                                     'brow_inr_dn_left':{'driverAttr':'-ty'},
                                     'brow_squeeze_left':{'driverAttr':'-tx'}}},                             
    'mid_brow_left':{'control':'l_mid_brow_anim',
                     'wiringDict':{'brow_mid_up_left':{'driverAttr':'ty'},
                                   'brow_mid_dn_left':{'driverAttr':'-ty'}}}, 
    'outer_brow_left':{'control':'l_outer_brow_anim',
                       'wiringDict':{'brow_outr_up_left':{'driverAttr':'ty'},
                                     'brow_outr_dn_left':{'driverAttr':'-ty'}}},
    'inner_brow_right':{'control':'r_inner_brow_anim',
                       'wiringDict':{'brow_inr_up_right':{'driverAttr':'ty'},
                                     'brow_inr_dn_right':{'driverAttr':'-ty'},
                                     'brow_squeeze_right':{'driverAttr':'-tx'}}},                             
    'mid_brow_right':{'control':'r_mid_brow_anim',
                     'wiringDict':{'brow_mid_up_right':{'driverAttr':'ty'},
                                   'brow_mid_dn_right':{'driverAttr':'-ty'}}}, 
    'outer_brow_right':{'control':'r_outer_brow_anim',
                       'wiringDict':{'brow_outr_up_right':{'driverAttr':'ty'},
                                     'brow_outr_dn_right':{'driverAttr':'-ty'}}}, 
    
    'eyeSqueeze_left':{'control':'l_eyeSqueeze_anim',
                       'wiringDict':{'eyeSqueeze_up_left':{'driverAttr':'ty'},
                                     'eyeSqueeze_dn_left':{'driverAttr':'-ty'}}}, 
    'eyeSqueeze_right':{'control':'r_eyeSqueeze_anim',
                       'wiringDict':{'eyeSqueeze_up_right':{'driverAttr':'ty'},
                                     'eyeSqueeze_dn_right':{'driverAttr':'-ty'}}}, 
    
    
    'cheek_left':{'control':'l_cheek_anim',
                  'wiringDict':{'cheek_up_left':{'driverAttr':'ty'},
                                'cheek_dn_left':{'driverAttr':'-ty'},
                                'cheek_blow_left':{'driverAttr':'tx'},
                                'cheek_suck_left':{'driverAttr':'-tx'}}},
    'cheek_right':{'control':'r_cheek_anim',
                  'wiringDict':{'cheek_up_right':{'driverAttr':'ty'},
                                'cheek_dn_right':{'driverAttr':'-ty'},
                                'cheek_blow_right':{'driverAttr':'tx'},
                                'cheek_suck_right':{'driverAttr':'-tx'}}},   
    
    'nose_left':{'control':'l_nose_anim',
                 'wiringDict':{'nose_in_left':{'driverAttr':'-tx'},
                               'nose_out_left':{'driverAttr':'tx'},
                               'nose_sneer_up_left':{'driverAttr':'ty'},
                               'nose_sneer_dn_left':{'driverAttr':'-ty'}},
                 'simpleArgs':['{0}.nose_seal_up_cntr_left = {0}.nose_sneer_up_left * {0}.seal_center',
                               '{0}.nose_seal_up_outr_left = {0}.nose_sneer_up_left * {0}.seal_left'
                               ]},
    'nose_right':{'control':'r_nose_anim',
                 'wiringDict':{'nose_in_right':{'driverAttr':'-tx'},
                               'nose_out_right':{'driverAttr':'tx'},
                               'nose_sneer_up_right':{'driverAttr':'ty'},
                               'nose_sneer_dn_right':{'driverAttr':'-ty'}},
                 'simpleArgs':['{0}.nose_seal_up_cntr_right = {0}.nose_sneer_up_right * {0}.seal_center',
                               '{0}.nose_seal_up_outr_right = {0}.nose_sneer_up_right * {0}.seal_right',
                               ]},
    
    'lipCorner_left':{'control':'l_lipCorner_anim',
                      'wiringDict':{'lips_purse_left':{'driverAttr':'purse'},
                                    'lips_out_left':{'driverAttr':'out'},
                                    'lips_twistUp_left':{'driverAttr':'twist'},
                                    'lips_twistDn_left':{'driverAttr':'-twist'},
                                    'lips_smile_left':{'driverAttr':'ty'},
                                    'lips_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_left':{'driverAttr':'-tx'},
                                    'lips_wide_left':{'driverAttr':'tx'}}},
    'lipCorner_right':{'control':'r_lipCorner_anim',
                      'wiringDict':{'lips_purse_right':{'driverAttr':'purse'},
                                    'lips_out_right':{'driverAttr':'out'},
                                    'lips_twistUp_right':{'driverAttr':'twist'},
                                    'lips_twistDn_right':{'driverAttr':'-twist'},
                                    'lips_smile_right':{'driverAttr':'ty'},
                                    'lips_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_right':{'driverAttr':'-tx'},
                                    'lips_wide_right':{'driverAttr':'tx'}}},},
    
    
'ren':{
    
    #Eye... -----------------------------------------------
    'L_eye':{'control':'L_eye_anim',
           'wiringDict':{'eye_up_left':{'driverAttr':'ty'},
                         'eye_dn_left':{'driverAttr':'-ty'},
                         'eye_right_left':{'driverAttr':'-tx'},
                         'eye_left_left':{'driverAttr':'tx'},
                         }},
    
    'R_eye':{'control':'R_eye_anim',
           'wiringDict':{'eye_up_right':{'driverAttr':'ty'},
                         'eye_dn_right':{'driverAttr':'-ty'},
                         'eye_right_right':{'driverAttr':'-tx'},
                         'eye_left_right':{'driverAttr':'tx'},
                         }},
    



    #Lid... --------------------------------------------
    'L_lidArc_anim':{'control':'L_lidArc_anim',
           'wiringDict':{'lid_arcUp_left':{'driverAttr':'ty'},
                         'lid_arcDn_left':{'driverAttr':'-ty'},
                         }},
    'L_lidLwrOpen':{'control':'L_lidLwr_open_anim',
           'wiringDict':{'lid_lwrOpen_left':{'driverAttr':'ty'},
                         }},
    'L_lidUprOpen':{'control':'L_lidUpr_open_anim',
           'wiringDict':{'lid_uprOpen_left':{'driverAttr':'ty'},
                         }},
    
    'R_lidArc_anim':{'control':'R_lidArc_anim',
           'wiringDict':{'lid_arcUp_right':{'driverAttr':'ty'},
                         'lid_arcDn_right':{'driverAttr':'-ty'},
                         }},
    'R_lidLwrOpen':{'control':'R_lidLwr_open_anim',
           'wiringDict':{'lid_lwrOpen_right':{'driverAttr':'ty'},
                         }},
    'R_lidUprOpen':{'control':'R_lidUpr_open_anim',
           'wiringDict':{'lid_uprOpen_right':{'driverAttr':'ty'},
                         }},


    
    
    #Mouth... --------------------------------------------
    'teethArc':{'control':'teeth_arcUp_anim',
           'wiringDict':{'teeth_arcUp':{'driverAttr':'ty'},
                         }},    
    
    },


'Wump':{

    
    #Brow... --------------------------------------------
    'l_eyebrow':{'control':'l_browHeight_anim',
           'wiringDict':{'brow_dn_left':{'driverAttr':'-ty'},
                         'brow_up_left':{'driverAttr':'ty'},
                         }},
    'l_eyebrowShape':{'control':'l_brow_anim',
           'wiringDict':{'brow_flatten_left':{'driverAttr':'-ty'},
                         'brow_arc_left':{'driverAttr':'ty'},
                         'brow_furrow_left':{'driverAttr':'-tx'},
                         }},    
    'r_eyebrow':{'control':'r_browHeight_anim',
           'wiringDict':{'brow_dn_right':{'driverAttr':'-ty'},
                         'brow_up_right':{'driverAttr':'ty'},
                         }},
    'r_eyebrowShape':{'control':'r_brow_anim',
           'wiringDict':{'brow_flatten_right':{'driverAttr':'-ty'},
                         'brow_arc_right':{'driverAttr':'ty'},
                         'brow_furrow_right':{'driverAttr':'-tx'},
                         }},        
    
    #Lid... --------------------------------------------
    'l_lidArc_anim':{'control':'l_lidArc_anim',
           'wiringDict':{'lid_arcUp_left':{'driverAttr':'ty'},
                         'lid_arcDn_left':{'driverAttr':'-ty'},
                         }},
    'l_lidLwrFurrow_anim':{'control':'l_lidLwrFurrow_anim',
           'wiringDict':{'lid_lwrFurrow_left':{'driverAttr':'ty'},
                         }},
    'l_lidUprFurrow_anim':{'control':'l_lidUprFurrow_anim',
           'wiringDict':{'lid_uprFurrow_left':{'driverAttr':'ty'},
                         }},
    'l_lidLwrSqueeze_anim':{'control':'l_lidLwrSqueeze_anim',
           'wiringDict':{'lid_lwrClose_left':{'driverAttr':'ty'},
                         }},    
    'l_lidUprSqueeze_anim':{'control':'l_lidUprSqueeze_anim',
           'wiringDict':{'lid_uprClose_left':{'driverAttr':'ty'},
                         }},
    
    'r_lidArc_anim':{'control':'r_lidArc_anim',
           'wiringDict':{'lid_arcUp_right':{'driverAttr':'ty'},
                         'lid_arcDn_right':{'driverAttr':'-ty'},
                         }},
    'r_lidLwrFurrow_anim':{'control':'r_lidLwrFurrow_anim',
           'wiringDict':{'lid_lwrFurrow_right':{'driverAttr':'ty'},
                         }},
    'r_lidUprFurrow_anim':{'control':'r_lidUprFurrow_anim',
           'wiringDict':{'lid_uprFurrow_right':{'driverAttr':'ty'},
                         }},
    'r_lidLwrSqueeze_anim':{'control':'r_lidLwrSqueeze_anim',
           'wiringDict':{'lid_lwrClose_right':{'driverAttr':'ty'},
                         }},    
    'r_lidUprSqueeze_anim':{'control':'r_lidUprSqueeze_anim',
           'wiringDict':{'lid_uprClose_right':{'driverAttr':'ty'},
                         }},    
    
    
    #Mouth... --------------------------------------------
    'mouth':{'control':'mouth_anim',
           'wiringDict':{'mouth_up':{'driverAttr':'ty'},
                         'mouth_dn':{'driverAttr':'-ty'},
                         'mouth_left':{'driverAttr':'tx'},
                         'mouth_right':{'driverAttr':'-tx'},
                         }},    
    'lipClose':{'control':'lipClose_anim',
           'wiringDict':{'lips_seal_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lips_seal_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    
    
    'lipCorner_left':{'control':'l_lipCorner_anim',
                      'wiringDict':{'lips_smile_left':{'driverAttr':'ty'},
                                    'lips_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_left':{'driverAttr':'-tx'},
                                    'lips_wide_left':{'driverAttr':'tx'}}},    
    'l_smileBig_anim':{'control':'l_smileBig_anim',
           'wiringDict':{'lips_smileBig_left':{'driverAttr':'ty'},
                         }},    
    'l_smirk_anim':{'control':'l_smirk_anim',
           'wiringDict':{'lips_smirk_left':{'driverAttr':'ty'},
                         }},
    'l_frownBig_anim':{'control':'l_frownBig_anim',
           'wiringDict':{'lips_frownBig_left':{'driverAttr':'ty'},
                         }},
    
    'lipCorner_right':{'control':'r_lipCorner_anim',
                      'wiringDict':{'lips_smile_right':{'driverAttr':'ty'},
                                    'lips_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_right':{'driverAttr':'-tx'},
                                    'lips_wide_right':{'driverAttr':'tx'}}},    
    'r_smileBig_anim':{'control':'r_smileBig_anim',
           'wiringDict':{'lips_smileBig_right':{'driverAttr':'ty'},
                         }},    
    'r_smirk_anim':{'control':'r_smirk_anim',
           'wiringDict':{'lips_smirk_right':{'driverAttr':'ty'},
                         }},
    'r_frownBig_anim':{'control':'r_frownBig_anim',
           'wiringDict':{'lips_frownBig_right':{'driverAttr':'ty'},
                         }},    
    
    
    'noseFlare_anim':{'control':'noseFlare_anim',
           'wiringDict':{'nose_flare':{'driverAttr':'ty'}}},    
    
    #Hide stuff .... ------------------------------------------------------------------
    'tongue_hide':{'control':'hide_tongue_anim',
           'wiringDict':{'tongue_hide':{'driverAttr':'-ty'}}},
    
    },
    'test':{
                      
    'inner_brow_left':{'control':'l_inner_brow_anim',
                       'wiringDict':{'brow_inr_up_left':{'driverAttr':'ty'},
                                     'brow_inr_dn_left':{'driverAttr':'-ty'},
                                     'brow_squeeze_left':{'driverAttr':'-tx'}}},                             
    'mid_brow_left':{'control':'l_mid_brow_anim',
                     'wiringDict':{'brow_mid_up_left':{'driverAttr':'ty'},
                                   'brow_mid_dn_left':{'driverAttr':'-ty'}}}, 
    'outer_brow_left':{'control':'l_outer_brow_anim',
                       'wiringDict':{'brow_outr_up_left':{'driverAttr':'ty'},
                                     'brow_outr_dn_left':{'driverAttr':'-ty'}}},
    'inner_brow_right':{'control':'r_inner_brow_anim',
                       'wiringDict':{'brow_inr_up_right':{'driverAttr':'ty'},
                                     'brow_inr_dn_right':{'driverAttr':'-ty'},
                                     'brow_squeeze_right':{'driverAttr':'-tx'}}},                             
    'mid_brow_right':{'control':'r_mid_brow_anim',
                     'wiringDict':{'brow_mid_up_right':{'driverAttr':'ty'},
                                   'brow_mid_dn_right':{'driverAttr':'-ty'}}}, 
    'outer_brow_right':{'control':'r_outer_brow_anim',
                       'wiringDict':{'brow_outr_up_right':{'driverAttr':'ty'},
                                     'brow_outr_dn_right':{'driverAttr':'-ty'}}}, 
    
    'eyeSqueeze_left':{'control':'l_eyeSqueeze_anim',
                       'wiringDict':{'eyeSqueeze_up_left':{'driverAttr':'ty'},
                                     'eyeSqueeze_dn_left':{'driverAttr':'-ty'}}}, 
    'eyeSqueeze_right':{'control':'r_eyeSqueeze_anim',
                       'wiringDict':{'eyeSqueeze_up_right':{'driverAttr':'ty'},
                                     'eyeSqueeze_dn_right':{'driverAttr':'-ty'}}}, 
    
    
    'cheek_left':{'control':'l_cheek_anim',
                  'wiringDict':{'cheek_up_left':{'driverAttr':'ty'},
                                'cheek_dn_left':{'driverAttr':'-ty'},
                                'cheek_blow_left':{'driverAttr':'tx'},
                                'cheek_suck_left':{'driverAttr':'-tx'}}},
    'cheek_right':{'control':'r_cheek_anim',
                  'wiringDict':{'cheek_up_right':{'driverAttr':'ty'},
                                'cheek_dn_right':{'driverAttr':'-ty'},
                                'cheek_blow_right':{'driverAttr':'tx'},
                                'cheek_suck_right':{'driverAttr':'-tx'}}},   
    
    'nose_left':{'control':'l_nose_anim',
                 'wiringDict':{'nose_in_left':{'driverAttr':'-tx'},
                               'nose_out_left':{'driverAttr':'tx'},
                               'nose_sneer_up_left':{'driverAttr':'ty'},
                               'nose_sneer_dn_left':{'driverAttr':'-ty'}},
                 'simpleArgs':['{0}.nose_seal_up_cntr_left = {0}.nose_sneer_up_left * {0}.seal_center',
                               '{0}.nose_seal_up_outr_left = {0}.nose_sneer_up_left * {0}.seal_left'
                               ]},
    'nose_right':{'control':'r_nose_anim',
                 'wiringDict':{'nose_in_right':{'driverAttr':'-tx'},
                               'nose_out_right':{'driverAttr':'tx'},
                               'nose_sneer_up_right':{'driverAttr':'ty'},
                               'nose_sneer_dn_right':{'driverAttr':'-ty'}},
                 'simpleArgs':['{0}.nose_seal_up_cntr_right = {0}.nose_sneer_up_right * {0}.seal_center',
                               '{0}.nose_seal_up_outr_right = {0}.nose_sneer_up_right * {0}.seal_right',
                               ]},
    
    'lipCorner_left':{'control':'l_lipCorner_anim',
                      'wiringDict':{'lips_purse_left':{'driverAttr':'purse'},
                                    'lips_out_left':{'driverAttr':'out'},
                                    'lips_twistUp_left':{'driverAttr':'twist'},
                                    'lips_twistDn_left':{'driverAttr':'-twist'},
                                    'lips_smile_left':{'driverAttr':'ty'},
                                    'lips_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_left':{'driverAttr':'-tx'},
                                    'lips_wide_left':{'driverAttr':'tx'}}},
    'lipCorner_right':{'control':'r_lipCorner_anim',
                      'wiringDict':{'lips_purse_right':{'driverAttr':'purse'},
                                    'lips_out_right':{'driverAttr':'out'},
                                    'lips_twistUp_right':{'driverAttr':'twist'},
                                    'lips_twistDn_right':{'driverAttr':'-twist'},
                                    'lips_smile_right':{'driverAttr':'ty'},
                                    'lips_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lips_narrow_right':{'driverAttr':'-tx'},
                                    'lips_wide_right':{'driverAttr':'tx'}}},}}
                 

def stacheSetup():
    _muzzle = 'muzzle_anim'
    _d = {'L_stache_root_anim':'L_uprLip_direct_anim',
          'R_stache_root_anim':'R_uprLip_direct_anim'}
    
    
    mMuzzle = cgmMeta.asMeta(_muzzle)
    
    for o,t in _d.iteritems():
        mObj = cgmMeta.asMeta(o)
        mTarget = cgmMeta.asMeta(t)
        
        mDynGroup = mObj.dynParentGroup
        
        for i in xrange(2):
            if not i:
                _name = "{0}_{1}_trackLoc".format(mObj.p_nameBase,mTarget.p_nameBase)
                _alias = 'trackLip'
            else:
                _name = "{0}_{1}_muzzleLoc".format(mObj.p_nameBase,mTarget.p_nameBase)
                _alias = 'trackLipMuzzle'
                
            mLoc = mObj.doLoc(fastMode=True)
            mLoc.rename(_name)
            mLoc.p_parent = mTarget
            mLoc.doStore('cgmAlias', _alias)
             
            if i:
                mc.orientConstraint(mMuzzle.mNode, mLoc.mNode, maintainOffset = True)
                
            mDynGroup.addDynParent(mLoc.mNode)
            
        mDynGroup.rebuild()
            
            
            #mObj.doCreateAt('joint', connectAs = 'sdkGroup', setClass = 'cgmObject')
            #            mSDK.p_parent = mObj.p_parent    
    

def swordSetup():
    _l = [['L_wrist_direct_anim','sword_l_hand','handR'],
          ['R_wrist_direct_anim','sword_r_hand','handL'],
          ['L_snapSheath_anim','sword_sheath','sheathL']]
    
    mSword = cgmMeta.asMeta('sword_anim')
    mDynGroup = mSword.dynParentGroup

    for s in _l:
        mObj = cgmMeta.asMeta(s[0])
        mTarget = cgmMeta.asMeta(s[1])
        
        
        mDriver = mDynGroup.addDynParent(mTarget.mNode)
        mDriver.doSnapTo(mTarget)
        mSword.doSnapTo(mTarget)
        
        mTarget.p_parent = mObj
        mTarget.v=False
        mTarget.doStore('cgmAlias', s[2])

            
        mDynGroup.rebuild()
    mSword.resetAttrs()

