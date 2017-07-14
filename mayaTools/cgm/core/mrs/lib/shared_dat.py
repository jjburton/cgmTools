"""
------------------------------------------
shared_dat: cgm.core.mrs.lib.shared_dat
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
_l_requiredSkeletonDat = ['__d_controlShapes__','__l_jointAttrs__','__l_buildOrder__']
_l_requiredRigDat = []

_l_blockStates = ['define','template','prerig','rig']
_l_requiredModuleDat = ['__version__',
                        'template','is_template','templateDelete',
                        'prerig','is_prerig','prerigDelete',
                        'rig','is_rig','rigDelete']

#These are our default attrs to make library. To be called via modules
_d_attrsTo_make = {'side':'none:left:right:center',
                   'position':'none:front:back:upper:lower:forward',
                   'basicShape':'circle:square:pyramid:semiSphere:sphere:cube',
                   'loftShape':'square:circle:squareRounded:triangle',
                   'loftSides':'int',     
                   'loftSplit':'int',
                   'loftDegree':'linear:cubic',
                   'controlType':'main:sub:direct:extra',    
                   'baseNames':'stringDatList',
                   'hasRootJoint':'bool',
                   'numberControls':'int',
                   'numberJoints':'int',
                   'buildDirect':'bool',
                   'buildIK':'bool',
                   'buildAdditiveScale':'bool',                   
                   'customStartOrientation':'bool',
                   'moduleTarget':'messageSimple',
                   'proxyType':'none:castMesh'}

