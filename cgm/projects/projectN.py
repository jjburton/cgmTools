import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from .cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from .cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
from .cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST
from .cgm.core import cgm_General as cgmGEN

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
    
    
    
    for k,t in list(_d.items()):
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


'ara':{
    
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
    

    #Brow...-----------------------------------------------
    'l_brow_anim':{'control':'l_brow_anim',
                   'wiringDict':{'brow_arcUp_left':{'driverAttr':'ty'},
                                 'brow_arcDn_left':{'driverAttr':'-ty'},
                                 'brow_furrow_left':{'driverAttr':'-tx'}}},
    'r_brow_anim':{'control':'r_brow_anim',
                   'wiringDict':{'brow_arcUp_right':{'driverAttr':'ty'},
                                 'brow_arcDn_right':{'driverAttr':'-ty'},
                                 'brow_furrow_right':{'driverAttr':'-tx'}}},        

    #Lid... --------------------------------------------
    'L_lidArcUpr_anim':{'control':'L_lidArcUpr_anim',
           'wiringDict':{'lid_arcUprUp_left':{'driverAttr':'ty'},
                         'lid_arcUprDn_left':{'driverAttr':'-ty'},
                         }},
    'L_lidArcLwr_anim':{'control':'L_lidArcLwr_anim',
           'wiringDict':{'lid_arcLwrUp_left':{'driverAttr':'ty'},
                         'lid_arcLwrDn_left':{'driverAttr':'-ty'},
                         }},    
    
    'L_lidUpr_anim':{'control':'L_lidUpr_anim',
           'wiringDict':{'lid_uprUp_left':{'driverAttr':'ty'},
                         'lid_uprDn_left':{'driverAttr':'-ty'},
                         }},
    'L_lidLwr_anim':{'control':'L_lidLwr_anim',
           'wiringDict':{'lid_lwrUp_left':{'driverAttr':'ty'},
                         'lid_lwrDn_left':{'driverAttr':'-ty'},
                         }},


    'R_lidArcUpr_anim':{'control':'R_lidArcUpr_anim',
           'wiringDict':{'lid_arcUprUp_right':{'driverAttr':'ty'},
                         'lid_arcUprDn_right':{'driverAttr':'-ty'},
                         }},
    'R_lidArcLwr_anim':{'control':'R_lidArcLwr_anim',
           'wiringDict':{'lid_arcLwrUp_right':{'driverAttr':'ty'},
                         'lid_arcLwrDn_right':{'driverAttr':'-ty'},
                         }},    
    
    'R_lidUpr_anim':{'control':'R_lidUpr_anim',
           'wiringDict':{'lid_uprUp_right':{'driverAttr':'ty'},
                         'lid_uprDn_right':{'driverAttr':'-ty'},
                         }},
    'R_lidLwr_anim':{'control':'R_lidLwr_anim',
           'wiringDict':{'lid_lwrUp_right':{'driverAttr':'ty'},
                         'lid_lwrDn_right':{'driverAttr':'-ty'},
                         }},
    
    #Pupil... --------------------------------------------
    'L_pupil_anim':{'control':'L_pupil_anim',
           'wiringDict':{'pupil_small_left':{'driverAttr':'ty'},
                         }},
    'R_pupil_anim':{'control':'R_pupil_anim',
           'wiringDict':{'pupil_small_right':{'driverAttr':'ty'},
                         }},
    
    #Cheek... --------------------------------------------
    'L_cheek_anim':{'control':'L_cheek_anim',
           'wiringDict':{'cheek_out_left':{'driverAttr':'ty'},
                         }},
    'R_cheek_anim':{'control':'R_cheek_anim',
           'wiringDict':{'cheek_out_right':{'driverAttr':'ty'},
                         }},    
    
    
    #Nose... --------------------------------------------
    'nose':{'control':'nose_anim',
           'wiringDict':{'nose_flare':{'driverAttr':'ty'},
                         }},
    
    #Tongue... --------------------------------------------
    'tongue':{'control':'tongue_anim',
           'wiringDict':{'tongue_fix':{'driverAttr':'ty'},
                         }},
    

    },

'urd':{
    
    #Eye... -----------------------------------------------
    'L_eye':{'control':'L_eyeCon_anim',
           'wiringDict':{'eye_up_left':{'driverAttr':'ty'},
                         'eye_dn_left':{'driverAttr':'-ty'},
                         'eye_right_left':{'driverAttr':'tx'},
                         'eye_left_left':{'driverAttr':'-tx'},
                         }},
    
    'R_eye':{'control':'R_eyeCon_anim',
           'wiringDict':{'eye_up_right':{'driverAttr':'ty'},
                         'eye_dn_right':{'driverAttr':'-ty'},
                         'eye_right_right':{'driverAttr':'tx'},
                         'eye_left_right':{'driverAttr':'-tx'},
                         }},
    

    #Brow...-----------------------------------------------
    'browUp':{'control':'browUpCon_anim',
              'wiringDict':{'brow_up_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'brow_up_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'}}},
    
    'browAngry':{'control':'browAngryCon_anim',
              'wiringDict':{'brow_angry_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'brow_angry_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'}}},    
              
    'browSad':{'control':'browSadCon_anim',
              'wiringDict':{'brow_sad_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'brow_sad_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'}}},

    'R_arcUp':{'control':'R_browArcCon_anim',
           'wiringDict':{'brow_arcUp_right':{'driverAttr':'ty'},
                         'brow_arcDn_right':{'driverAttr':'-ty'}
                         }},
    'L_arcUp':{'control':'L_browArcCon_anim',
           'wiringDict':{'brow_arcUp_left':{'driverAttr':'ty'},
                         'brow_arcDn_left':{'driverAttr':'-ty'}
                         }},

    #Lid... --------------------------------------------
    'r_lid':{'control':'R_lidCon_anim',
           'wiringDict':{'lid_up_right':{'driverAttr':'ty'},
                         'lid_dn_right':{'driverAttr':'-ty'},
                         }},
    'r_eyeHide':{'control':'R_eyeHideCon_anim',
           'wiringDict':{'eye_hide_right':{'driverAttr':'ty'},
                         }},    
    
    'l_lid':{'control':'L_lidCon_anim',
           'wiringDict':{'lid_up_left':{'driverAttr':'ty'},
                         'lid_dn_left':{'driverAttr':'-ty'},
                         }},
    'l_eyeHide':{'control':'L_eyeHideCon_anim',
           'wiringDict':{'eye_hide_left':{'driverAttr':'ty'},
                         }},    

    
    #Pupil... --------------------------------------------
    'L_pupil':{'control':'L_pupilCon_anim',
           'wiringDict':{'pupil_big_left':{'driverAttr':'ty'},
                         'pupil_small_left':{'driverAttr':'-ty'}
                         }},
    'R_pupil':{'control':'R_pupilCon_anim',
           'wiringDict':{'pupil_big_right':{'driverAttr':'ty'},
                         'pupil_small_right':{'driverAttr':'-ty'}
                         }},
    
    #Cheek... --------------------------------------------
    'L_cheek_anim':{'control':'L_cheekPuffCon_anim',
           'wiringDict':{'cheek_out_left':{'driverAttr':'ty'},
                         }},
    'R_cheek_anim':{'control':'R_cheekPuffCon_anim',
           'wiringDict':{'cheek_out_right':{'driverAttr':'ty'},
                         }},    
    
    
    #Tongue... --------------------------------------------
    'tongueTeeth':{'control':'teethTongueCon_anim',
           'wiringDict':{'tongue_teethPose':{'driverAttr':'ty'},
                         }},    
    'tongueFix':{'control':'tongueHideCon_anim',
           'wiringDict':{'tongue_hide':{'driverAttr':'ty'},
                         }},    
    
    #Lips...-----------------------------------------------
    'uprLip':{'control':'uprLipCon_anim',
           'wiringDict':{'lip_uprSneer_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_uprSneer_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    'lwrLip':{'control':'lwrLipCon_anim',
           'wiringDict':{'lip_lwrSneer_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                         'lip_lwrSneer_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},
                         }},    
    
    'lipClose':{'control':'lipSealCon_anim',
           'wiringDict':{'lip_sealRaw_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_sealRaw_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         },
           'simpleArgs':['{0}.lip_seal_left = {0}.lip_sealRaw_left - {0}.cheek_out_left',
                         '{0}.lip_seal_right = {0}.lip_sealRaw_right - {0}.cheek_out_right']},

    'mouth':{'control':'mouthCon_anim',
           'wiringDict':{'lip_up_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_up_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_dn_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                         'lip_dn_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'}},
           },    
    
    
    
    
    'lipCorner_left':{'control':'L_lipCornerCon_anim',
                      'wiringDict':{'lip_smileRaw_left':{'driverAttr':'ty'},
                                    'lip_frownRaw_left':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_left':{'driverAttr':'-tx'},
                                    'lip_wide_left':{'driverAttr':'tx'}},
                      'simpleArgs':['{0}.lip_smile_left = {0}.lip_smileRaw_left - {0}.jaw_smileOpen_left',
                                    '{0}.lip_frown_left = {0}.lip_frownRaw_left - {0}.jaw_frownOpen_left']
                      },
    'lipCorner_right':{'control':'R_lipCornerCon_anim',
                      'wiringDict':{'lip_smileRaw_right':{'driverAttr':'ty'},
                                    'lip_frownRaw_right':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_right':{'driverAttr':'-tx'},
                                    'lip_wide_right':{'driverAttr':'tx'}},
                      'simpleArgs':['{0}.lip_smile_right = {0}.lip_smileRaw_right - {0}.jaw_smileOpen_right',
                                    '{0}.lip_frown_right = {0}.lip_frownRaw_right - {0}.jaw_frownOpen_right']                      
                      },
    
    'jawOpenSmile':{'control':'jawCon_anim',
                    'wiringDict':{'jaw_openUse':{'driverAttr':'ty'},
                                  'jaw_close':{'driverAttr':'-ty'}},
                    'simpleArgs':['{0}.jaw_open_left = {0}.jaw_openUse - {0}.jaw_frownOpen_left - {0}.jaw_smileOpen_left',
                                  '{0}.jaw_open_right = {0}.jaw_openUse - {0}.jaw_frownOpen_right - {0}.jaw_smileOpen_right',
                                  '{0}.jaw_frownOpen_left = {0}.jaw_openUse * {0}.lip_frownRaw_left',
                                  '{0}.jaw_frownOpen_right = {0}.jaw_openUse * {0}.lip_frownRaw_right',
                                  '{0}.jaw_smileOpen_left = {0}.jaw_openUse * {0}.lip_smileRaw_left',
                                  '{0}.jaw_smileOpen_right = {0}.jaw_openUse * {0}.lip_smileRaw_right',
                                  ]},    
    
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
'pip':{
    #Lid... --------------------------------------------
    'l_eyeArc':{'control':'L_eyeArcCon_anim',
           'wiringDict':{'lid_arcUp_left':{'driverAttr':'ty'},
                         'lid_arcDn_left':{'driverAttr':'-ty'},
                         }},
    'l_eyeBlink':{'control':'L_blinkCon_anim',
           'wiringDict':{'lid_blink_left':{'driverAttr':'-ty'},
                         }},
    
    'l_eyeSqueeze':{'control':'L_lidSqueezeCon_anim',
           'wiringDict':{'lid_squeeze_left':{'driverAttr':'ty'},
                         }},    
    'l_eyeSad':{'control':'L_eyeSadConCon_anim',
           'wiringDict':{'lid_sad_left':{'driverAttr':'ty'},
                         }},    
    'l_eyeAngry':{'control':'L_eyeAngryCon_anim',
           'wiringDict':{'lid_angry_left':{'driverAttr':'ty'},
                         }},
    
    'R_eyeArc':{'control':'R_eyeArcCon_anim',
           'wiringDict':{'lid_arcUp_right':{'driverAttr':'ty'},
                         'lid_arcDn_right':{'driverAttr':'-ty'},
                         }},
    'R_eyeBlink':{'control':'R_blinkCon_anim',
           'wiringDict':{'lid_blink_right':{'driverAttr':'-ty'},
                         }},
    
    'R_eyeSqueeze':{'control':'R_lidSqueezeCon_anim',
           'wiringDict':{'lid_squeeze_right':{'driverAttr':'ty'},
                         }},    
    'R_eyeSad':{'control':'R_eyeSadConCon_anim',
           'wiringDict':{'lid_sad_right':{'driverAttr':'ty'},
                         }},    
    'R_eyeAngry':{'control':'R_eyeAngryCon_anim',
           'wiringDict':{'lid_angry_right':{'driverAttr':'ty'},
                         }},    
    
    #Tail ------------------------------------------------------------------
    'tailEnd':{'control':'tailSpreadCon_anim',
                      'wiringDict':{'tail_narrow':{'driverAttr':'tx'},
                                    'tail_spread':{'driverAttr':'-tx'}}},        

    #Mouth... --------------------------------------------
    'lipClose':{'control':'lipSealCon_anim',
           'wiringDict':{'lip_seal_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_seal_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    
    'mouthOO':{'control':'mouth_ooCon_anim',
           'wiringDict':{'lip_ooo_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_ooo_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    'pout':{'control':'poutCon_anim',
           'wiringDict':{'lip_pout_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_pout_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    'inflate':{'control':'inflateCon_anim',
           'wiringDict':{'cheek_inflate_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'cheek_inflate_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},             

    'jaw':{'control':'jawCon_anim',
           'wiringDict':{'jaw_up':{'driverAttr':'ty'},
                         'jaw_open':{'driverAttr':'-ty'},
                         'jaw_side_left':{'driverAttr':'-tx'},
                         'jaw_side_right':{'driverAttr':'tx'}
                         }},
    

    'lipCorner_left':{'control':'L_lipCornerCon_anim',
                      'wiringDict':{'lip_smile_left':{'driverAttr':'ty'},
                                    'lip_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_left':{'driverAttr':'-tx'},
                                    'lip_wide_left':{'driverAttr':'tx'}}},
    
    'lipCorner_right':{'control':'R_lipCornerCon_anim',
                      'wiringDict':{'lip_smile_right':{'driverAttr':'ty'},
                                    'lip_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_right':{'driverAttr':'-tx'},
                                    'lip_wide_right':{'driverAttr':'tx'}}},    
    
    
    },
'cha1':{
    #Brow... --------------------------------------------
    'l_eyebrow':{'control':'l_browCon_anim',
           'wiringDict':{'brow_flat_left':{'driverAttr':'-ty'},
                         'brow_arcUp_left':{'driverAttr':'ty'},
                         'brow_angry_left':{'driverAttr':'-tx'},
                         }},
    'r_eyebrow':{'control':'r_browCon_anim',
           'wiringDict':{'brow_flat_right':{'driverAttr':'-ty'},
                         'brow_arcUp_right':{'driverAttr':'ty'},
                         'brow_angry_right':{'driverAttr':'-tx'},
                         }},    
    
    'l_browThick':{'control':'L_browThickConCon_anim',
           'wiringDict':{'brow_thick_left':{'driverAttr':'ty'},
                         }},
    'r_browThick':{'control':'R_browThickConCon_anim',
           'wiringDict':{'brow_thick_right':{'driverAttr':'ty'},
                         }},
    
    #Lid... --------------------------------------------
    'L_smileFix':{'control':'L_eyeSmileFixConCon_anim',
           'wiringDict':{'eye_fix_left':{'driverAttr':'ty'},
                         }},
    'l_eyeAngle':{'control':'L_eyeAngleCon_anim',
           'wiringDict':{'lid_eyeAngle_left':{'driverAttr':'ty'},
                         }},
    'l_eyeArc':{'control':'L_eyeArcCon_anim',
           'wiringDict':{'lid_arcUp_left':{'driverAttr':'ty'},
                         'lid_arcDn_left':{'driverAttr':'-ty'},
                         }},
    'l_eyeBlink':{'control':'L_blinkCon_anim',
           'wiringDict':{'lid_blink_left':{'driverAttr':'-ty'},
                         }},    
    'l_eyeRound':{'control':'L_roundIrisCon_anim',
           'wiringDict':{'eye_pupilRound_left':{'driverAttr':'ty'},
                         }},    
    'l_pupilUp':{'control':'L_pupilBottomUpFixConCon_anim',
           'wiringDict':{'eye_pupilBottom_left':{'driverAttr':'ty'},
                         }},    

    'R_smileFix':{'control':'R_eyeSmileFixConCon_anim',
           'wiringDict':{'eye_fix_right':{'driverAttr':'ty'},
                         }},
    'R_eyeAngle':{'control':'R_eyeAngleCon_anim',
           'wiringDict':{'lid_eyeAngle_right':{'driverAttr':'ty'},
                         }},
    'R_eyeArc':{'control':'R_eyeArcCon_anim',
           'wiringDict':{'lid_arcUp_right':{'driverAttr':'ty'},
                         'lid_arcDn_right':{'driverAttr':'-ty'},
                         }},
    'R_eyeBlink':{'control':'R_blinkCon_anim',
           'wiringDict':{'lid_blink_right':{'driverAttr':'-ty'},
                         }},  
    
    'R_eyeRound':{'control':'R_roundIrisCon_anim',
           'wiringDict':{'eye_pupilRound_right':{'driverAttr':'ty'},
                         }},        
    'R_pupilUp':{'control':'R_pupilBottomUpFixConCon_anim',
           'wiringDict':{'eye_pupilBottom_right':{'driverAttr':'ty'},
                         }},       
    
    
    
    
    #Mouth... --------------------------------------------
    'lipClose':{'control':'lipSealCon_anim',
           'wiringDict':{'lip_seal_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_seal_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    'catLip':{'control':'catLipCon_anim',
           'wiringDict':{'lip_cat_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_cat_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},    
    
    'smileBig':{'control':'smileBigCon_anim',
           'wiringDict':{'lip_smilePush_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_smilePush_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},        

    'jaw':{'control':'jawCon_anim',
           'wiringDict':{'mouth_up':{'driverAttr':'ty'},
                         'jaw_open':{'driverAttr':'-ty'},
                         }},
    
    'mouthOut':{'control':'mouthOutCon_anim',
           'wiringDict':{'mouth_out':{'driverAttr':'ty'},
                         }},    

    'lipCorner_left':{'control':'L_lipCornerCon_anim',
                      'wiringDict':{'lip_smile_left':{'driverAttr':'ty'},
                                    'lip_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_left':{'driverAttr':'-tx'},
                                    'lip_wide_left':{'driverAttr':'tx'}}},
    
    'lipCorner_right':{'control':'R_lipCornerCon_anim',
                      'wiringDict':{'lip_smile_right':{'driverAttr':'ty'},
                                    'lip_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_right':{'driverAttr':'-tx'},
                                    'lip_wide_right':{'driverAttr':'tx'}}},    
    
    #Teeth stuff .... ------------------------------------------------------------------
    'teethClose':{'control':'teethCloseCon_anim',
           'wiringDict':{'teeth_closeReg':{'driverAttr':'ty'},
                         }},    
    'teethCloseFlat':{'control':'teethFlatCloseCon_anim',
           'wiringDict':{'teeth_closeFlat':{'driverAttr':'ty'},
                         }},
    
    'teethUprFlat':{'control':'teethUprFlatCon_anim',
           'wiringDict':{'teeth_flatUpr':{'driverAttr':'ty'},
                         }},
    'teethLwrFlat':{'control':'teethLwFlatCon_anim',
           'wiringDict':{'teeth_flatLwr':{'driverAttr':'ty'},
                         }},        
 
    #Hide stuff .... ------------------------------------------------------------------
    'teeth_hide':{'control':'teethHideCon_anim',
           'wiringDict':{'teeth_hide':{'driverAttr':'ty'}}},
    
    'tongue_hide':{'control':'tongueHideCon_anim',
           'wiringDict':{'tongue_hide':{'driverAttr':'ty'}}},
    
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
'och':{
    #Pupil... --------------------------------------------
    'L_ear':{'control':'L_earShapeCon_anim',
                    'wiringDict':{'ear_thickBase_left':{'driverAttr':'-tx'},
                                  'ear_cup_left':{'driverAttr':'ty'}
                     }},
    'R_ear':{'control':'R_earShapeCon_anim',
                    'wiringDict':{'ear_thickBase_right':{'driverAttr':'-tx'},
                                  'ear_cup_right':{'driverAttr':'ty'}
                     }},    
    
    #Brow... --------------------------------------------
    'l_eyebrow':{'control':'L_browCon_anim',
           'wiringDict':{'brow_furrow_left':{'driverAttr':'-tx'},
                         'brow_up_left':{'driverAttr':'ty'},
                         'brow_down_left':{'driverAttr':'-ty'},
                         }},
    'r_eyebrow':{'control':'R_browCon_anim',
           'wiringDict':{'brow_furrow_right':{'driverAttr':'-tx'},
                         'brow_up_right':{'driverAttr':'ty'},
                         'brow_down_right':{'driverAttr':'-ty'},
                         }},    
    
    'browMid':{'control':'browMidCon_anim',
           'wiringDict':{'browMid_squeeze':{'driverAttr':'-tx'},
                         'browMid_up':{'driverAttr':'ty'},
                         'browMid_down':{'driverAttr':'-ty'},
                         }},    
    
    #Lid... --------------------------------------------
    'L_blinkUpr':{'control':'L_blinkUprCon_anim',
           'wiringDict':{'lid_upr_left':{'driverAttr':'-ty'},
                         }},
    'L_blinkLwr':{'control':'L_blinkLwrCon_anim',
           'wiringDict':{'lid_lwr_left':{'driverAttr':'ty'},
                         }},

    'R_blinkUpr':{'control':'R_blinkUprCon_anim',
           'wiringDict':{'lid_upr_right':{'driverAttr':'-ty'},
                         }},
    'R_blinkLwr':{'control':'R_blinkLwrCon_anim',
           'wiringDict':{'lid_lwr_right':{'driverAttr':'ty'},
                         }},
    
    #Pupil... --------------------------------------------
    'L_pupilShape':{'control':'L_pupilShapeCon_anim',
                    'wiringDict':{'pupil_horizontal_left':{'driverAttr':'-tx'},
                                  'pupil_vertical_left':{'driverAttr':'ty'}
                     }},
    'L_pupilAngle':{'control':'L_pupilAngleCon_anim',
           'wiringDict':{'pupil_angle_left':{'driverAttr':'ty'},
                         }},    
    
    
    'R_pupilShape':{'control':'R_pupilShapeCon_anim',
                    'wiringDict':{'pupil_horizontal_right':{'driverAttr':'-tx'},
                                  'pupil_vertical_right':{'driverAttr':'ty'}
                     }},
    'R_pupilAngle':{'control':'R_pupilAngleCon_anim',
           'wiringDict':{'pupil_angle_right':{'driverAttr':'ty'},
                         }},        
    
    
    #Mouth... --------------------------------------------
    'lipOut':{'control':'lipOutCon_anim',
                'wiringDict':{'lipOut_upr':{'driverAttr':'ty','driverAttr2':'-tx','mode':'cornerBlend'},
                              'lipOut_lwr':{'driverAttr':'-ty','driverAttr2':'-tx','mode':'cornerBlend'},
                              }},
    'lipClose':{'control':'lipSealCon_anim',
           'wiringDict':{'lip_seal_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_seal_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    'lipSealCenter':{'control':'centerSealCon_anim',
           'wiringDict':{'lip_sealCenter':{'driverAttr':'ty'}}},
    
    'cheekPuff':{'control':'cheekPuffCon_anim',
           'wiringDict':{'cheek_puff_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'cheek_puff_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    'cheekPuffOuter':{'control':'cheekOutrPuffCon_anim',
           'wiringDict':{'cheek_outer_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'cheek_outer_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},    
    
    'overMuzzle':{'control':'overMuzzleCon_anim',
           'wiringDict':{'uprMuzzle_tweak_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'uprMuzzle_tweak_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    
    'lineHide':{'control':'lineHideCon_anim',
           'wiringDict':{'hide_line':{'driverAttr':'ty'},
                         }},
    
    
    'lipCorner_left':{'control':'L_lipCornerCon_anim',
                      'wiringDict':{'lip_smile_left':{'driverAttr':'ty'},
                                    'lip_frown_left':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_left':{'driverAttr':'-tx'},
                                    'lip_wide_left':{'driverAttr':'tx'}}},
    
    'lipCorner_right':{'control':'R_lipCornerCon_anim',
                      'wiringDict':{'lip_smile_right':{'driverAttr':'ty'},
                                    'lip_frown_right':{'driverAttr':'-ty'},                                                    
                                    'lip_narrow_right':{'driverAttr':'-tx'},
                                    'lip_wide_right':{'driverAttr':'tx'}}},
    
    'lipUpr':{'control':'uprLipCon_anim',
              'wiringDict':{'lip_uprUp_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'lip_uprUp_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'lip_uprDown_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},
                            'lip_uprDown_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},                                    
                            }},
    'lipLwr':{'control':'lwrLipCon_anim',
              'wiringDict':{'lip_lwrUp_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'lip_lwrUp_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                            'lip_lwrDown_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},
                            'lip_lwrDown_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},                                    
                            }},    
    
    
    'sneerUpr':{'control':'sneerUprCon_anim',
           'wiringDict':{'lip_uprSneer_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_uprSneer_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    'sneerLwr':{'control':'sneerLwrCon_anim',
           'wiringDict':{'lip_lwrSneer_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'lip_lwrSneer_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},    
    
    
    'noseSniff':{'control':'noseSniffCon_anim',
           'wiringDict':{'nose_sniff':{'driverAttr':'ty'},
                         }},    
    #Mouth... --------------------------------------------
    'jaw':{'control':'jawCon_anim',
           'wiringDict':{'jaw_close':{'driverAttr':'ty'},
                         'jaw_open':{'driverAttr':'-ty'},
                         'jaw_left':{'driverAttr':'tx'},
                         'jaw_right':{'driverAttr':'-tx'},
                         }},
    
    'jawFwdBack':{'control':'jawFwdBackCon_anim',
           'wiringDict':{'jaw_forward':{'driverAttr':'ty'},
                         'jaw_back':{'driverAttr':'-ty'},
                         }},        
    
    'mouth':{'control':'mouthMoveCon_anim',
           'wiringDict':{'mouth_up':{'driverAttr':'ty'},
                         'mouth_down':{'driverAttr':'-ty'},
                         'mouth_left':{'driverAttr':'tx'},
                         'mouth_right':{'driverAttr':'-tx'},
                         }},
    
    #Tongue... --------------------------------------------
    'tongue_down':{'control':'tongueDnCon_anim',
           'wiringDict':{'tongue_down':{'driverAttr':'-ty'}}},
    
    'tongue':{'control':'tongueCon_anim',
           'wiringDict':{'tongue_out':{'driverAttr':'ty'},
                         'tongue_left':{'driverAttr':'tx'},
                         'tongue_right':{'driverAttr':'-tx'},
                         }},    
    'tongue_hide':{'control':'tongueHideCon_anim',
           'wiringDict':{'tongue_hide':{'driverAttr':'-ty'}}},
    
    #Teeth stuff .... ------------------------------------------------------------------
    'teethHide':{'control':'teethHideCon_anim',
                 'wiringDict':{'teeth_hideUpr':{'driverAttr':'ty','driverAttr2':'-tx','mode':'cornerBlend'},
                               'teeth_hideLwr':{'driverAttr':'-ty','driverAttr2':'-tx','mode':'cornerBlend'},
                               }},    
    'teethWide':{'control':'teethWideCon_anim',
           'wiringDict':{'teeth_wide_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'teeth_wide_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    'teethFangUp':{'control':'fangUpCon_anim',
           'wiringDict':{'teeth_fangUp_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                         'teeth_fangUp_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                         }},
    
    'teethNice':{'control':'teethNiceCon_anim',
           'wiringDict':{'teeth_nice':{'driverAttr':'ty'}}},
    
    'teethBack':{'control':'teethBackCon_anim',
           'wiringDict':{'teeth_back':{'driverAttr':'ty'}}},
    
    'teethClose':{'control':'teethCloseCon_anim',
           'wiringDict':{'teeth_close':{'driverAttr':'ty'},
                         }},    
    'uprGum':{'control':'uprGumCon_anim',
           'wiringDict':{'teeth_uprGum':{'driverAttr':'ty'},
                         }},    
    
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
                                    'lips_wide_right':{'driverAttr':'tx'}}},}

}
                 

def stacheSetup():
    _muzzle = 'muzzle_anim'
    _d = {'L_stache_root_anim':'L_uprLip_direct_anim',
          'R_stache_root_anim':'R_uprLip_direct_anim'}
    
    
    mMuzzle = cgmMeta.asMeta(_muzzle)
    
    for o,t in list(_d.items()):
        mObj = cgmMeta.asMeta(o)
        mTarget = cgmMeta.asMeta(t)
        
        mDynGroup = mObj.dynParentGroup
        
        for i in range(2):
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



def simpleLipHandleTrack(top = 'muzzle_anim', lwr = 'lip_anim'):
    _muzzle = top
    _lip = lwr
    _d = ['L_lip_anim','R_lip_anim']
    
    mMuzzle = cgmMeta.asMeta(_muzzle)
    mLip = cgmMeta.asMeta(_lip)
    
    for o in _d:
        mObj = cgmMeta.asMeta(o)        
        mDynGroup = mObj.dynParentGroup

        _name = "{0}_{1}_trackLoc".format(mObj.p_nameBase,mObj.p_nameBase)
        _alias = 'trackLip'

                
        mLoc = mObj.doLoc(fastMode=True)
        mLoc.rename(_name)
        mLoc.p_parent = mMuzzle
        mLoc.doStore('cgmAlias', _alias)
         
        mc.pointConstraint([mMuzzle.mNode, mLip.mNode], mLoc.mNode, maintainOffset = True)
            
        mDynGroup.addDynParent(mLoc.mNode)
            
        mDynGroup.rebuild()
        
        
        
        
d_wiring = {'R_lip_smile': '|cha_faceBuffer.lip_smile_right', 'R_lip_narrow': '|cha_faceBuffer.lip_narrow_right', 'R_lip_smileBig': '|cha_faceBuffer.lip_smilePush_right', 'L_lid_happyBlink': '|cha_faceBuffer.lid_arcUp_left', 'teeth_lwrFlat': '|cha_faceBuffer.teeth_flatLwr', 'L_lip_wide': '|cha_faceBuffer.lip_wide_left', 'R_lid_blink': '|cha_faceBuffer.lid_blink_right', 'L_lid_blink': '|cha_faceBuffer.lid_blink_left', 'R_lip_seal': '|cha_faceBuffer.lip_seal_right', 'L_brow_anger': '|cha_faceBuffer.brow_angry_left', 'mouth_up': '|cha_faceBuffer.mouth_up', 'jaw_open': '|cha_faceBuffer.jaw_open', 'L_brow_thicken': '|cha_faceBuffer.brow_thick_left', 'teeth_hide': '|cha_faceBuffer.teeth_hide', 'R_brow_flat': '|cha_faceBuffer.brow_flat_right', 'tongueHide': '|cha_faceBuffer.tongue_hide', 'R_lip_wide': '|cha_faceBuffer.lip_wide_right', 'L_lid_downBlink': '|cha_faceBuffer.lid_arcDn_left', 'L_brow_arcUp': '|cha_faceBuffer.brow_arcUp_left', 'R_lip_cat': '|cha_faceBuffer.lip_cat_right', 'R_lid_downBlink': '|cha_faceBuffer.lid_arcDn_right', 'R_eye_mouthFix': '|cha_faceBuffer.eye_fix_right', 'L_lip_smile': '|cha_faceBuffer.lip_smile_left', 'R_brow_thicken': '|cha_faceBuffer.brow_thick_right', 'R_brow_arcUp': '|cha_faceBuffer.brow_arcUp_right', 'L_lip_narrow': '|cha_faceBuffer.lip_narrow_left', 'L_eyeRound': '|cha_faceBuffer.eye_pupilRound_left', 'L_brow_flat': '|cha_faceBuffer.brow_flat_left', 'teeth_flatSeal': '|cha_faceBuffer.teeth_closeFlat', 'L_lip_seal': '|cha_faceBuffer.lip_seal_left', 'teeth_close': '|cha_faceBuffer.teeth_closeReg', 'mouth_out': '|cha_faceBuffer.mouth_out', 'R_eyeRound': '|cha_faceBuffer.eye_pupilRound_right', 'R_lip_frown': '|cha_faceBuffer.lip_frown_right', 'L_eye_mouthFix': '|cha_faceBuffer.eye_fix_left', 'L_lip_smileBig': '|cha_faceBuffer.lip_smilePush_left', 'R_brow_anger': '|cha_faceBuffer.brow_angry_right', 'teeth_uprFlat': '|cha_faceBuffer.teeth_flatUpr', 'L_lip_frown': '|cha_faceBuffer.lip_frown_left', 'L_lip_cat': '|cha_faceBuffer.lip_cat_left'} # 




d_cha = {'tail_settings_anim':{'tail_rigRibbon_segScale':0,'visRoot':False},
         'head_root_anim':{'scaleSpace':'cog','orientTo':'cog'},
         'head_settings_anim':{'visRoot':True},
         
         'L_UPR_whisker_root_anim':{'scaleSpace':'head_root'},
         'L_LWR_whisker_root_anim':{'scaleSpace':'head_root'},
         'L_UPR_whisker_settings_anim':{'visRoot':False},
         'L_LWR_whisker_settings_anim':{'visRoot':False},         
         
         'L_ear_root_anim':{'scaleSpace':'head_root'},
         'L_ear_settings_anim':{'visRoot':False},         
         'L_arm_root_anim':{'scaleSpace':'cog'},
         'L_leg_root_anim':{'scaleSpace':'cog'},
         
         'L_arm_settings_anim':{'shoulder_seg_0_factor_0':.6,
                                'shoulder_seg_0_factor_1':.6,
                                'elbow_seg_1_factor_0':0,
                                'elbow_seg_1_factor_1':0,
                                'visRoot':False},
         'L_leg_settings_anim':{'hip_seg_0_factor_0':.6,
                                'hip_seg_0_factor_1':.6,
                                'knee_seg_1_factor_0':0,
                                'knee_seg_1_factor_1':0,
                                'visRoot':False},
         
         'R_UPR_whisker_root_anim':{'scaleSpace':'head_root'},
         'R_LWR_whisker_root_anim':{'scaleSpace':'head_root'},
         'whisker_settings_anim':{'visRoot':False},
         'R_LWR_whisker_settings_anim':{'visRoot':False},    
         
         'R_ear_root_anim':{'scaleSpace':'head_root'},
         'R_ear_settings_anim':{'visRoot':False},                  
         'R_arm_root_anim':{'scaleSpace':'cog'},
         'R_leg_root_anim':{'scaleSpace':'cog'},
         
         'R_arm_settings_anim':{'shoulder_seg_0_factor_0':.6,
                                'shoulder_seg_0_factor_1':.6,
                                'elbow_seg_1_factor_0':0,
                                'elbow_seg_1_factor_1':0,
                                'visRoot':False},
         'R_leg_settings_anim':{'hip_seg_0_factor_0':.6,
                                'hip_seg_0_factor_1':.6,
                                'knee_seg_1_factor_0':0,
                                'knee_seg_1_factor_1':0,
                                'visRoot':False},              

              }

d_pip = {'tail_settings_anim':{'FKIK':0,'visRoot':1},
         'R_fin_1_settings_anim':{'FKIK':0},
         'R_fin_2_settings_anim':{'FKIK':0},
         'L_fin_1_settings_anim':{'FKIK':0},
         'L_fin_2_settings_anim':{'FKIK':0},
         'tail_root_anim':{'scaleSpace':'cog'},
         'headRidge_1_settings_anim':{'FKIK':0},
         'headRidge_2_settings_anim':{'FKIK':0},
         'headRidge_3_settings_anim':{'FKIK':0},            
              }


d_och = {'tail_settings_anim':{'tail_rigRibbon_segScale':0,'visRoot':False},
         'head_root_anim':{'orientTo':'cog',
                           'scaleSpace':'cog'},
         'head_settings_anim':{'visRoot':True},
             
         'L_eyeOrb_rig_anim':{'visDirect':1},
         
         'L_ear_root_anim':{'scaleSpace':'head_root'},
         'L_ear_settings_anim':{'visRoot':False, 'FKIK':0},         
         'L_arm_root_anim':{'scaleSpace':'cog'},
         'L_leg_root_anim':{'scaleSpace':'cog'},
         'tail_root_anim':{'scaleSpace':'cog'},
         'scarfKnot_anim':{'scaleSpace':'cog'},
         'FRNT_scarf_root_anim':{'scaleSpace':'cog'},
         'FRNT_scarf_settings_anim':{'FKIK':0},
         
         'L_arm_settings_anim':{'shoulder_seg_0_factor_0':.6,
                                'shoulder_seg_0_factor_1':.6,
                                'elbow_seg_1_factor_0':0,
                                'elbow_seg_1_factor_1':0,
                                'visRoot':False},
         'L_leg_settings_anim':{'hip_seg_0_factor_0':.6,
                                'hip_seg_0_factor_1':.6,
                                'knee_seg_1_factor_0':0,
                                'knee_seg_1_factor_1':0,
                                'visRoot':False},
         

         'R_eyeOrb_rig_anim':{'visDirect':1},
         
         'R_ear_root_anim':{'scaleSpace':'head_root'},
         'R_ear_settings_anim':{'visRoot':False, 'FKIK':0},                  
         'R_arm_root_anim':{'scaleSpace':'cog'},
         'R_leg_root_anim':{'scaleSpace':'cog'},
         
         'R_arm_settings_anim':{'shoulder_seg_0_factor_0':.6,
                                'shoulder_seg_0_factor_1':.6,
                                'elbow_seg_1_factor_0':0,
                                'elbow_seg_1_factor_1':0,
                                'visRoot':False},
         'R_leg_settings_anim':{'hip_seg_0_factor_0':.6,
                                'hip_seg_0_factor_1':.6,
                                'knee_seg_1_factor_0':0,
                                'knee_seg_1_factor_1':0,
                                'visRoot':False},              

              }