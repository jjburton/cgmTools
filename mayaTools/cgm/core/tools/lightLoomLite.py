"""
------------------------------------------
Light Loom Lite: cgm.core.tools
Authors: Matt Berenty | Josh Burton

Website : http://www.cgmonastery.com
------------------------------------------
================================================================
"""
__version__ = '0.1.01022019'
__MAYALOCAL = 'LIGHTLOOMLITE'


# From Python =============================================================
import copy
import re
import sys
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
from Red9.core import Red9_Meta as r9Meta

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import search_utils as SEARCH
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

d_profiles = {'modeling2':{'back_right': {'dag': {'orient': [149.8269192017149,
                                                            -34.31589051142867,
                                                            86.96559860743753],
                                                 'position': [37.86773955420067,
                                                              12.584391673753146,
                                                              -19.662372050992847]},
                                         'settings': {'color': (0.0, 0.4120999872684479, 1.0),
                                                      'intensity': 1.2048193216323853},
                                         'type': 'directionalLight'},
                          'back': {'dag': {'orient': [-139.1551534832984,
                                                               7.0685525095093835,
                                                               -17.677475166287874],
                                                    'position': [5.338372934864596,
                                                                 22.25696525807767,
                                                                 -9.807179298371963]},
                                            'settings': {'color': (1.0,
                                                                   0.8830000162124634,
                                                                   0.5550000071525574),
                                                         'intensity': 0.2409638613462448},
                                            'type': 'directionalLight'},
                          'back_left': {'dag': {'orient': [-137.80030891127288,
                                                                    5.401106924411733,
                                                                    70.28216954100812],
                                                         'position': [-28.801250988640763,
                                                                      24.538696474173694,
                                                                      -15.921167096897996]},
                                                 'settings': {'color': (1.2760000228881836,
                                                                        0.18950000405311584,
                                                                        0.0),
                                                              'intensity': 1.5060241222381592},
                                                 'type': 'directionalLight'},
                          'key': {'dag': {'orient': [-39.599421538287224,
                                                              -33.48346679103192,
                                                              -81.37923606699864],
                                                   'position': [12.065361460355659,
                                                                14.328787931728947,
                                                                40.498967064890024]},
                                           'settings': {'color': (1.0, 0.7455999851226807, 0.5),
                                                        'intensity': 0.03999999910593033},
                                           'type': 'directionalLight'}},
              'modeling1':{'back': {'dag': {'orient': [-144.58960250011384,
                                                      2.2004948103566293,
                                                      -5.614774127338882],
                                           'position': [1.2204236414501435,
                                                        21.768248864596522,
                                                        -12.029355817572641]},
                                   'settings': {'color': (1.0,
                                                          0.8830000162124634,
                                                          0.5550000071525574),
                                                'intensity': 0.0},
                                   'type': 'directionalLight'},
                          'backRight': {'dag': {'orient': [146.09132517298158,
                                                           -27.7736344854791,
                                                           101.39824404906868],
                                                'position': [35.709764470088,
                                                             18.50635498867393,
                                                             -19.00707852193206]},
                                        'settings': {'color': (1.100000023841858,
                                                               0.7000000476837158,
                                                               0.0),
                                                     'intensity': 2.499999761581421},
                                        'type': 'directionalLight'},
                          'back_left': {'dag': {'orient': [-142.91535712301646,
                                                           10.634152950172071,
                                                           82.07004991417486],
                                                'position': [-32.0657141659523,
                                                             15.878922647716387,
                                                             -20.119469065185047]},
                                        'settings': {'color': (0.46737128496170044,
                                                               0.4229999780654907,
                                                               3.0),
                                                     'intensity': 3.5999999046325684},
                                        'type': 'directionalLight'},
                          'bottom': {'dag': {'orient': [-76.26987007405373,
                                                        77.60232492630021,
                                                        172.81177983110322],
                                             'position': [-0.12152552355322283,
                                                          -43.81936242930551,
                                                          -7.66747645912023]},
                                     'settings': {'color': (0.8108879923820496,
                                                            0.8536093831062317,
                                                            0.9039999842643738),
                                                  'intensity': 1.1000001430511475},
                                     'type': 'directionalLight'},
                          'key': {'dag': {'orient': [-37.063578141498425,
                                                     -40.47851812884972,
                                                     -70.40515212485938],
                                          'position': [5.661759079407707,
                                                       20.67299959753195,
                                                       39.135981089679255]},
                                  'settings': {'color': (1.0, 1.0, 1.0),
                                               'intensity': 1.5},
                                  'type': 'directionalLight'}},
              'fireSide':{'fill': {'dag': {'orient': [-525.2780421629645,
                                                      -46.04075978081318,
                                                      -14.22501206341005],
                                           'position': [-32.36513573898018,
                                                        13.68887906486817,
                                                        -21.21923239503386]},
                                   'settings': {'color': (0.19599999487400055,
                                                          0.33320000767707825,
                                                          1.0),
                                                'intensity': 2.0},
                                   'type': 'directionalLight'},
                          'fire': {'dag': {'orient': [-79.16026364278069,
                                                      60.757407783934966,
                                                      -186.08741999751626],
                                           'position': [-0.16402994945061425,
                                                        -44.38078490843497,
                                                        -3.0431090190432952]},
                                   'settings': {'color': (1.0, 0.388866662979126, 0.0),
                                                'intensity': 3.1111111640930176},
                                   'type': 'directionalLight'},
                          'key': {'dag': {'orient': [-176.7546664004424,
                                                     -113.2320152670248,
                                                     119.10754421352334],
                                          'position': [6.174466342597539,
                                                       24.65057470446122,
                                                       36.678039426998424]},
                                  'settings': {'color': (0.0,
                                                         0.07349206507205963,
                                                         0.9409999847412109),
                                               'intensity': 1.5},
                                  'type': 'directionalLight'}},
              'night':{'bounce': {'dag': {'orient': [-74.66499599543174,
                                                     52.569412503821916,
                                                     -169.49302053803888],
                                          'position': [-0.16402994945061425,
                                                       -44.38078490843497,
                                                       -3.0431090190432952]},
                                  'settings': {'color': (0.4397999942302704,
                                                         0.5284000039100647,
                                                         0.8626999855041504),
                                               'intensity': 0.0},
                                  'type': 'directionalLight'},
                       'fill': {'dag': {'orient': [-381.5259739490165,
                                                   -74.92852852873064,
                                                   -144.31346737450247],
                                        'position': [-32.36513573898018,
                                                     13.68887906486817,
                                                     -21.21923239503386]},
                                'settings': {'color': (0.19599999487400055,
                                                       0.33320000767707825,
                                                       1.0),
                                             'intensity': 1.1111111640930176},
                                'type': 'directionalLight'},
                       'key': {'dag': {'orient': [99.18578286737527,
                                                  -69.33873110009108,
                                                  -138.08788733575858],
                                       'position': [6.174466342597539,
                                                    24.65057470446122,
                                                    36.678039426998424]},
                               'settings': {'color': (0.0,
                                                      0.07349206507205963,
                                                      0.9409999847412109),
                                            'intensity': 2.222222328186035},
                               'type': 'directionalLight'},
                       'moon': {'dag': {'orient': [388.7137070607546,
                                                   -160.32334853621197,
                                                   -42.16551888879823],
                                        'position': [35.41534813622566,
                                                     16.41819453058887,
                                                     -21.333951630219506]},
                                'settings': {'color': (1.0,
                                                       0.9613999724388123,
                                                       0.9606999754905701),
                                             'intensity': 0.6666666865348816},
          'type': 'directionalLight'}},
              'dusk':{'bounce': {'dag': {'orient': [-82.64772082434983,
                                                    55.35618109265466,
                                                    -172.29651369125858],
                                         'position': [-0.16402994945061425,
                                                      -44.38078490843497,
                                                      -3.0431090190432952]},
                                 'settings': {'color': (0.4397999942302704,
                                                        0.82669997215271,
                                                        0.8626999855041504),
                                              'intensity': 1.703703761100769},
                                 'type': 'directionalLight'},
                      'fill': {'dag': {'orient': [-372.7557052275718,
                                                  -46.59395678169743,
                                                  -143.9759982969701],
                                       'position': [-32.36513573898018,
                                                    13.68887906486817,
                                                    -21.21923239503386]},
                               'settings': {'color': (0.48399999737739563,
                                                      0.21559999883174896,
                                                      1.0),
                                            'intensity': 1.5},
                               'type': 'directionalLight'},
                      'key': {'dag': {'orient': [97.26050484478581,
                                                 -41.6443786335215,
                                                 -117.05233225332694],
                                      'position': [6.174466342597539,
                                                   24.65057470446122,
                                                   36.678039426998424]},
                              'settings': {'color': (1.0, 0.632269024848938, 0.5449999570846558),
                                           'intensity': 1.703703761100769},
                              'type': 'directionalLight'},
                      'sun': {'dag': {'orient': [337.4116029337838,
                                                 -121.76039081992025,
                                                 25.029121749984085],
                                      'position': [35.41534813622566,
                                                   16.41819453058887,
                                                   -21.333951630219506]},
                              'settings': {'color': (0.9692000150680542,
                                                     0.017100000753998756,
                                                     0.0),
                                           'intensity': 1.6296296119689941},
                              'type': 'directionalLight'}},
              'day':{'bounce': {'dag': {'orient': [-86.69984309149251,
                                                   56.80181294633969,
                                                   -175.66807942874752],
                                        'position': [-0.08730806218455285,
                                                     -44.21433975747943,
                                                     -4.9016348831099155]},
                                'settings': {'color': (0.6934999823570251,
                                                       0.8482999801635742,
                                                       0.8626999855041504),
                                             'intensity': 0.8148148059844971},
                                'type': 'directionalLight'},
                     'fill': {'dag': {'orient': [-319.58425411412173,
                                                 14.609237784228485,
                                                 -123.17963404236552],
                                      'position': [-31.917790024485367,
                                                   14.584277305809055,
                                                   -21.3001591616067]},
                              'settings': {'color': (0.9606999754905701,
                                                     0.9327999949455261,
                                                     0.8288999795913696),
                                           'intensity': 0.7407407164573669},
                              'type': 'directionalLight'},
                     'key': {'dag': {'orient': [-58.23814312042314,
                                                -13.750288713272639,
                                                -84.88177505076706],
                                     'position': [5.398003922851215,
                                                  23.08957474003413,
                                                  37.799292798381884]},
                             'settings': {'color': (1.0, 1.0, 1.0),
                                          'intensity': .75},
                             'type': 'directionalLight'},
                     'sun': {'dag': {'orient': [136.08619078740466,
                                                -87.63625472916992,
                                                126.712753908411],
                                     'position': [35.84943816047591,
                                                  17.276372589351897,
                                                  -19.881806284816534]},
                             'settings': {'color': (1.7652266025543213,
                                                    1.6012107133865356,
                                                    1.1420373916625977),
                                          'intensity': 1.5},
                             'type': 'directionalLight'}},
              'dawn':{'backLeft': {'dag': {'orient': [-142.91535712301643,
                                          10.634152950172068,
                                          82.0700499141749],
                               'position': [-32.0657141659523,
                                            15.878922647716387,
                                            -20.119469065185047]},
                       'settings': {'color': (0.9606999754905701,
                                              0.652899980545044,
                                              0.640500009059906),
                                    'intensity': 0.37037038803100586},
                       'type': 'directionalLight'},
                      'fill': {'dag': {'orient': [34.601225083794894,
                                                  -0.6973337169539241,
                                                  -111.45326643497647],
                                       'position': [-0.12152552355322283,
                                                    -43.81936242930551,
                                                    -7.66747645912023]},
                               'settings': {'color': (1.0,
                                                      0.8808000087738037,
                                                      0.8626999855041504),
                                            'intensity': 1.0},
                               'type': 'directionalLight'},
                      'key': {'dag': {'orient': [-79.968285216368,
                                                 -12.706194695679418,
                                                 -90.7405652689505],
                                      'position': [5.661759079407707,
                                                   20.67299959753195,
                                                   39.135981089679255]},
                              'settings': {'color': (0.8431000113487244,
                                                     0.9509000182151794,
                                                     1.0),
                                           'intensity': 1.5},
                              'type': 'directionalLight'},
                      'sun': {'dag': {'orient': [104.02014808536255,
                                                 -14.794449013129281,
                                                 81.23140036794108],
                                      'position': [35.709764470088,
                                                   18.50635498867393,
                                                   -19.00707852193206]},
                              'settings': {'color': (1.0,
                                                     0.1371999979019165,
                                                     0.1371999979019165),
                                           'intensity': 1.0370370149612427},
                              'type': 'directionalLight'}}}

d_lightCalls = {'directionalLight':mc.directionalLight,
                'pointLight':mc.pointLight,
                'ambientLight':mc.ambientLight,
                'spotLight':mc.spotLight}


def uiMenu(parent):
    _str_func = 'uiMenu'
    
    _uiRoot = mc.menuItem(parent = parent, l='LightLoom Lite', subMenu=True,tearOff=True)
    
    _keys = d_profiles.keys()
    _keys.sort()
    
    mUI.MelMenuItemDiv(_uiRoot,label='Setup')
    
    _uiToPersp = mc.menuItem(parent = _uiRoot,subMenu=True,
                             l='toPersp',
                             )

    _uiToSelected = mc.menuItem(parent = _uiRoot,subMenu=True,
                             l='toSelected',
                             )
    _uiToNone = mc.menuItem(parent = _uiRoot,subMenu=True,
                            l='toWorld',
                            )    
    for k in _keys:
        mc.menuItem(parent = _uiToPersp,
                    l=k,
                    ann = "Setup {0} Orient to persp cam".format(k),
                    c=cgmGEN.Callback(factory, **{'profile':k,'constrainTo':'persp'}))
        mc.menuItem(parent = _uiToSelected,
                    l=k,
                    ann = "Setup {0} Orient to selected".format(k),
                    c=cgmGEN.Callback(factory, **{'profile':k,'constrainTo':'selected'}))        
        mc.menuItem(parent = _uiToNone,
                    l=k,
                    ann = "Setup {0} to world".format(k),
                    c=cgmGEN.Callback(factory, **{'profile':k,'constrainTo':None}))
        
    mUI.MelMenuItemDiv(_uiRoot,label='Utilities')
    mc.menuItem(parent = _uiRoot,
                l='Get Light Dict',
                ann = "Get light dict of selected lights",
                c=cgmGEN.Callback(get_lightDict))    
    mc.menuItem(parent = _uiRoot,
                l='Clean cgmLights',
                ann = "Remove cgmLights from scene",
                c=cgmGEN.Callback(clean_lights))    
    

def get_lightDict(lights=None):
    if lights is None:
        lights = mc.ls(sl=1)
        if not lights:
            log.warning("No lights found")
            return False
        
    _res = {}
    for l in lights:
        mDag = cgmMeta.asMeta(l)
        mLight = mDag.getShapes(asMeta=1)[0]
        _base = str(mDag.p_nameBase)
        _res[_base] = {}
        d = _res[_base]
        d['type'] = str(mLight.getMayaType())
        d['settings'] = {'intensity':mLight.intensity,
                         'color':mLight.color}
        d['dag']= {'position':mDag.p_position,
                   'orient':mDag.p_orient}
        
    pprint.pprint(_res)
    return _res

@cgmGEN.Timer
def clean_lights():
    _str_func = 'clean_lights'
    l_lights = []
    for t in d_lightCalls.keys():
        l_lights.extend(mc.ls(type=t))
    if l_lights:
        log.debug("|{0}| >> existing Lights:  {1} | ...".format(_str_func,len(l_lights)))
        for l in l_lights:
            mLight = cgmMeta.asMeta(l)
            if mLight.getMayaAttr('cgmType') == 'cgmLight':
                log.debug("|{0}| >> cgmLight:  {1} | ...".format(_str_func,mLight))                
                mLight.getTransform(asMeta=1).delete()
    else:
        log.debug("|{0}| >> no existing lights...".format(_str_func)) 
        
    if mc.objExists('cgmLightGroup'):
        mc.delete('cgmLightGroup')        

class factory(object):
    @cgmGEN.Timer
    def __init__(self, profile = 'default', constrainMode = 'orient', constrainTo = 'selected', clean = True, forceNew = True, autoBuild = True, *a,**kws):
        """
        Simple light studio setup idea

        """
        _str_func = 'factory._init_'
        self.mLightGroup = None
        self.b_clean = clean
        self.profile = profile
        self.constrainTo = None
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self.call_kws = kws
            log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
            
        if constrainTo == 'selected':
            _sel = mc.ls(sl=1) or False
            if _sel:
                self.constrainTo = _sel[0]
        else:
            self.constrainTo = constrainTo
        
        if autoBuild:
            clean_lights()
            self.get_lights()
            mLightGroup = cgmMeta.cgmObject(name='cgmLightGroup')
            for mLight in self.ml_lightDags:
                mLight.p_parent = mLightGroup
                
            if self.constrainTo and constrainMode:
                mConstrainTo = cgmMeta.cgmObject(self.constrainTo)
                mLoc = mConstrainTo.doLoc()
                mConstrainTo.resetAttrs(['translate','rotate'])

                mc.orientConstraint(mConstrainTo.mNode,mLightGroup.mNode)
                mConstrainTo.doSnapTo(mLoc)
                mLoc.delete()

    @cgmGEN.Timer
    def get_lights(self):
        _str_func = 'factory.get_lights'
        _profile = d_profiles.get(self.profile)
        self.ml_lights = []
        self.ml_lightDags = []

        for n,d in _profile.iteritems():
            _type = d.get('type')
            try:_light = d_lightCalls[_type]()  
            except:
                log.error("|{0}| >> Light create fail {1} | {2}".format(_str_func,n,_type))
                continue
            mLight = cgmMeta.asMeta(_light)
            mLight.addAttr('cgmType','cgmLight',lock=True)
            mDag = mLight.getTransform(asMeta=True)
            mDag.rename("{0}_cgmLight".format(n))
            
            for a,v in d['settings'].iteritems():
                log.debug("|{0}| >> setting {1} | {2}:{3}".format(_str_func,n,a,v))                
                ATTR.set(mLight.mNode,a,v)
                
            mDag.p_position = d['dag']['position']
            mDag.p_orient = d['dag']['orient']
            log.debug("|{0}| >> setting {1} | position:{2}".format(_str_func,n,d['dag']['position']))                
            log.debug("|{0}| >> setting {1} | orient:{2}".format(_str_func,n,d['dag']['orient']))                
                
            self.ml_lightDags.append(mDag)
            self.ml_lights.append(mLight)
            #mDag.doConnectOut('instObjGroups[0]','defaultLightSet.dagSetMembers[0]')
            #mc.sets('defaultLightSet',addElement = mDag.mNode)
            
            
            
class cgmLightMaster(object):
    def __init__(self,node=None,name=None,lightType=None):
        pass
            
            
class cgmLight(cgmMeta.cgmObject): 
    def __init__(self,node=None,name=None,nodeType=None, **kws):
        #>>> TO USE Cached instance ---------------------------------------------------------
        _str_func = 'cgmLight.__init__'        
        if node is None:
            if nodeType not in d_lightCalls.keys():
                raise ValueError,"Unknown light node: {0}".format(nodeType)
            if name is None:
                name = nodeType
            _light = d_lightCalls.get(nodeType)(name=name)
            _dag = cgmMeta.getTransform(_light)
            ATTR.add(_dag,'mClass','string',value='cgmLight',lock=True)
            self.__justCreatedState__ = True                
            node = _dag
                
        try: super(cgmLight, self).__init__(node,name, **kws)
        except StandardError,error:
            raise StandardError, "cgmLight.__init__ fail! | %s"%error
        
        for a in ['mShape']:
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)
                
        self.mShape = None

        if self.cached:
            log.debug("|{0}| >> cached | {1}".format(_str_func,self.cached))
            return
        
        self.mShape = self.getShapes(asMeta=1)[0]
        
        
    def __createnodeasdf__(self, nodeType, name):
        '''
        :param nodeType: type of node to create
        :param name: name of the new node
        '''
        _str_func = 'cgmLight.__createnode__'        
        
        #Trying to use the light shape as the metaClass caused all sorts of issues. Best just to use the dag
        _light = d_lightCalls.get(nodeType)(name=name)
        _dag = cgmMeta.getTransform(_light)
        ATTR.add(_dag,'mClass','string',value='cgmLight')
        self.__justCreatedState__ = True
        return _dag, True
    
    def __getattribute3__(self, attr):
        '''
        Overload the method to always return the MayaNode
        attribute if it's been serialized to the MayaNode
        '''
        err = None
        try:
            _str_func = 'cgmLight.__getattribute__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))            
            return r9Meta.MetaClass.__getattribute__(self,attr)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                return r9Meta.MetaClass.__getattribute__(self.mShape,attr)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return

    def __setattr2__(self, attr, value, force=True, **kws):
        err = None
        if not ATTR.has_attr(self.mNode, attr):
            log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
            try:
                if ATTR.has_attr(self.mShape.mNode,attr):
                    log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                    return r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                log.debug("|{0}| >> shape attempt err: {1}".format(_str_func,err))
        return r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        
        
        try:
            _str_func = 'cgmLight.__setattr__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))
            
            r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return
    
class cgmLightShape(cgmMeta.cgmNode): 
    def __init__(self,node=None,name=None,nodeType=None, **kws):
        #>>> TO USE Cached instance ---------------------------------------------------------
        _str_func = 'cgmLight.__init__'        
        if node is None:
            if nodeType not in d_lightCalls.keys():
                raise ValueError,"Unknown light node: {0}".format(nodeType)
            if name is None:
                name = nodeType
            _light = d_lightCalls.get(nodeType)(name=name)
            _dag = cgmMeta.getTransform(_light)
            ATTR.add(_dag,'mClass','string',value='cgmLight',lock=True)
            self.__justCreatedState__ = True                
            node = _dag
                
        try: super(cgmLight, self).__init__(node,name, **kws)
        except StandardError,error:
            raise StandardError, "cgmLight.__init__ fail! | %s"%error
        
        for a in ['mShape']:
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)
                
        self.mShape = None

        if self.cached:
            log.debug("|{0}| >> cached | {1}".format(_str_func,self.cached))
            return
        
        self.mShape = self.getShapes(asMeta=1)[0]
        
        
    def __createnodeasdf__(self, nodeType, name):
        '''
        :param nodeType: type of node to create
        :param name: name of the new node
        '''
        _str_func = 'cgmLight.__createnode__'        
        
        #Trying to use the light shape as the metaClass caused all sorts of issues. Best just to use the dag
        _light = d_lightCalls.get(nodeType)(name=name)
        _dag = cgmMeta.getTransform(_light)
        ATTR.add(_dag,'mClass','string',value='cgmLight')
        self.__justCreatedState__ = True
        return _dag, True
    
    def __getattribute3__(self, attr):
        '''
        Overload the method to always return the MayaNode
        attribute if it's been serialized to the MayaNode
        '''
        err = None
        try:
            _str_func = 'cgmLight.__getattribute__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))            
            return r9Meta.MetaClass.__getattribute__(self,attr)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                return r9Meta.MetaClass.__getattribute__(self.mShape,attr)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return

    def __setattr2__(self, attr, value, force=True, **kws):
        err = None
        if not ATTR.has_attr(self.mNode, attr):
            log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
            try:
                if ATTR.has_attr(self.mShape.mNode,attr):
                    log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                    return r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                log.debug("|{0}| >> shape attempt err: {1}".format(_str_func,err))
        return r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        
        
        try:
            _str_func = 'cgmLight.__setattr__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))
            
            r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return
        
        
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
