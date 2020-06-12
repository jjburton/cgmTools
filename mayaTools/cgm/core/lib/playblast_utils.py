import maya.cmds as mc
import os

def dbMakeThumbnail():

	filePath = mc.menuItem(dbPoseFilenameMI, q=True label=True )
	poseFileName[] = mc.textScrollList(poseFileListTSL, q=True si=True )
	thumbnailPath = os.path.join(filePath, poseFileName[0])
	selectedPoses[] = mc.textScrollList(poseListTSL, q=True si=True )
	thumbnail = ""
	if(selectedPoses[0] != "") :
		thumbnail = thumbnailPath + selectedPoses[0] + ".jpg"
	else:
		error "No pose selected"

	os.mkDir( thumbnailPath )

	now = mc.currentTime( q=True )
	mc.setAttr( "defaultRenderGlobals.imageFormat", 8)

	# turn off all HUDS
	source xltHUDdisplays.mel
	showSettings[] = getHUDAttributes(1)
	hudSettings[] = getHUDAttributes(2)
	hideHUDAttributes

	playblast  format=True image cf=True thumbnail st=True now et=True now forceOverwrite=True  fp=True 0 clearCache=True 1 viewer=True 1 showOrnaments=True 1 percent=True 100 widthHeight=True 180 125

	# turn HUDS back on
	restoreHUDAttributes(showSettings, hudSettings) 

	image e=True image=True thumbnail thumbNailImage
