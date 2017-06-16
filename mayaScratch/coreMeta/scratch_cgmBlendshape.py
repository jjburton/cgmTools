import cgm.core
cgm.core._reload()
from cgm.core import cgm_Deformers as cgmDeformers

from cgm.core.lib import geo_Utils as GEO
reload(GEO)
mGeo = cgmMeta.cgmObject('base')
GEO.get_deltaBaseLine(mGeo)


cgm.core._reload()

mi_bsNode = cgmDeformers.cgmBlendShape('pSphere1_bsNode')
mi_bsNode.set_bsShapeDeltaToTargetMesh('xfer_large1', 0, 1.0)
