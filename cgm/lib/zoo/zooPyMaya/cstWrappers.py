

'''
these are the optional args and their default values for the keyed rig primitive
build functions
'''
PRIM_OPTIONS = { 'zooBuildControl': {},
                 'zooCSTBuildPrimBasicSpine': {},
                 #'parents': tuple(),
                 #'hips': '',
                 #'scale': 1.0,
                 #'spaceswitching': True,
                 #'colour': 'lightblue 0.65',
                 #'buildhips': True },
                 'zooCSTBuildPrimHead': {},
                 #'parents': tuple(),
                 #'headType': 'skingeometry',
                 #'neckType': 'pin',
                 #'colour': 'blue 0.92'
                 #'scale': 1.0,
                 #'orient': True,
                 #'spaceswitching': True,
                 #'pickwalking': True,
                 #'buildNeck': True,
                 #'neckCount': True },
                 'zooCSTBuildPrimArm': {},
                 #'parents': tuple(),
                 #'scale': 1.0,
                 #'buildclav': True,
                 #'spaceswitching': True,
                 #'pickwalking': True,
                 #'allPurpose': True,
                 #'stretch': False },
                 'zooCSTBuildPrimLeg': { #'parents': tuple(),
                                         #'ikType': 'skingeometry',
                                         #'allPurpose': True,
                                         #'scale': 1.0,
                                         #'spaceswitching': True,
                                         #'pickwalking': True,
                                         'stretch': False },
                 'zooCSTBuildPrimHand': { 'names': ("index", "mid", "ring", "pinky", "thumb"),
                                          #'axes': ("#", "#", "#", "#", "#"),
                                          #'colour': 'orange 0.65',
                                          #'maxSlider': 90,
                                          #'minSlider': -90,
                                          #'maxFingerRot': 90,
                                          #'minFingerRot': -90,
                                          #'scale': 1.0,
                                          'taper': 1.0,
                                          #'pickwalking': True,
                                          'num': 0,
                                          #'invert': True,
                                          'sliders': True,
                                          'triggers': True,
                                          'stretch': False } }


#end
