"""
------------------------------------------
shared_data: cgm.core.lib.shared_data
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------
"""
l_cgmNameOrder = ['cgmDirection',
                  'cgmDirectionModifier',
                  'cgmPosition',
                  'cgmPositionModifer',
                  'cgmName',
                  'cgmNameModifier',
                  'cgmIterator',
                  'cgmTypeModifier',
                  'cgmType']

str_nameDivider = '_'

defaultTextFont = 'Arial'

d_shortNames = {'module':'part',
                'modules':'parts',
                
                ### Types
                
                'blendShapeGeo':'bsGeo',
                'object':'obj',
                
                
                ### General acgmreviations
                'left':'L' ,
                'right':'R' ,
                'center':'CTR',
                'front':'FRNT',
                'upper':'UPR',
                'lower':'LWR',
                'back':'BCK',
                'top':'TOP',
                'rear':'REAR',
                'bottom':'BTM',
                'blendShape':'bs',
                'quickSelectSet':'qss',
                'characterSet':'cs',
                'template':'tmpl',

                'controlMaster':'all',

                #Arms
                'clavicle':'clav',
                'upperArm':'uprArm',
                'lowerArm':'lwrArm',
                
                #Leg
                'upperLeg':'uprLeg',
                'lowerLeg':'lwrLeg',
                
                #Digits
                'finger1':'thumb',
                'finger2':'index',
                'finger3':'middle',
                'finger4':'ring',
                'finger5':'pinky',
                'toe1':'big',
                'toe2':'index',
                'toe3':'middle',
                'toe4':'ring',
                'toe5':'pinky',
                }
                
                
                

d_cgmTypes = {### Custom Types
              'null':'null',
              'object':'obj',
              'skinCluster':'skinNode',
              'blendShapeGeo':'bsGeo',
              'group':'grp',
              ### Controls
              'controlMaster':'placer',
              'controlAnim':'anim',
              
              ### Sets
              'quickSelectSet':'qss',
              'characterSet':'cs',
              
              ### Maya Types
              'camera':'cam',
              'transform':'group',
              'locator':'loc',
              
              
              'subdiv':'subGeo',
              'mesh':'geo',
              'nurbsCurve':'crv',
              'nurbsSurface':'surf',
              
              
              'ambientLight':'ambLt',
              'spotLight':'sptLt',
              'pointLight':'pntLt',
              
              
              'joint':'jnt',
              'skinJoint':'sknJnt',
              'rigJoint':'rigJnt',
              'ikHandle':'ikH',
              'ikEffector':'ikE',
              
              
              ###Contraints
              'orientConstraint':'orConst',
              'parentConstraint':'prntConst',
              'pointConstraint':'pntConst',
              'aimConstraint':'aimConst',
              'scaleConstraint':'scConst',
              'geometryConstraint':'geoConst',
              'normalConstraint':'normConst',
              'tangentConstraint':'tangConst',
              'poleVectorConstraint':'pvConst',
              
              
              ### Nodes
              'pointOnSurfaceInfoNode':'posInfoNode',
              'frameCacheNode':'fCacheNode',
              'plusMinusAverageNode':'pmAvNode',
              'closestPointOnSurfaceNode':'cPntOnSurfNode',
              'blendShapeNode':'bsNode',
              'multiplyDivideNode':'mdNode',
              'remapNode':'remapNode',
              'reverseNode':'revNode'}



#>>> Attributes
#==================================================================
_d_attrCategoryLists = {'transform':('translateX','translateY','translateZ',
                                     'rotateX','rotateY','rotateZ',
                                     'scaleX','scaleY','scaleZ','visibility'),
                        'joint':('rotateOrder','rotateAxisX','rotateAxisY','rotateAxisZ',
                                 'inheritsTransform','drawStyle','radius',
                                 'jointTypeX','jointTypeY','jointTypeZ',
                                 'stiffnessX','stiffnessY','stiffnessZ',
                                 'preferredAngleX','preferredAngleY','preferredAngleZ',
                                 'jointOrientX','jointOrientY','jointOrientZ','segmentScaleCompensate','showManipDefault',
                                 'displayHandle','displayLocalAxis','selectHandleX','selectHandleY','selectHandleZ'),
                        'objectDisplayAttrs':('visibility','template','lodVisibility'),
                        'curveShapeAttrs':('intermediateObject','dispCV','dispEP','dispHull','dispGeometry'),
                        'locatorShape':('localPositionX','localPositionY','localPositionZ',
                                        'localScaleX','localScaleY','localScaleZ'),
                        'overrideAttrs':('overrideEnabled','overrideDisplayType',
                                         'overrideLevelOfDetail','overrideShading',
                                         'overrideTexturing','overridePlayback',
                                         'overrideVisibility','overrideColor')}
_d_attrTypes_toShort = {'matrix':'mtrx','float':'fl','double':'d','double3':'d3','string':'str','long':'int','float3':'fl3',
                        'message':'msg','doubleLinear':'dl','doubleAngle':'da','TdataCompound':'Tdata'}

#>>> Naming
#==================================================================
_d_node_to_suffix = {'follicle':'foll','curveInfo':'crvInfo','condition':'condNode','multiplyDivide':'mdNode','pointOnSurfaceInfo':'posInfoNode','closestPointOnSurface':'cPntOnSurfNode','closestPointOnMesh':'cPntOnMeshNode','plusMinusAverage':'pmAvNode','frameCache':'fCacheNode','surfaceInfo':'surfInfo'}


#>>> Positional data
#===================================================================
_d_rotateOrder_to_index = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
_d_rotateOrder_from_index = {0: 'xyz', 1: 'yzx', 2: 'zxy', 3: 'xzy', 4: 'yxz', 5: 'zyx', 6: 'none'}

_d_pivotArgs = {'rp':['rp','r','rotate','rotatePivot','pivot'],
                'sp':['scale','s','scalePivot'],
                'local':['l','translate'],
                'boundingBox':['bb','bbCenter'],
                'axisBox':['ab'],
                'closestPoint':['cpos','closest','closestPoint']}
_d_spaceArgs = {'object':['os','objectSpace','o'],'world':['w','worldSpace','ws'],'local':['l','translate']}



#>>> Axis data
#===================================================================
_d_axisToJointOrient = {'x+':{'y+':[0,-90,0],
                              'z+':[-90,-90,0],
                              'y-':[180,-90,0],
                              'z-':[90,-90,0]},
                        'x-':{'y+':[0,90,0],
                              'z+':[0,90,90],
                              'y-':[90,90,-90],
                              'z-':[0,90,-90]},
                        'y+':{'x+':[90,0,90],
                              'z+':[90,0,180],
                              'x-':[90,0,-90],
                              'z-':[90,0,0]},
                        'y-':{'x+':[-90,0,90],
                              'z+':[-90,0,0],
                              'x-':[-90,0,-90],
                              'z-':[-90,0,180]},
                        'z+':{'x+':[0,0,90],
                              'y+':[0,0,0],
                              'x-':[0,0,-90],
                              'y-':[0,0,180]},
                        'z-':{'x+':[0,180,-90],
                              'y+':[0,180,0],
                              'x-':[180,0,-90],
                              'y-':[180,0,0]},
                        }

_d_axis_string_to_vector = {'x+':[1,0,0],
                            'x-':[-1,0,0],
                            'y+':[0,1,0],
                            'y-':[0,-1,0],
                            'z+':[0,0,1],
                            'z-':[0,0,-1]}

_d_axis_vector_to_string = {'[1,0,0]':'x+',
                           '[-1,0,0]':'x-',
                           '[0,1,0]':'y+',
                           '[0,-1,0]':'y-',
                           '[0,0,1]':'z+',
                           '[0,0,-1]':'z-'}

_l_axis_by_string = ['x+','y+','z+','x-','y-','z-'] #Used for several menus and what not
_d_short_axis_to_long = {'x':'x+',
                         'y':'y+',
                         'z':'z+'}

d_vectorToString = {
    '[1, 0, 0]' :'x+',
    '[-1, 0, 0]':'x-',
    '[0, 1, 0]' :'y+',
    '[0,-1, 0]':'y-',
    '[0, 0, 1]' :'z+',
    '[0, 0,-1]':'z-'
}

d_tupleToString = {
    '(1, 0, 0)':'x+',
    '(-1, 0, 0)':'x-',
    '(0, 1, 0)':'y+',
    '(0,-1, 0)':'y-',
    '(0, 0, 1)':'z+',
    '(0, 0,-1)':'z-'
}

d_shortAxisToLong = {
    'x':'x+',
    'y':'y+',
    'z':'z+'
}


#>>> Colors
#===================================================================
_d_colors_to_index = {'black':1,'grayDark':2,'grayLight':3,'redDark':4,
                      'blueDark':5,'blueBright':6,'greenDark':7,'violetDark':8,
                      'violetBright':9,'brownReg':10,'brownDark':11,
                      'orangeDark':12,'redBright':13,'greenBright':14,'blueDull':15,
                      'white':16,'yellowBright':17,'blueSky':18,'teal':19,
                      'pink':20,'peach':21,'yellow':22,'greenBlue':23,'tan':24,
                      'olive':25,'greenYellow':26,'greenBlue':27,'blueGray':28,
                      'blueGrayDark':29,'purple':30,'purpleBrown':31}

_d_colors_to_RGB = {'red':[1,0,0],'redDark':[.5,0,0],'redLight':[1,.2,.2],'redBlack':[.25,0,0],'redWhite':[1,.5,.5],
                    'orange':[1,.27,0],'orangeDark':[.65,.1,0],'orangeLight':[1,.5,.2],'orangeBlack':[.2,.02,0],'orangeWhite':[1,.6,.1],                    
                    'yellow':[1,1,0],'yellowDark':[.882,.815,.121],'yellowLight':[1,.8,.1],'yellowBlack':[.25,.25,0],'yellowWhite':[1,1,.7],
                    'green':[0,.4,0],'greenDark':[0,.25,0],'greenLight':[0,1,0],'greenBlack':[0,.129,0],'greenWhite':[.667,1,.667],                                        
                    'blue':[0,0,1],'blueDark':[0,.05,.4],'blueLight':[.06,.275,1],'blueBlack':[0,0,.25],'blueWhite':[.634,.79,.98],
                    'purple':[.22,0,.44],'purpleDark':[.22,0,.44],'purpleLight':[.5,0,1],'purpleBlack':[.05,0,.1],'purpleWhite':[.8,.6,1],
                    'teal':[0,1,.5],'blueSky':[.392,.789,1.0],'blueSkyDark':[0.0,.535,1.0],'blueSkyLight':[0.0,.535,1.0],
                    'white':[1,1,1],'black':[0,0,0],
                    'gray':[.5,.5,.5],'gray25':[.25,.25,.25],'gray75':[.75,.75,.75],
                    }

_d_colorSetsRGB = {'red':['White','Light','Dark','Black'],
                   'orange':['White','Light','Dark','Black'],
                   'yellow':['White','Light','Dark','Black'],
                   'green':['White','Light','Dark','Black'],
                   'blue':['White','Light','Dark','Black'],
                   'teal':[],
                   'white':[],
                   'black':[],
                   'gray':['25','75']}

_d_colorsByIndexSets = {'red':['pink','redBright','redDark'],
                        'orange':['orangeDark','peach'],
                        'yellow':['yellow','yellowBright'],
                        'blue':['blueBright','blueDark','blueDull','blueGray','blueGrayDark','blueSky','teal'],
                        'green':['greenBlue','greenBright','greenDark','greenYellow','olive'],
                        'purple':['purple','purpleBrown','violetBright','violetDark'],
                        'brown':['brownDark','brownReg','tan','purpleBrown'],
                        'b&w':['black','white','grayDark','grayLight']}


#We have our main dicts which use rgb and a corresponding setup for old stuff...
_d_side_colors = {'left':{'main':'blue',
                          'sub':'blueWhite',
                          'aux':'blueDark'},
                  'right':{'main':'red',
                           'sub':'redWhite',
                           'aux':'redDark'},
                  'center':{'main':'yellow',
                            'sub':'yellowWhite',
                            'aux':'yellowDark'}}
_d_side_colors_index = {'left':{'main':'blueBright',
                                'sub':'blueSky',
                                'aux':'blueDark'},
                        'right':{'main':'redBright',
                                 'sub':'pink',
                                 'aux':'redDark'},
                        'center':{'main':'yellow',
                                  'sub':'yellowBright',
                                  'aux':'peach'}}

#>>> Gui
#===================================================================
_d_gui_state_colors = {'normal':[1,1,1],
                       'ready':[ 0.166262 ,0.388495 , 0.022797],
                       'keyed':[0.870588, 0.447059, 0.478431],
                       'locked':[0.360784, 0.407843, 0.454902],
                       'connected':[0.945098, 0.945098, 0.647059],
                       'reserved':[0.411765 , 0.411765 , 0.411765],
                       'semiLocked':[ 0.89, 0.89, 0.89],
                       'help':[0.8, 0.8, 0.8],
                       'warning':[0.837, 0.399528, 0.01674],
                       'error':[1, 0.0470588, 0.0677366],
                       'black':[0,0,0]}

_d_gui_direction_colors = {'center':[0.971679, 1, 0],
                           'centerSub':[0.972, 1, 0.726],
                           'left':[0.305882 ,0.814528, 1],
                           'right':[0.976471 ,0.355012, 0.310173]}

    
#>>>Object Sets
#==================================================================
objectSetTypes = {'animation':'animSet',
                  'layout':'layoutSet',
                  'modeling':'modelingSet',
                  'td':'tdSet',
                  'fx':'fxSet',
                  'lighting':'lightingSet'}


#>>>Option vars
#=================================================================
l_resetModes = 'all','transforms','keyable'
