import maya.cmds as mc
import os
import cgm.core.lib.hud_utils as HUD

def MakeThumbnail(filePath, dimensions=(256, 256)):
	now = mc.currentTime( q=True )
	
	defaultImageFormat = mc.getAttr("defaultRenderGlobals.imageFormat")
	mc.setAttr( "defaultRenderGlobals.imageFormat", 8)

	# turn off all HUDS
	showSettings = HUD.getHUDAttributes('show')
	hudSettings = HUD.getHUDAttributes('hud')
	HUD.hideHUDAttributes()

	playblastImage = mc.playblast( fmt='image', cf=filePath, st=now, et=now, forceOverwrite=True, fp=False, clearCache=True, viewer=True, showOrnaments=True, percent=100, widthHeight=dimensions)

	# turn HUDS back on
	HUD.restoreHUDAttributes(showSettings, hudSettings) 
	
	mc.setAttr( "defaultRenderGlobals.imageFormat", defaultImageFormat)
	
	return playblastImage
