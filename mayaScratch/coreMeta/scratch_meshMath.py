import cgm.core
cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta

from cgm.core.lib import geo_Utils as GEO
reload(GEO)
from cgm.core.cgmPy import validateArgs
reload(validateArgs)
mGeo = cgmMeta.cgmObject('base')
mGeo = cgmMeta.cgmObject('xfer_large')
GEO.get_deltaBaseLine(mGeo)
cgm.core._reload()
from cgm.core.lib import geo_Utils as GEO
reload(GEO)
GEO.get_symmetryDict(axis = 'x')
GEO.get_symmetryDict(axis = 'y')
GEO.get_symmetryDict(axis = 'z')
GEO.get_symmetryDict(axis = 'x', returnMode = 'i')
from cgm.core.lib import geo_Utils as GEO
reload(GEO)
GEO.get_symmetryDict(axis = 'x')
GEO.get_symmetryDict(axis = 'y')
GEO.get_symmetryDict(axis = 'z')
GEO.get_symmetryDict(axis = 'x', returnMode = 'i')

len('a')
GEO.get_symmetryDict('xfer_large3')
mc.select ('xfer_largeShape.vtx[379]','xfer_largeShape.vtx[369]')
GEO.get_symmetryDict('xfer_large', 'world')
GEO.get_symmetryDict('xfer_large', 'bb')
abs(-1)
abs(1)
from cgm.core.cgmPy import validateArgs
reload(validateArgs)
mGeo = cgmMeta.cgmObject('base')
mGeo = cgmMeta.cgmObject('xfer_large')
GEO.get_deltaBaseLine(mGeo)
cgm.core._reload()
_diff = GEO.meshMath(mode = 'diff', resultMode = 'values', space = 'os', multiplier = None)
_diff
GEO.meshMath(sourceObj = _diff, target = 'base', mode = 'add', resultMode = 'new')

GEO.meshMath(mode = 'add', space = 'os', multiplier = None)
GEO.meshMath(mode = '+diff', space = 'os', multiplier = None)
GEO.meshMath(mode = '-diff', space = 'os', multiplier = 2)
GEO.meshMath(mode = 'diff', space = 'os', multiplier = 1)
GEO.meshMath(mode = 'reset', space = 'os', multiplier = None)
reload(GEO)

GEO.meshMath(mode = 'xBlend', space = 'os', multiplier = None)
GEO.meshMath(mode = 'yBlend', space = 'os', multiplier = None)
GEO.meshMath(mode = 'zBlend', space = 'os', multiplier = None)

GEO.meshMath(mode = 'xOnly', space = 'os', multiplier = None)
GEO.meshMath(mode = 'yOnly', space = 'os', multiplier = None)
GEO.meshMath(mode = 'zOnly', space = 'os', multiplier = None)

GEO.meshMath(mode = 'flip', space = 'os', multiplier = None)
GEO.meshMath(mode = 'symPos', space = 'os', multiplier = None)
GEO.meshMath(mode = 'symNeg', space = 'os', multiplier = None)
GEO.meshMath(mode = 'reset', space = 'os', multiplier = None)

GEO.meshMath(mode = 'subtract', space = 'os', multiplier = 1)
GEO.meshMath(mode = 'multiply', space = 'os',  multiplier = 1.5)
GEO.meshMath(mode = 'divide', space = 'os', multiplier = 1.5)
GEO.meshMath(mode = 'average', space = 'os', multiplier = 1)

GEO.meshMath(mode = 'blend', space = 'os', multiplier = 2)
GEO.meshMath(mode = 'blend', space = 'os', multiplier = 1.5)
GEO.meshMath(mode = 'blend', space = 'os', multiplier = 1)
GEO.meshMath(mode = 'blend', space = 'os', multiplier = .75)
GEO.meshMath(mode = 'blend', space = 'os', multiplier = .5)
GEO.meshMath(mode = 'blend', space = 'os', multiplier = .25)
GEO.meshMath(mode = 'blend', space = 'os', multiplier = .5)

GEO.meshMath(mode = 'blend', space = 'w', multiplier = 2)
GEO.meshMath(mode = 'blend', space = 'w', multiplier = 1.5)
GEO.meshMath(mode = 'blend', space = 'w', multiplier = 1)
GEO.meshMath(mode = 'blend', space = 'w', multiplier = .75)
GEO.meshMath(mode = 'blend', space = 'w', multiplier = .5)
GEO.meshMath(mode = 'blend', space = 'w', multiplier = .25)




