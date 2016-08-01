from morpheusRig_v2.core import MorpheusFactory as MF
reload(MF)
m1 = cgmMeta.cgmNode('M1_customizationNetwork')
m1.mPuppet

m1.getMessageAsMeta('geo_baseHead')
mi_p_geo_head = cgmMeta.validateObjArg( m1.mPuppet.masterNull.geoGroup.getMessage('geo_baseHead'))
mi_p_geo_head.mNode
mi_asset_geo_bridgeHead = m1.getMessageAsMeta('geo_baseHead')
mi_asset_geo_bridgeHead.mNode
ml_asset_bsNodes = m1.mSimpleFaceModule.rigNull.msgList_get('bsNodes')
ml_asset_bsNodes

deformers.bakeBlendShapeNodesToTargetObject(mi_p_geo_head.mNode,mi_asset_geo_bridgeHead.mNode,[bsn.mNode for bsn in ml_asset_bsNodes],transferConnections = True)

#Resolved the baking on base
#Skin dat copying off...


MF.puppet_verifyGeoDeformation(m1)

