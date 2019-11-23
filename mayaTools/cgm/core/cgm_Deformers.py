"""
------------------------------------------
cgm_Deformers: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'cgmDEFORMERS'

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OM
import maya.OpenMayaAnim as OMANIM 

import copy
import time

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import OM_Utils as cgmOM
from cgm.core.lib import geo_Utils as geoUtils

from cgm.lib import search
from cgm.lib import attributes
from cgm.lib import cgmMath

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

class cgmBlendShape(cgmMeta.cgmNode):  
    def __init__(self,node = None, name = 'null', **kws):
        if not search.returnObjectType(node) == 'blendShape':
            raise ValueError, "Not a blendshape"

        super(cgmBlendShape, self).__init__(node = node)
        if self.cached:return

        self._MFN = OMANIM.MFnBlendShapeDeformer(self._MObject)

    def bsShapes_get(self, asMData = False):
        result = []
        bsFn = self._MFN

        int_indices = self.get_indices()

        #Declare variables
        mBaseObjects = OM.MObjectArray()

        #>>>>May need better logic for detecting the base
        bsFn.getBaseObjects(mBaseObjects)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Meat
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        mArray_targets = OM.MObjectArray()

        for i in int_indices:
            targetsReturnBuffer = []
            targetsObjArray = OM.MObjectArray()
            bsFn.getTargets(mBaseObjects[0],i,targetsObjArray)

            for t in range( targetsObjArray.length() ):
                mArray_targets.append(targetsObjArray[t])

        if asMData:
            return mArray_targets
        return cgmOM.mObjectArray_get_list(mArray_targets)

    def bsShapes_delete(self, asMData = False):
        _shapes = self.bsShapes_get()
        _dags = []
        for o in _shapes:
            _dags.extend(mc.listRelatives(_shapes,parent=True,type='transform'))
        mc.delete(_dags)
        log.warning('cgmBlendshape.bsShapes_delete: deleted {0}'.format(_dags))
        return True

    def bsShapes_restore(self):
        """
        So you inadvertantly deleted some targets? No problem!
        If any shapes have been deleted: rebuild and rewire them.

        :returns
            list of created shapes| False
        """  	
        _str_funcName = 'cgmBlendshape.bsShapes_restoreMissing: '
        self.get_deltaBaseLine()#...this shouldn't be necessary but currently is. will investigate later.
        
        #...for our first loop, we're gonna find missing shapes and their deltas to compare in case two use the same
        _d_targetsData = self.get_targetWeightsDict()
        _d_deltas = []	
        _created = []
        for i in _d_targetsData.keys():
            for ii in _d_targetsData[i].keys():
                _d_buffer = self.bsShape_validateShapeArg(i, ii)
                #_d_buffer = _d_targetsData[i][ii]
                if not _d_buffer['shape']:
                    try:
                        _created = self.bsShape_createGeoFromIndex(i,ii)
                        _shapes = mc.listRelatives(_created,shapes = True)
                        #log.info(_str_funcName + "Missing: {0},{1} | created '{2}'".format(i,ii,_created))
                        #log.info(_shapes[0] + '.worldMesh[0]')
                        log.info(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputGeomTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))
                        attributes.doConnectAttr(_shapes[0] + '.worldMesh[0]',
                                                 self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputGeomTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))
                        #_data = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputPointsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))
                    except Exception,err:
                        raise Exception, err
                    #self.bsShape_replace(self.bsShape_createGeoFromIndex(i,ii), i, ii)



    def bsShape_createGeoFromIndex(self, shapeOrIndex = None,  weight = 1.0, multiplier = None):
        """
        Creates a mesh duplicate of a target index and weight. 

        :parameters:
            shapeOrIndex(str/int): name of bsShape or index
            weight(float): the weight of the target
            multiplier(float):factor to multiply the delta by

        :returns
            name of new mesh
        """  
        _str_funcName = 'cgmBlendshape.bsShape_createGeoFromIndex: '

        _d_buffer = self.bsShape_validateShapeArg(shapeOrIndex, weight)
        if not _d_buffer:
            raise ValueError, _str_funcName + "shapeOrIndex({0}) and weight ({1}) found no data.".format(shapeOrIndex,weight)

        #mc.getAttr('pSphere1_bsNode.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputPointsTarget')
        _data = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputPointsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))
        _components = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputComponentsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))

        _baseObject = self.get_baseObjects()[0]    
        _dup = mc.duplicate(_baseObject)
        _dup = mc.rename(_dup, _d_buffer['alias'] + '_' + str(_d_buffer['weight']))
        _l_deltaBaseLine = self.get_deltaBaseLine()

        idx = 0
        for componentSet in _components:
            if ':' in componentSet:
                _buffer = mc.ls("{0}.{1}".format(_dup,componentSet), flatten = True)
            else:
                _buffer = ["{0}.{1}".format(_dup,componentSet)]
            for c in _buffer:
                _idx = int(c.split('[')[1].split(']')[0])
                if multiplier is not None:
                    _c_data = [multiplier*v for v in _data[idx][:-1]]
                else:
                    _c_data = _data[idx][:-1]

                _deltaPlus_base = cgmMath.list_add(_l_deltaBaseLine[_idx], _c_data)
                #log.info(_str_funcName + c)
                mc.xform(c, t =_deltaPlus_base, os = True, a=True)
                #mc.xform(c, t = [-v for v in _data[idx][:-1]], r = True, os = True)		
                idx +=1   
        return _dup

    def bsShape_createTargetBase(self):
        """
        Create a clean target base

        :returns
            name of new mesh
        """  
        _str_funcName = 'cgmBlendshape.bsShape_createTargetBase: '
        #cgmNode().getTransform(asMeta = True)
        _baseShape = self.get_baseObjects(asMeta = True)[0]
        _baseTrans = cgmMeta.validateObjArg(_baseShape.getTransform(),'cgmObject')
        _deformers = _baseTrans.getDeformers(asMeta = True)

        _d_wiring = {}
        #...go through and zero out the envelops on the deformers
        for mDef in _deformers:
            _d = {}
            _envelopeAttr = "{0}.envelope".format(mDef.mNode)
            _plug = attributes.returnDriverAttribute(_envelopeAttr) or False
            if _plug:
                attributes.doBreakConnection(_envelopeAttr)
            _d['plug'] = _plug
            _d['value'] = mDef.envelope
            _d['attr'] = _envelopeAttr
            _d_wiring[mDef] = _d
            mDef.envelope = 0
        _dup = mc.duplicate(_baseTrans.mNode)	

        #...rewire
        for mDef in _d_wiring.keys():
            _d = _d_wiring[mDef]
            if _d.get('plug'):
                attributes.doConnectAttr( _d.get('plug'),_d['attr'])
            else:
                mDef.envelope = _d.get('value')
        return _dup

    def get_deltaBaseLine(self):
        """
        I know there must be a better way to do this...

        :returns
            list of base line values
        """  
        _str_funcName = 'cgmBlendshape.get_deltaBaseLine: '
        _baseShape = self.get_baseObjects(asMeta = True)[0]
        _baseTrans = cgmMeta.validateObjArg(_baseShape.getTransform(),'cgmObject')
        _deformers = _baseTrans.getDeformers(asMeta = True)

        _d_wiring = {}
        #...go through and zero out the envelops on the deformers
        for mDef in _deformers:
            _d = {}
            _envelopeAttr = "{0}.envelope".format(mDef.mNode)
            _plug = attributes.returnDriverAttribute(_envelopeAttr) or False
            if _plug:
                attributes.doBreakConnection(_envelopeAttr)
            _d['plug'] = _plug
            _d['value'] = mDef.envelope
            _d['attr'] = _envelopeAttr
            _d_wiring[mDef] = _d
            mDef.envelope = 0

        #meat...
        _result = []
        _dict = cgmValid.MeshDict(_baseTrans.mNode)
        for i in range(_dict['pointCount']):
            _result.append(mc.xform("{0}.vtx[{1}]".format(_baseTrans.mNode,i), t = True, os = True, q=True))

        #...rewire
        for mDef in _d_wiring.keys():
            _d = _d_wiring[mDef]
            if _d.get('plug'):
                attributes.doConnectAttr( _d.get('plug'),_d['attr'])
            else:
                mDef.envelope = _d.get('value')
        return _result

    def bsShape_getDelta(self, shapeOrIndex = None, weight = 1.0, flatten = True):

        #Props to Daniel Lima
        #https://github.com/Bumpybox/Tapp/blob/master/Maya/rigging/sculptInbetweenEditor/dslReverseShape.py

        _str_funcName_ = '{0}.bsShape_getDelta'.format(self.mNode)
        _d_buffer = self.bsShape_validateShapeArg(shapeOrIndex, weight)

        if not _d_buffer:
            raise ValueError,"{0}>> Invalid shape:{1} | weight:{2}".format(_str_funcName_,shapeOrIndex,weight)
        #mc.getAttr('pSphere1_bsNode.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputPointsTarget')
        _l_deltaVs = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputPointsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))

        if not flatten:
            return _l_deltaVs

        _components = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputComponentsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))

        _mi_base = self.get_baseObjects(asMeta = True)[0]
        #_mi_trans = cgmMeta.validateObjArg(_mi_base.getTransform(),'cgmObject')
        #_l_delta = geoUtils.get_deltaBaseLine(_mi_trans)
        _l_delta = [[0,0,0] for i in range(mc.polyEvaluate(_mi_base.mNode, vertex=True))]
        _split_idx = []
        for i,componentSet in enumerate(_components):
            if ':' in componentSet:
                _buffer = mc.ls("{0}.{1}".format(_mi_base.mNode,componentSet), flatten = True)
            else:
                _buffer = ["{0}.{1}".format(_mi_base.mNode,componentSet)]

            for c in _buffer:
                _idx = int(c.split('[')[1].split(']')[0])
                _split_idx.append(_idx)
                #if weight is not 1.0:
                    #_c_data = [weight*v for v in _l_deltaVs[i][:-1]]
                _c_data = _l_deltaVs[i][:-1]
                log.debug("idx: {0} | data:{1}".format(_idx,_c_data))
                #_l_delta[_idx] = cgmMath.list_add(_l_delta[i][:-1], _c_data)
                _l_delta[_idx] = _c_data
        #log.info(len(_l_deltaVs))
        #log.info(len(_split_idx))
        #mc.setAttr(gatherInfoFrom, type='pointArray', *resultPointArray)
        #mc.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *resultComponentList)	
        return _l_delta

        _baseObject = self.get_baseObjects()[0]
        _baseDict = cgmValid.MeshDict(_baseObject)
        _i_verts = _baseDict['pointCount']

        defaultPointArray = ([_i_verts] + [(0,0,0,1)] * _i_verts)
        return defaultPointArray

        t = time.time()
        if correctiveItem == None:
            correctiveItem = int(6000)
        crPercentage = (correctiveItem - 5000) / 10
        print "crPercentage: " + str(crPercentage) + '%'
        numVtx = cmds.getAttr (skinGeo + '.vrts', s=True )
        defaultPointArray = ([numVtx] + [(0,0,0,1)] * numVtx)
        #print defaultPointArray
        ###################################
        xSculp = cmds.xform(sculptGeo + '.pnts[*]', q=True, os=True, t=True)
        sculptPts = zip(xSculp[0::3], xSculp[1::3], xSculp[2::3])
        #####################################
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem[%s]' %correctiveItem
        iPt = '.inputPointsTarget'
        iCt = '.inputComponentsTarget'
        cr6000 = iTg + iTgGr + '.inputTargetItem[6000].inputPointsTarget'
        cri6000 = iTg + iTgGr + '.inputTargetItem[6000].inputComponentsTarget'
        gatherInfoFrom = iTg + iTgGr + iTi + iPt
        cmds.setAttr(gatherInfoFrom, type='pointArray', *defaultPointArray)
        xSkin = cmds.xform(skinGeo + '.pnts[*]', q=True, os=True, t=True)
        skinPts = zip(xSkin[0::3], xSkin[1::3], xSkin[2::3])
        offsetPointArray = []
        offsetPointArray.append([numVtx] + [(1,0,0,1)] * numVtx)
        offsetPointArray.append([numVtx] + [(0,1,0,1)] * numVtx)
        offsetPointArray.append([numVtx] + [(0,0,1,1)] * numVtx)
        axis = 'XYZ'
        unityDeltaXYZ = []
        unitDeltaX = []
        unitDeltaY = []
        unitDeltaZ = []
        for pArray in offsetPointArray:
            cmds.setAttr(gatherInfoFrom, type='pointArray', *pArray)
            tmpXform = cmds.xform(skinGeo + '.pnts[*]', q=True, os=True, t=True)
            unityDeltaXYZ.append(zip(tmpXform[0::3], tmpXform[1::3], tmpXform[2::3]))
            eval('unitDelta' + axis[offsetPointArray.index(pArray)]).append(unityDeltaXYZ[offsetPointArray.index(pArray)])
        if not keepSculpt:
            cmds.delete(sculptGeo)
        resultPointArray = []
        resultComponentList=[]
        calculated = []
        for v in range(numVtx):
            vectorSkin = om.MVector(*skinPts[v])
            vectorScpt = om.MVector(*sculptPts[v])
            disOnPose = vectorScpt - vectorSkin
            dispResult = (disOnPose.x, disOnPose.y, disOnPose.z)
            if dispResult != (0.0, 0.0, 0.0):
                resultComponentList.append('vtx[%s]' %v)
                calculated.append(1)
                dispOffset = vectorScpt - vectorSkin
                vectorunitDeltaX = om.MVector(*unitDeltaX[0][v])
                vectorunitDeltaY = om.MVector(*unitDeltaY[0][v])
                vectorunitDeltaZ = om.MVector(*unitDeltaZ[0][v])
                dispX = vectorunitDeltaX - vectorSkin
                dispY = vectorunitDeltaY - vectorSkin
                dispZ = vectorunitDeltaZ - vectorSkin
                listMatrix = (dispX.x, dispX.y, dispX.z, 0,
                              dispY.x, dispY.y, dispY.z, 0,
                              dispZ.x, dispZ.y, dispZ.z, 0,
                              0,0,0,1)
                matrix = om.MMatrix()
                om.MScriptUtil.createMatrixFromList(listMatrix, matrix)
                matrixInverted = om.MMatrix.inverse(matrix)
                vectorResult = (dispOffset * matrixInverted)
                if inBetweenMode != True:
                    vectorRlist = (float((vectorResult.x / crPercentage ) * 100),
                                   float((vectorResult.y / crPercentage ) * 100),
                                   float((vectorResult.z / crPercentage ) * 100))
                else:
                    vectorRlist = (float(vectorResult.x), float(vectorResult.y), float(vectorResult.z), int(1))
                resultPointArray.append(vectorRlist)

        #print 'resultPointtList ----> ',resultPointArray
        #print 'resultComponentList ----> ',resultComponentList
        #===========================================================================
        # ADDING FIRST VALUE TO THE RESULTS TO BE USED WITH SETATTR -TYPE
        #===========================================================================
        resultComponentList.insert(0, len(resultPointArray))
        resultPointArray.insert(0, len(resultPointArray))

        #allData = [resultPointArray, resultComponentList]

        if inBetweenMode != True:
            print '--------------IF'
            cmds.setAttr(cr6000, type='pointArray', *resultPointArray)
            cmds.setAttr(cri6000, type='componentList', *resultComponentList)
            if correctiveItem != 6000:
                cmds.removeMultiInstance(iTg + iTgGr + iTi, b=True)

        else:

            cmds.setAttr(gatherInfoFrom, type='pointArray', *resultPointArray)
            cmds.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *resultComponentList)

            if cmds.listAttr(cr6000) == None:
                print 'cmds.listAttr(cr6000) == None:'
                cmds.setAttr(cr6000, type='pointArray', *resultPointArray)
                cmds.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *resultComponentList)
            if flatten:
                cmds.setAttr(cr6000, type='pointArray', *resultPointArray)
                cmds.setAttr(cri6000, type='componentList', *resultComponentList)
    def get_indices(self):
        weightListIntArray = OM.MIntArray()
        self._MFN.weightIndexList(weightListIntArray)

        return weightListIntArray

    def get_weight_attrs(self):
        return mc.listAttr((self.mNode+'.weight'),m=True)    

    def is_bsShape(self, target = None):
        """
        See whether a provided target is a blendshape shape or not.

        :parameters:
            target | Node to check

        :returns
            list of shapes on node that are shapes| False
        """    	
        if target is None :
            _sel = mc.ls(sl=True)
            if not _sel:
                raise ValueError,"cgmBlendshape.is_bsShape: No object selected and no arg passed!"
            target = _sel[0]

        _targets = self.bsShapes_get()
        _match = []
        if cgmMeta.isTransform(target):
            for shape in mc.listRelatives(target,shapes=True,fullPath=True):
                if shape in _targets:
                    _match.append(shape)
        elif target in _targets:
            _match.append(shape)
        if not _match:
            return False
        return _match

    def bsShape_index(self, target = None):
        """
        Index a provided target. Maybe multiple.

        :parameters:
            target | Node to check

        :returns
            nested list of of indices/weights [[index,weight]...]
        """    	
        if target is None :
            _sel = mc.ls(sl=True)
            if not _sel:
                raise ValueError,"cgmBlendshape.bsShape_index: No object selected and no arg passed!"
            target = _sel[0]

        _d_targetsData = self.get_targetWeightsDict()
        _match = []
        if cgmMeta.isTransform(target):
            for shape in mc.listRelatives(target,shapes=True,fullPath=True):
                for i in _d_targetsData.keys():
                    for ii in _d_targetsData[i].keys():
                        _buffer = _d_targetsData[i][ii]
                        if shape == _buffer['shape']:
                            _match.append([i,ii])
                        #else:
                            #log.info("{0} != {1}".format(shape, _buffer['shape']))
        else:
            _shapeLong = mc.ls(target, long = True)[0]
            for i in _d_targetsData.keys():
                for ii in _d_targetsData[i].keys():
                    _buffer = _d_targetsData[i][ii]
                    if _shapeLong == _buffer['shape']:
                        _match.append([i,ii])
                    #else:
                        #log.info("{0} != {1}".format(_shapeLong, _buffer['dag']))			

        if not _match:
            return False
        return _match

    def get_baseObjects(self, asMData = False, asMeta = False):
        """
        Get base objects

        :parameters:
            asMData | Whether to return as api data or not

        :returns
            list
        """    
        baseObjects = OM.MObjectArray()

        self._MFN.getBaseObjects(baseObjects)	

        if asMeta:return cgmMeta.validateObjListArg(cgmOM.mObjectArray_get_list(baseObjects),'cgmNode')
        if asMData:return baseObjects
        return cgmOM.mObjectArray_get_list(baseObjects)


    def get_targetWeightsDict(self):
        """
        Get the target data in a nested dict format. 

        {index : {weightValue: {shape: , dag:}}}

        :returns
            dict

        """    	
        _str_funcName = 'cgmBlendshape.get_targetWeightsDict: '
        self.get_deltaBaseLine()#...this shouldn't be necessary but currently is. will investigate later.
        
        try:
            int_indices = self.get_indices()

            #bsFn = self._MFN
            bsFn = OMANIM.MFnBlendShapeDeformer(self._MObject)
            mBaseObjects = self.get_baseObjects(True)
            _array_weights_raw = OM.MIntArray() 

            targetDict = {}

            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Meat
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            for i in int_indices:
                log.debug(_str_funcName + "idx: {0}".format(i))
                d_targetsBuffer = {}
                targetsObjArray = OM.MObjectArray()
                bsFn.getTargets(mBaseObjects[0],i,targetsObjArray)
                bsFn.targetItemIndexList(i,mBaseObjects[0],_array_weights_raw)


                for ii,rawWeight in enumerate( _array_weights_raw ):
                    log.debug(_str_funcName + "Checking {0} | {1}".format(ii,rawWeight))

                    d_targetBuffer = {'dag':False,
                                      'shape':False}
                    inbetweenWeight = float( (rawWeight-5000) * .001 )

                    #try:
                    if targetsObjArray.length()>=ii +1:
                        shapeNameBuffer = ( cgmOM.mObject_getNameString(targetsObjArray[ii]))
                        geoNameBuffer = mc.listRelatives(shapeNameBuffer, parent = True, fullPath = True)
                        d_targetBuffer['dag'] = geoNameBuffer[0]
                        d_targetBuffer['shape'] = shapeNameBuffer
                    #except Exception, err:
                        #log.debug(_str_funcName +"It appears the shape geo for index: {0}| weight: {1} is missing. err: {2}".format(ii,inbetweenWeight,err))

                    #Prep data
                    log.debug(_str_funcName + "inbetweenWeight: {0} | raw:{1} | buffer:{2}".format(inbetweenWeight,rawWeight, d_targetBuffer))			
                    d_targetsBuffer[inbetweenWeight] = d_targetBuffer

                """for t in range( targetsObjArray.length() ):
		    log.info(_str_funcName + "t: {0}".format(t))		
		    d_targetBuffer = {}
		    shapeNameBuffer = ( cgmOM.mObject_getNameString(targetsObjArray[t]) )
		    geoNameBuffer = mc.listRelatives(shapeNameBuffer, parent = True, fullPath = True)
		    d_targetBuffer['dag'] = geoNameBuffer[0]
		    d_targetBuffer['shape'] = shapeNameBuffer

		    # Get the destination attr from which to calculate the inbetween weight
		    #shapeConnectionAttr = mc.connectionInfo((shapeNameBuffer+'.worldMesh'),destinationFromSource=True)
		    #targetBuffer = shapeConnectionAttr[0].split('.',)
		    #indexOneBuffer = targetBuffer[-2].split('[',)
		    #indexTwoBuffer = indexOneBuffer[1].split(']',)
		    #rawIndex = int(indexTwoBuffer[0])
		    rawIndex = _array_weights_raw[t]
		    # Calculate inbetween weight using Maya's index = weight * 1000 + 5000 formula
		    inbetweenWeight = float( (rawIndex-5000) * .001 )

		    #Prep data
		    d_targetsBuffer[inbetweenWeight] = d_targetBuffer
		    #targetsReturnBuffer.append(d_targetBuffer)"""
                targetDict[i] = d_targetsBuffer

            return targetDict
        except Exception,err:
            raise Exception,err

    def bsShape_get(self, index = None, weight = None):
        """
        Get a bsShape from an index and provided weight. If no weight is provided, will return all weights at that index.

        :parameters:
            index(int) | Index you want the bsShape from
            weight(float) | name of shape to replace or index

        :returns
            dict - {shape, dag}
        """ 
        #Validate
        _d_targetsData = self.get_targetWeightsDict()
        try:
            if weight is not None:
                return _d_targetsData[index][weight]
            return _d_targetsData[index]
        except Exception,err:
            raise Exception,"cgmBlendshape.bsShape_get: no data found at index:{0} | weight:{1}".format(index,weight)
        return False

    def bsShape_validateShapeArg(self, shapeOrIndex = None, weight = None):
        """
        Validate a shape arg

        :parameters:
            shapeOrIndex(str/int): name of bsShape or index
            weight(float): the weight of the target

        :returns
            {index, shape, dag, weight }
        """ 
        _str_func = "cgmBlendshape.bsShape_validateShapeArg: "
        if shapeOrIndex is None and weight is None:
            raise ValueError, _str_func + "Must have shape or index and weight args"

        #Validate
        _d_targetsData = self.get_targetWeightsDict()
        _l_indices = self.get_indices()	
        _index = False
        _shape = False
        _dag = False
        _weight = False
        _noFalse = ['index','alias','plug','weight']
        _d_result = {'index':False,
                     'shape':False,
                     'dag':False,
                     'alias':False,
                     'plug':False,
                     'weightIndex':False,
                     'weight':False}

        _type = type(shapeOrIndex)

        if _type is int:
            #_index = shapeOrIndex
            if shapeOrIndex in _l_indices:
                _index = shapeOrIndex
            else:
                log.warning(_str_func + "Not a valid index: {0}".format(shapeOrIndex))
                return {}

            _buffer = _d_targetsData[_index]	
            log.debug("Found index: {0} | {1}".format(_index,_buffer))

            if weight:
                if _buffer.get(weight):
                    _weight = weight
                    _shape = _buffer[weight]['shape']
                    _dag = _buffer[weight]['dag']
                else:
                    log.warning( _str_func + "Invalid weight specified. No data on: {0}".format(weight))
                    return {}

            elif len(_buffer.keys()) == 1:
                log.info(_str_func + "One key at index. Can resolve.")
                for k in _buffer.keys():
                    _weight = _buffer.keys()[0]
                    _shape = _buffer[k]['shape']
                    _dag = _buffer[k]['dag']	
                    continue
            else:
                log.warning(_str_func + "No weight specified and more than one shape on the index: {0}. Can't resolve".format(_index))
                return {}


        elif self.is_bsShape(shapeOrIndex):#if we have a string
            _buffer = self.bsShape_index(shapeOrIndex)

            if weight:
                _match = False
                for pair in _buffer:
                    log.info("{0} =?= {1}".format(weight,pair[1]))
                    if cgmMath.isFloatEquivalent(weight, pair[1]):
                        _match = True
                        _indexBuffer = _d_targetsData[pair[0]][pair[1]]
                        _index = pair[0]
                        _weight = pair[1]
                        _shape = _indexBuffer['shape']
                        _dag = _indexBuffer['dag']
                        continue
                if not _match:
                    log.warning(_str_func + "Found no data for this shape at this weight: {0}. Can't resolve".format(weight))
                    return {}


            elif len(_buffer) == 1:
                _index = _buffer[0][0]
                _weight = _buffer[0][1]
                _indexBuffer = _d_targetsData[_index][_weight]
                _shape = _indexBuffer['shape']
                _dag = _indexBuffer['dag']
            else:
                log.warning(_str_func + "Too many weight values found and none specified".format(_index))
                return {}

            _index = _buffer[0][0]
            _currentWeight = _buffer[0][1]
            #weight?
        else:
            log.warning(_str_func + "invalid shapeOrIndex ({0})".format(shapeOrIndex))
            return {}

        _d_result['index'] = _index
        _d_result['shape'] = _shape
        _d_result['dag'] = _dag
        _d_result['weight'] = _weight
        _d_result['alias'] = mc.aliasAttr('{0}.w[{1}]'.format(self.mNode,_index), q = True)
        _d_result['plug'] = '{0}.w[{1}]'.format(self.mNode,_index)
        _d_result['weightIndex'] = int(_weight * 1000 + 5000)

        for k in _noFalse:
            if _d_result.get(k) is False:
                log.info(_d_result)
                log.warning(_str_func + "Missing validated data on ({0})".format(k))
                _d_result = False

        return _d_result

    def bsShape_nameWeightAlias(self, name = None, shapeOrIndex = None, weight = 1.0):
        """
        Rename a shape's alias on the bsNode

        :parameters:
            name(str): name to use. If none, will attempt to use the target shapes name
            shapeOrIndex(str/int): name of bsShape or index
            weight(float): weight of the target to use. Only needed if we are passed an index arg

        :returns
            name
        """ 
        _str_func = "cgmBlendshape.bsShape_nameWeightAlias: "
        if shapeOrIndex is None and name is None:
            raise ValueError, _str_func + "Must have shape or index and weight args"

        _l_indices = self.get_indices()
        _index = False
        _currentName = False

        _d_validShape = self.bsShape_validateShapeArg(shapeOrIndex, weight)

        _name = self.bsShape_getAvailableAlias(name)
        mc.aliasAttr(_name, _d_validShape['plug'])
        return _name

    def bsShape_getAvailableAlias(self, name = None):
        """
        Get an available alias for the 

        :parameters:
            shapeOrIndex(str/int) | name of bsShape or index

        :returns
            {index, shape, dag, weight }
        """ 
        _str_func = "cgmBlendshape.bsShape_getAvailableAlias: "

        if name is None:
            raise ValueError, _str_func + "Must have a name arg"

        _name = str(name)#...just to make sure we're on the same playing field
        _l_attrs = [str(n) for n in self.get_weight_attrs()]

        if _name not in _l_attrs:
            return _name
        else:
            _cnt = 1
            _name_iter = "{0}_{1}".format(_name, _cnt)	    
            while _name_iter in _l_attrs:
                _cnt +=1
                _name_iter = "{0}_{1}".format(_name, _cnt)
            return _name_iter


    def bsShape_replace(self, targetShape = None, shapeToReplace = None, weight = 1.0):
        """
        Replace a givin shape with another one

        :parameters:
            targetShape(str) | name of new shape
            shapeToReplace(str/int) | name of shape to replace or index
            weight(float) | weight at which the shape is at full value

        :returns
            [index,weight]
        """ 
        #Validate
        _d_targetsData = self.get_targetWeightsDict()
        _l_indices = self.get_indices()	
        _sel = mc.ls(sl=True)
        _index = False
        _currentWeight = False
        _baseObject = self.get_baseObjects()[0]

        if targetShape is None:
            if not _sel:
                raise ValueError,"cgmBlendshape.bsShape_replace: must have an index or target shape"
            targetShape = _sel[0]

        if shapeToReplace is None:
            try:shapeToReplace = _sel[1]
            except:
                raise ValueError,"cgmBlendshape.bsShape_replace: must have an index or shapeToReplace specified"
        else:
            _type = type(shapeToReplace)
            if _type is int:
                _index = shapeToReplace
                shapeToReplace = self.bsShape_get(shapeToReplace, weight)['dag']
            elif self.is_bsShape(shapeToReplace):
                _buffer = self.bsShape_index(shapeToReplace)
                _index = _buffer[0][0]
                _currentWeight = _buffer[0][1]
                #weight?
            else:
                raise ValueError,"cgmBlendshape.bsShape_replace: invalid shapeToReplace ({0})".format(shapeToReplace)


        """if _index is None:
	    if weight != 1.0:
		raise ValueError,"cgmBlendshape.bsShape_replace: Must have index value for inbetween setup"
	    if not _l_targetArgs:
		raise ValueError,"cgmBlendshape.bsShape_replace: Must have a connected shape or an index to replace" 
	elif weight != 1.0 and _index not in _l_indices:
	    raise ValueError,"cgmBlendshape.bsShape_replace: Must have valid index value for inbetween setup. Valid indices: {0}".format(_l_indices)	    
	    """

        #Check connections
        #for 
        #blendShapeBuffer = (bsn + '.' + shape)
            #""" get the connection """
            #d_blendShapeConnections[shape] = attributes.returnDriverAttribute(blendShapeBuffer)	
        #Remove the targets at this index
        #Rebuild the index

        #Build our new arg
        _d_new_arg = copy.copy(_d_targetsData[_index])
        #for k in _d_new_arg.keys():
        #    if k == weight:
        _d_new_arg[weight] = {'shape':targetShape}

        log.debug("currentArgs: {0}".format(_d_targetsData[_index]))
        log.debug("newArgs: {0}".format(_d_new_arg))

        #Get the data for rebuilding
        plug_in = attributes.returnDriverAttribute("{0}.{1}".format(self.mNode, self.get_weight_attrs()[_index]))

        #Remove the existing targets on that index
        for w in _d_targetsData[_index]:
            self.bsShape_remove(_d_targetsData[_index][w]['shape'], index = _index, weight = w)

        #Need to rebuild in 1.0 order
        l_keys = _d_new_arg.keys()
        l_keys.sort()
        l_keys.reverse()

        for w in l_keys:
            self.bsShape_add(_d_new_arg[w]['shape'], index = _index, weight = w)   

        if plug_in:
            attributes.doConnectAttr(plug_in, "{0}.{1}".format(self.mNode, self.get_weight_attrs()[_index]))

        log.debug(cgmGeneral._str_subLine)	
        log.debug("cgmBlendshape.bsShape_replace...")
        log.debug("index: {0}".format(_index))	
        log.debug("baseObject: {0}".format(_baseObject))	
        log.debug("targetShape: {0}".format(targetShape))
        log.debug("weight: {0}".format(weight))		
        log.debug("shapeToReplace: {0}".format(shapeToReplace))
        log.debug("currentWeight: {0}".format(_currentWeight))	
        log.debug("driverPlug: {0}".format(plug_in))	
        log.debug(cgmGeneral._str_subLine)
        #log.debug("currentArgs: {0}".format(_d_targetsData[_index]))
        #log.debug("newArgs: {0}".format(_d_new_arg))

        #log.debug("pre data: {0}".format(_d_targetsData[_index]))
        #log.debug("post data: {0}".format(self.get_targetWeightsDict()[_index]))	

        log.debug(cgmGeneral._str_hardBreak)	

        return [_index,weight]

    def bsShape_add(self, targetShape = None, index = None, weight = 1.0):
        """
        Add a shape

        :parameters:
            targetShape(str) | name of new shape
            index(int) | index to use -- None will use the next available
            weight(float) | weight at which the shape is at full value

        :returns
            [index,weight]
        """ 	
        if targetShape is None:
            _sel = mc.ls(sl=True)
            if not _sel:
                raise ValueError,"cgmBlendshape.bsShape_add: must have an index or target shape"
            targetShape = _sel[0]

        _l_indices = self.get_indices()
        if index is None:
            if weight != 1.0:
                raise ValueError,"cgmBlendshape.bsShape_add: Must have index value for inbetween setup"

            _foundValue = False
            _cnt = 0
            while not _foundValue:
                if _cnt not in _l_indices:
                    _foundValue = True
                    index = _cnt
                    log.debug("cgmBlendshape.bsShape_add: Found open index: {0}".format(_cnt))
                _cnt+=1	  
        elif weight != 1.0 and index not in _l_indices:
            raise ValueError,"cgmBlendshape.bsShape_add: Must have valid index value for inbetween setup. Valid indices: {0}".format(_l_indices)	    

        _baseObject = self.get_baseObjects()[0]
        log.debug("cgmBlendshape.bsShape_add...")
        log.debug("baseObject: {0}".format(_baseObject))	
        log.debug("targetShape: {0}".format(targetShape))
        log.debug("index: {0}".format(index))
        log.debug("weight: {0}".format(weight))
        log.debug(cgmGeneral._str_subLine)

        if weight == 1.0:
            mc.blendShape(self.mNode, edit = True, ib = False , target = [_baseObject,index,targetShape,weight])
        else:
            mc.blendShape(self.mNode, edit = True, ib = True , target = [_baseObject,index,targetShape,weight])	   

        return [index,weight]

    def bsShape_remove(self, targetShape = None, index = None, weight = None):
        if index is None and targetShape is None:
            _sel = mc.ls(sl=True)
            if not _sel:
                raise ValueError,"cgmBlendshape.bsShape_remove: must have an index or target shape"
            targetShape = _sel[0]

        if targetShape is None:
            try:
                targetShape = self.bsShapes_get()[index]
            except Exception, err:
                raise Exception,"cgmBlendshape.bsShape_remove: invalid index most likely | {0}".format(err)

        _baseObject = self.get_baseObjects()[0]
        _args = self.bsShape_getTargetArgs(targetShape)

        log.debug("cgmBlendshape.bsShape_remove...")
        log.debug("baseObject: {0}".format(_baseObject))	
        log.debug("targetShape: {0}".format(targetShape))
        log.debug("index: {0}".format(index))
        log.debug("Shape args: {0}".format(_args))
        log.debug(cgmGeneral._str_subLine)

        if index is not None and weight is None:
            mc.blendShape(self.mNode, edit = True, remove = True, target = [_baseObject,index,targetShape,1.0])	
        elif weight is not None:
            mc.blendShape(self.mNode, edit = True, remove = True, target = [_baseObject,index,targetShape,weight])		    
        else:
            for arg in _args:
                mc.blendShape(self.mNode, edit = True, remove = True, target = [_baseObject] + arg)	

        return True

    def set_bsShapeDeltaToTargetMesh(self, targetMesh = None, shapeOrIndex = None, weight = None, multiplier = None):
        """
        Apply the delta shape to another mesh of the same vertice count. 
        If the meshes can be placed over one and be equivalent use a 
        wrap bake method found in deformers.

        :parameters:
            targetMesh(str) | mesh target
            shapeOrIndex(str/int) | name of shape to replace or index -- pass through to bsShape_getDelta
            weight(float) | weight at which the shape is at full value -- pass through to bsShape_getDelta

        :returns
            newTarget
        """ 
        _str_func = "cgmBlendshape.set_bsShapeDeltaToTargetMesh: "

        _d_buffer = self.bsShape_validateShapeArg(shapeOrIndex, weight)
        if not _d_buffer:
            raise ValueError, _str_funcName + "shapeOrIndex({0}) and weight ({1}) found no data.".format(shapeOrIndex,weight)

        #Get our target mesh
        mi_target = cgmMeta.validateObjArg(targetMesh,'cgmObject', mayaType = ['mesh'])

        #Get the target Delta
        import cgm.core.lib.geo_Utils as GEO
        _targetBaseDelta = GEO.get_deltaBaseLine(mi_target)

        #Get Base delta
        _baseDelta = self.get_deltaBaseLine()

        #Get Target delta
        _targetShapeDelta = self.bsShape_getDelta(shapeOrIndex, weight)

        #Geo stuff
        d_target = cgmValid.MeshDict(mi_target.mNode)
        _baseShape = self.get_baseObjects(asMeta = True)[0]
        _baseTrans = cgmMeta.validateObjArg(_baseShape.getTransform(),'cgmObject')	
        d_base = cgmValid.MeshDict(_baseTrans.mNode)

        log.info(cgmGeneral._str_subLine)	
        log.info("cgmBlendshape.set_bsShapeDeltaToTargetMesh...")
        log.info("baseCount: {0}".format(d_base['pointCount']))	
        log.info("targCount: {0}".format(d_target['pointCount']))	

        log.info("bDelta: {0} | {1}".format(len(_baseDelta),_baseDelta))	
        log.info("tDelta: {0} | {1}".format(len(_targetBaseDelta),_targetBaseDelta))	
        log.info("sDelta: {0} | {1}".format(len(_targetShapeDelta),_targetShapeDelta))	
        log.info(cgmGeneral._str_subLine)


        #Do the math
        #Apply the delta ||  (target - base) + delta?

        #mc.getAttr('pSphere1_bsNode.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputPointsTarget')
        #_data = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputPointsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))
        #_components = mc.getAttr(self.mNode + '.inputTarget[0].inputTargetGroup[{0}].inputTargetItem[{1}].inputComponentsTarget'.format(_d_buffer['index'],_d_buffer['weightIndex']))

        #_baseObject = self.get_baseObjects()[0]    
        _dup = mc.duplicate(mi_target.mNode)
        _strNew = "{0}_{1}_{2}".format(mi_target.p_nameBase,_d_buffer['alias'],(_d_buffer['weight']))
        iii = 0
        while mc.objExists(_strNew) and iii < 100:
            _strNew = "{0}_NEW_{1}".format(_strNew,iii)
        _dup = mc.rename(_dup, _strNew)

        return
        idx = 0
        for componentSet in _components:
            if ':' in componentSet:
                _buffer = mc.ls("{0}.{1}".format(_dup,componentSet), flatten = True)
            else:
                _buffer = ["{0}.{1}".format(_dup,componentSet)]
            for c in _buffer:
                _idx = int(c.split('[')[1].split(']')[0])
                if multiplier is not None:
                    _c_data = [multiplier*v for v in _data[idx][:-1]]
                else:
                    _c_data = _data[idx][:-1]

                _deltaPlus_base = cgmMath.list_add(_l_deltaBaseLine[_idx], _c_data)
                #log.info(_str_funcName + c)
                mc.xform(c, t =_deltaPlus_base, os = True, a=True)
                #mc.xform(c, t = [-v for v in _data[idx][:-1]], r = True, os = True)		
                idx +=1   
        return _dup	






        return
        #Validate
        _d_targetsData = self.get_targetWeightsDict()
        _l_indices = self.get_indices()	
        _sel = mc.ls(sl=True)
        _index = False
        _currentWeight = False
        _baseObject = self.get_baseObjects()[0]

        if targetShape is None:
            if not _sel:
                raise ValueError,"cgmBlendshape.bsShape_replace: must have an index or target shape"
            targetShape = _sel[0]

        if shapeToReplace is None:
            try:shapeToReplace = _sel[1]
            except:
                raise ValueError,"cgmBlendshape.bsShape_replace: must have an index or shapeToReplace specified"
        else:
            _type = type(shapeToReplace)
            if _type is int:
                _index = shapeToReplace
                shapeToReplace = self.bsShape_get(shapeToReplace, weight)['dag']
            elif self.is_bsShape(shapeToReplace):
                _buffer = self.bsShape_index(shapeToReplace)
                _index = _buffer[0][0]
                _currentWeight = _buffer[0][1]
                #weight?
            else:
                raise ValueError,"cgmBlendshape.bsShape_replace: invalid shapeToReplace ({0})".format(shapeToReplace)




        _d_new_arg = copy.copy(_d_targetsData[_index])
        #for k in _d_new_arg.keys():
        #    if k == weight:
        _d_new_arg[weight] = {'shape':targetShape}

        log.debug("currentArgs: {0}".format(_d_targetsData[_index]))
        log.debug("newArgs: {0}".format(_d_new_arg))

        #Get the data for rebuilding
        plug_in = attributes.returnDriverAttribute("{0}.{1}".format(self.mNode, self.get_weight_attrs()[_index]))

        #Remove the existing targets on that index
        for w in _d_targetsData[_index]:
            self.bsShape_remove(_d_targetsData[_index][w]['shape'], index = _index, weight = w)

        #Need to rebuild in 1.0 order
        l_keys = _d_new_arg.keys()
        l_keys.sort()
        l_keys.reverse()

        for w in l_keys:
            self.bsShape_add(_d_new_arg[w]['shape'], index = _index, weight = w)   

        if plug_in:
            attributes.doConnectAttr(plug_in, "{0}.{1}".format(self.mNode, self.get_weight_attrs()[_index]))

        log.debug(cgmGeneral._str_subLine)	
        log.debug("cgmBlendshape.bsShape_replace...")
        log.debug("index: {0}".format(_index))	
        log.debug("baseObject: {0}".format(_baseObject))	
        log.debug("targetShape: {0}".format(targetShape))
        log.debug("weight: {0}".format(weight))		
        log.debug("shapeToReplace: {0}".format(shapeToReplace))
        log.debug("currentWeight: {0}".format(_currentWeight))	
        log.debug("driverPlug: {0}".format(plug_in))	
        log.debug(cgmGeneral._str_subLine)
        #log.debug("currentArgs: {0}".format(_d_targetsData[_index]))
        #log.debug("newArgs: {0}".format(_d_new_arg))

        #log.debug("pre data: {0}".format(_d_targetsData[_index]))
        #log.debug("post data: {0}".format(self.get_targetWeightsDict()[_index]))	

        log.debug(cgmGeneral._str_hardBreak)	

        return [_index,weight]       
    def bsShape_getTargetArgs(self, target = None):
        """
        Get the target args for a provided target

        :parameters:
            target(str) | Node to check

        :returns
            list of shapes on node that are shapes| False
        """    	
        if target is None :
            _sel = mc.ls(sl=True)
            if not _sel:
                raise ValueError,"bsShape_getTargetArgs: No object selected and no arg passed!"
            target = _sel[0]

        target = mc.ls(target, long = True)[0]
        _result = []    
        _d_buffer = self.get_targetWeightsDict()

        log.debug("cgmBlendshape.bsShape_getTargetArgs...")
        log.debug("targetShape: {0}".format(target))	

        for i in _d_buffer.keys():
            for ii in _d_buffer[i].keys():
                #log.info(_d_buffer[i][ii])
                if target == _d_buffer[i][ii]['dag'] or target == _d_buffer[i][ii]['shape']:
                    _result.append([i, target, ii])

        return _result
    #TO DO.........................
    def bsShape_reset(self):
        raise NotImplementedError

    def bsShapes_math(self, 
                      sourceShapesAndWeights = None,
                      targetShapeOrIndex = None, targetWeight = None,
                      mode = 'add', space = 'object', resultMode = 'new',
                      multiplier = None):
        """
        Add,subract, etc a target mesh or index to another 

        :parameters:

        :returns:

        """ 
        _str_func = "{0}.bsShape_math".format(self.mNode)
        _d_modes_ = {'add':['a','+'],'subtract':['s','sub','-'],
                     'multiply':['mult','m'],
                     'average':['avg'],'difference':['d','diff'],
                     'copyTo':['transfer','push','pushTo','transferTo'],
                     'xFlip':['xf'],
                     'yFlip':['yf'],
                     'zFlip':['zf'],
                     'xOnly':['xo'],
                     'yOnly':['yo'],
                     'zOnly':['zo'],
                     'reset':['r']} 	

        __resultModes__ = {'new':['n'],'modify':['self','m','replace'],'values':['v']}
        __space__ = {'world':['w','ws'],'object':['o','os']}

        _mode = cgmValid.kw_fromDict(mode, _d_modes_, calledFrom=_str_func)
        _space = cgmValid.kw_fromDict(space, __space__, calledFrom=_str_func)
        _replaceMode = cgmValid.kw_fromDict(resultMode, __resultModes__, calledFrom=_str_func)

        _multiplier = cgmValid.valueArg(multiplier, calledFrom=_str_func)
        if not _multiplier:
            if _mode == 'blend':
                _multiplier = .5
            else:
                _multiplier = 1	

        #...Get our deltas
        _d_targetsData = self.get_targetWeightsDict()
        _l_indices = self.get_indices()	
        _sel = mc.ls(sl=True)
        _index = False
        _currentWeight = False
        _baseObject = self.get_baseObjects()[0]

        try:#>>Figure out our target...
            if targetShapeOrIndex is None:
                if not _sel:
                    raise ValueError,"{0}: must have an index or target shape".format(_str_func)
                targetShape = _sel[-1]
                _l_sourceOptions = _sel[:-1]
        except Exception,err:raise Exception,"{0}: failed to find target".format(_str_func)
        return  

        if shapeToReplace is None:
            try:shapeToReplace = _sel[1]
            except:
                raise ValueError,"{0}: must have an index or shapeToReplace specified".format(_str_func)
        else:
            _type = type(shapeToReplace)
            if _type is int:
                _index = shapeToReplace
                shapeToReplace = self.bsShape_get(shapeToReplace, weight)['dag']
            elif self.is_bsShape(shapeToReplace):
                _buffer = self.bsShape_index(shapeToReplace)
                _index = _buffer[0][0]
                _currentWeight = _buffer[0][1]
                #weight?
            else:
                raise ValueError,"{1}: invalid shapeToReplace ({0})".format(shapeToReplace,_str_func)


        log.info(cgmGeneral._str_subLine)	
        log.info("{0}...".format(_str_func))
        #log.info("sourceObj: {0}".format(sourceObj))	
        #log.info("target: {0}".format(target))	
        log.info("resultMode: {0}".format(_replaceMode))		
        log.info("mode: {0}".format(_mode))	
        log.info("space: {0}".format(_space))
        log.info("multiplier: {0}".format(_multiplier))	

        #Need...
        #>>Shape we're using to 'math' with. Either an existing shape or a new mesh
        #>>Target Shape, existing shape or 
        #>>Get our data, do the math
        #>>Result -- push to new target, push to new mesh, replace target mesh	
        #_d_buffer = self.bsShape_validateShapeArg(shapeOrIndex, weight)
        #if not _d_buffer:
            #raise ValueError, "{0} shapeOrIndex({1}) and weight ({2}) found no data.".format(_str_func,shapeOrIndex,weight)


#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
