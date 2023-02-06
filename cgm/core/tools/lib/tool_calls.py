#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>======================================================================
import logging
import importlib
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

import cgm.core.cgm_General as cgmGEN
import webbrowser
import maya.mel as mel

def FuncIterTime():
    import cgm.core.tools.funcIterTime as cgmFIT
    cgmGEN._reloadMod(cgmFIT)
    mel.eval('python "import cgm.core.tools.funcIterTime as cgmFIT;uiFIT = cgmFIT.ui()"')
    
def RandomAttr():
    import cgm.core.tools.randomizeAttribute as cgmRandAttr
    cgmGEN._reloadMod(cgmRandAttr)
    mel.eval('python "import cgm.core.tools.randomizeAttribute as cgmRandAttr;uiRANDATTR= cgmRandAttr.ui()"')

def red9( *a ):
    import Red9
    cgmGEN._reloadMod(Red9)
    Red9.start()

def attrTools( *a ):
    from cgm.core.tools import attrTools as attrTools
    cgmGEN._reloadMod(attrTools)
    attrTools.ui()

def cgmMeshTools( *a ):
    from cgm.core.tools import meshTools
    cgmGEN._reloadMod(meshTools)
    cgmMeshToolsWin = meshTools.run()
    
def mrsUI():
    try:
        import cgm.core.mrs.Builder as MRSBUILDER
        cgmGEN._reloadMod(MRSBUILDER)
        #MRSBUILDER.ui()
        MRSBUILDER.ui_get()
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
        
def mrsBlockEditor():
    import cgm.core.mrs.Builder as MRSBUILDER
    MRSBUILDER.blockEditor_get()
    
def mrsBlockCreate():
    import cgm.core.mrs.Builder as MRSBUILDER
    cgmGEN._reloadMod(MRSBUILDER)
    MRSBUILDER.ui_createBlock()
    
def mrsBlockPicker():
    import cgm.core.mrs.Builder as MRSBUILDER
    MRSBUILDER.blockPicker_get()        
    
def mrsANIMATE():
    import cgm.core.mrs.Animate as MRSANIMATE
    cgmGEN._reloadMod(MRSANIMATE)
    MRSANIMATE.ui()
    
def mrsPOSER():
    import cgm.core.mrs.PoseManager as MRSPOSER
    cgmGEN._reloadMod(MRSPOSER)
    MRSPOSER.ui()
    
def cgmSnapTools():
    try:
        import cgm.core.tools.snapTools as SNAP
        cgmGEN._reloadMod(SNAP)
        SNAP.ui()
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def mocapBakeTool():
    try:
        import cgm.core.tools.mocapBakeTools as MOCAPBAKE
        cgmGEN._reloadMod(MOCAPBAKE)
        MOCAPBAKE.ui()
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def cgmUpdateTool():
    try:
        import cgm.core.tools.updateTool as CGMUPDATE
        cgmGEN._reloadMod(CGMUPDATE)
        CGMUPDATE.ui()
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def cgmUpdateTool_lastBranch():
    try:
        import cgm.core.tools.updateTool as CGMUPDATE
        cgmGEN._reloadMod(CGMUPDATE)
        CGMUPDATE.checkBranch()
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def locinator():
    from cgm.core.tools import locinator as LOCINATOR
    cgmGEN._reloadMod(LOCINATOR)
    LOCINATOR.ui()

def dynParentTool( *a ):
    from cgm.core.tools import dynParentTool as DYNPARENTTOOL
    cgmGEN._reloadMod(DYNPARENTTOOL)
    DYNPARENTTOOL.ui()
    
def setTools():
    import cgm.core.tools.setTools as SETTOOLS
    cgmGEN._reloadMod(SETTOOLS)
    SETTOOLS.ui()
    
def transformTools():
    import cgm.core.tools.transformTools as TT
    cgmGEN._reloadMod(TT)
    TT.ui()
    
def jointTools():
    import cgm.core.tools.jointTools as JOINTTOOLS
    cgmGEN._reloadMod(JOINTTOOLS)
    JOINTTOOLS.ui()

def ngskin():
    try:
        from ngSkinTools.ui.mainwindow import MainWindow
        MainWindow.open()    
    except Exception as err:
        webbrowser.open("http://www.ngskintools.com/")
        raise ValueError("Failed to load. Go get it. | {0}".format(err))

def SVGator():
    import cgm.core.tools.SVGator as SVGATOR
    cgmGEN._reloadMod(SVGATOR)
    SVGATOR.ui()
    
    
def CGMDATui():
    import cgm.core.cgm_Dat as CGMDAT
    cgmGEN._reloadMod(CGMDAT)
    CGMDAT.ui()
    
def BLOCKDATui():
    import cgm.core.mrs.MRSDat as MRSDAT
    cgmGEN._reloadMod(MRSDAT)
    MRSDAT.uiBlockDat()
    
def CONFIGDATui():
    import cgm.core.mrs.MRSDat as MRSDAT
    cgmGEN._reloadMod(MRSDAT)
    MRSDAT.uiBlockConfigDat()
    
def SHAPEDATui():
    import cgm.core.mrs.MRSDat as MRSDAT
    cgmGEN._reloadMod(MRSDAT)
    MRSDAT.uiShapeDat()
    
def mrsShots():
    try:
        import cgm.core.mrs.Shots as SHOTS
        cgmGEN._reloadMod(SHOTS)
        x = SHOTS.ShotUI()
    except Exception as err:
        cgmGEN.cgmException(Exception,err)

def mrsScene():
    try:
        import cgm.core.mrs.Scene as SCENE
        cgmGEN._reloadMod(SCENE)
        #mel.eval('python "import cgm.core.mrs.Scene as SCENE;cgmSceneUI = SCENE.ui()"')
        SCENE.ui()
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
        
def mrsSceneLegacy():
    import cgm.core.mrs.SceneOld as SCENELEGACY
    cgmGEN._reloadMod(SCENELEGACY)
    #mel.eval('python "import cgm.core.mrs.Scene as SCENE;cgmSceneUI = SCENE.ui()"')
    SCENELEGACY.ui()

        
def mrsShapeDat():
    import cgm.core.mrs.MRSDat as MRSDAT
    cgmGEN._reloadMod(MRSDAT)
    MRSDAT.uiShapeDat()
        
def animDraw():
    try:
        import cgm.core.tools.liveRecord as liveRecord
        cgmGEN._reloadMod(liveRecord)
        import cgm.core.tools.animDrawTool as ADT
        cgmGEN._reloadMod(ADT)
        import cgm.core.tools.animDraw as animDraw
        cgmGEN._reloadMod(animDraw)        
        mel.eval('python "import cgm.core.tools.animDrawTool as ANIMDRAW;cgmAnimDrawUI = ANIMDRAW.ui()"')
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
        
        
def animFilter():
    try:
        import cgm.core.tools.animFilterTool as ANIMFILTER
        cgmGEN._reloadMod(ANIMFILTER)
        mel.eval('python "import cgm.core.tools.animFilterTool as ANIMFILTER;cgmAnimFilterUI = ANIMFILTER.ui()"')
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
        

    #except Exception,err:
    #    log.warning("[mrsScene] failed to load. | {0}".format(err))
def cgmSimChain():
    try:
        from cgm.core.tools import dynFKTool
        cgmGEN._reloadMod(dynFKTool)
        dynFKTool.ui()
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
        

def cgmProject():
    try:
        import cgm.core.tools.Project as PROJECT
        cgmGEN._reloadMod(PROJECT)
        cgmGEN._reloadMod(PROJECT.PU)
        #x = PROJECT.ui()
        mel.eval('python "import cgm;uiProject = cgm.core.tools.Project.ui();"')
        
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
    #except Exception,err:
    #    log.warning("[cgmProject] failed to load. | {0}".format(err))
    #    raise Exception,err

def loadPuppetBox( *a ):
    from cgm.tools import puppetBox
    cgmGEN._reloadMod(puppetBox)
    cgmPuppetBoxWin = puppetBox.run()

def loadPuppetBox2( *a ):
    from cgm.tools import puppetBox2
    cgmGEN._reloadMod(puppetBox2)
    cgmPuppetBoxWin = puppetBox2.run()	

def loadCGMSimpleGUI( *a ):
    try:
        
        from cgm.core.classes import GuiFactory as uiFactory
        cgmGEN._reloadMod(uiFactory)
        uiFactory.cgmGUI()
    except Exception as err:
        cgmGEN.cgmException(Exception,err)        

def reload_cgmCore( *a ):
    try:
        import cgm.core
        cgm.core._reload()	
    except Exception as err:
        cgmGEN.cgmException(Exception,err)

def testMorpheus( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    cgmGEN._reloadMod(testCGM)
    testCGM.MorpheusBase_Test()


#Zoo stuff =====================================================================
def loadZooToolbox( *a ):
    import zooToolbox
    zooToolbox.ToolboxWindow()

def loadSkinPropagation( *a ):
    from cgm.lib.zoo.zooPyMaya import refPropagation
    refPropagation.propagateWeightChangesToModel_confirm()

def loadXferAnim( *a ):
    from cgm.lib.zoo.zooPyMaya import xferAnimUI
    xferAnimUI.XferAnimWindow()
    
    

#>>Legacy Tools =======================================================================================
def attrToolsLEGACY( *a ):
    from cgm.tools import attrTools as attrTools1
    cgmGEN._reloadMod(attrTools1)
    cgmAttrToolsWin = attrTools1.run()
    
def animToolsLEGACY( *a ):
    from cgm.tools import animTools
    cgmGEN._reloadMod(animTools)
    cgmAnimToolsWin = animTools.run()

def setToolsLEGACY( *a ):
    from cgm.tools import setTools
    cgmGEN._reloadMod(setTools)
    cgmSetToolsWin = setTools.run()	
    
    
def locinatorLEGACY( *a ):
    from cgm.tools import locinator
    cgmGEN._reloadMod(locinator)
    locinator.run()
    
def tdToolsLEGACY( *a ):
    import maya.cmds as mc
    import maya.mel as mel
    mel.eval('python("import maya.cmds as mc;")')
    from cgm.tools import tdTools
    cgmGEN._reloadMod(tdTools)
    tdTools.run()
