"""
------------------------------------------
shared_data: cgm.core.lib.shared_data
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------
"""


#>>> Positional data
#===================================================================
_d_rotateOrder_to_index = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
_d_rotateOrder_from_index = {0: 'xyz', 1: 'yzx', 2: 'zxy', 3: 'xzy', 4: 'yxz', 5: 'zyx', 6: 'none'}

_d_pivotArgs = {'rp':['rp','r','rotate','rotatePivot','pivot'],'sp':['scale','s','scalePivot'],'boundingBox':['bb','bbCenter'],'closestPoint':['cpos','closest','closestPoint']}
_d_spaceArgs = {'object':['os','objectSpace','local','o'],'world':['w','worldSpace','ws']}

    