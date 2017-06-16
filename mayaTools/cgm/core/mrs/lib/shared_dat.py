"""
------------------------------------------
builder_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
_l_requiredModuleDat = ['__version__']
_l_requiredSkeletonDat = ['__d_controlShapes__','__l_jointAttrs__','__l_buildOrder__']
_l_requiredRigDat = []


_d_attrsTo_make = {'direction':'none:left:right:center',
                   'position':'none:front:back:upper:lower:forward',
                   'hasRootJoint':'bool',
                   'proxyType':'none:castMesh'}