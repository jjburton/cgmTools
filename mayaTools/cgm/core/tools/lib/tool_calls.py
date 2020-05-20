#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

import cgm.core.cgm_General as cgmGEN
import webbrowser
import maya.mel as mel

def red9( *a ):
    import Red9
    reload(Red9)
    Red9.start()

def attrTools( *a ):
    from cgm.core.tools import attrTools as attrTools
    reload(attrTools)
    attrTools.ui()

def cgmMeshTools( *a ):
    from cgm.core.tools import meshTools
    reload(meshTools)
    cgmMeshToolsWin = meshTools.run()
    
def mrsUI():
    try:
        import cgm.core.mrs.Builder as MRSBUILDER
        reload(MRSBUILDER)
        MRSBUILDER.ui()
    except Exception,err:
        cgmGEN.cgmException(Exception,err)    
    
def mrsANIMATE():
    import cgm.core.mrs.Animate as MRSANIMATE
    reload(MRSANIMATE)
    MRSANIMATE.ui()
    
def mrsPOSER():
    import cgm.core.mrs.PoseManager as MRSPOSER
    reload(MRSPOSER)
    MRSPOSER.ui()
    
def cgmSnapTools():
    try:
        import cgm.core.tools.snapTools as SNAP
        reload(SNAP)
        SNAP.ui()
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def mocapBakeTool():
    try:
        import cgm.core.tools.mocapBakeTools as MOCAPBAKE
        reload(MOCAPBAKE)
        MOCAPBAKE.ui()
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def cgmUpdateTool():
    try:
        import cgm.core.tools.updateTool as CGMUPDATE
        reload(CGMUPDATE)
        CGMUPDATE.ui()
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
def locinator():
    from cgm.core.tools import locinator as LOCINATOR
    reload(LOCINATOR)
    LOCINATOR.ui()

def dynParentTool( *a ):
    from cgm.core.tools import dynParentTool as DYNPARENTTOOL
    reload(DYNPARENTTOOL)
    DYNPARENTTOOL.ui()
    
def setTools():
    import cgm.core.tools.setTools as SETTOOLS
    reload(SETTOOLS)
    SETTOOLS.ui()

def jointTools():
    import cgm.core.tools.jointTools as JOINTTOOLS
    reload(JOINTTOOLS)
    JOINTTOOLS.ui()

def ngskin():
    try:
        from ngSkinTools.ui.mainwindow import MainWindow
        MainWindow.open()    
    except Exception,err:
        webbrowser.open("http://www.ngskintools.com/")
        raise ValueError,"Failed to load. Go get it. | {0}".format(err)


def mrsShots():
    try:
        import cgm.core.mrs.Shots as SHOTS
        reload(SHOTS)
        x = SHOTS.ShotUI()
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

def mrsScene():
    try:
        import cgm.core.mrs.Scene as SCENE
        reload(SCENE)
        x = SCENE.ui()
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
        
    #except Exception,err:
    #    log.warning("[mrsScene] failed to load. | {0}".format(err))
def cgmSimChain():
    try:
        from cgm.core.tools import dynFKTool
        reload(dynFKTool)
        dynFKTool.ui()
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def animDraw():
    try:
        import cgm.tools.liveRecordTool as LR
        reload(LR)
        import cgm.tools.liveRecord as liveRecord
        reload(liveRecord)
        mel.eval('python "animDraw = cgm.tools.liveRecordTool.ui();"')
        
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

def cgmProject():
    try:
        import cgm.core.tools.Project as PROJECT
        reload(PROJECT)
        x = PROJECT.ui()
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
    #except Exception,err:
    #    log.warning("[cgmProject] failed to load. | {0}".format(err))
    #    raise Exception,err

def loadPuppetBox( *a ):
    from cgm.tools import puppetBox
    reload(puppetBox)
    cgmPuppetBoxWin = puppetBox.run()

def loadPuppetBox2( *a ):
    from cgm.tools import puppetBox2
    reload(puppetBox2)
    cgmPuppetBoxWin = puppetBox2.run()	

def loadCGMSimpleGUI( *a ):
    try:
        
        from cgm.core.classes import GuiFactory as uiFactory
        reload(uiFactory)
        uiFactory.cgmGUI()
    except Exception,err:
        cgmGEN.cgmException(Exception,err)        

def reload_cgmCore( *a ):
    try:
        import cgm.core
        cgm.core._reload()	
    except Exception,err:
        cgmGEN.cgmException(Exception,err)

def testMorpheus( *a ):
    from cgm.core.tests import cgmMeta_test as testCGM
    reload(testCGM)
    testCGM.MorpheusBase_Test()


#Zoo stuff =====================================================================
def loadZooToolbox( *a ):
    import zooToolbox
    zooToolbox.ToolboxWindow()

def loadSkinPropagation( *a ):
    from zooPyMaya import refPropagation
    refPropagation.propagateWeightChangesToModel_confirm()

def loadXferAnim( *a ):
    from zooPyMaya import xferAnimUI
    xferAnimUI.XferAnimWindow()
    
    

#>>Legacy Tools =======================================================================================
def attrToolsLEGACY( *a ):
    from cgm.tools import attrTools as attrTools1
    reload(attrTools1)
    cgmAttrToolsWin = attrTools1.run()
    
def animToolsLEGACY( *a ):
    from cgm.tools import animTools
    reload(animTools)
    cgmAnimToolsWin = animTools.run()

def setToolsLEGACY( *a ):
    from cgm.tools import setTools
    reload(setTools)
    cgmSetToolsWin = setTools.run()	
    
    
def locinatorLEGACY( *a ):
    from cgm.tools import locinator
    reload(locinator)
    locinator.run()
    
def tdToolsLEGACY( *a ):
    import maya.cmds as mc
    import maya.mel as mel
    mel.eval('python("import maya.cmds as mc;")')
    from cgm.tools import tdTools
    reload(tdTools)
    tdTools.run()
