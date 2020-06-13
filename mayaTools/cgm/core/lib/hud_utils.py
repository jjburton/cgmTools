import maya.cmds as mc
import cgm.core.lib.camera_utils as CAM

def getHUDAttributes(mode):
	cameraShape = mc.listRelatives(CAM.getCurrentCamera(), shapes=True)[0]
	panelName = CAM.getCurrentPanel()
	huds = mc.headsUpDisplay( lh=True )
	hudSettings = {}
	showSettings = {}

	#store vieport settings
	showSettings['nc'] = mc.modelEditor( panelName, q=True, nc=True )
	showSettings['ns'] = mc.modelEditor( panelName, q=True, ns=True )
	showSettings['pm'] = mc.modelEditor( panelName, q=True, pm=True )
	showSettings['sds'] = mc.modelEditor( panelName, q=True, sds=True )
	showSettings['pl'] = mc.modelEditor( panelName, q=True, pl=True )
	showSettings['lt'] = mc.modelEditor( panelName, q=True, lt=True )
	showSettings['ca'] = mc.modelEditor( panelName, q=True, ca=True )
	showSettings['cv'] = mc.modelEditor( panelName, q=True, cv=True )
	showSettings['gr'] = mc.modelEditor( panelName, q=True, gr=True )
	showSettings['hu'] = mc.modelEditor( panelName, q=True, hu=True )
	showSettings['j'] = mc.modelEditor( panelName, q=True, j=True )
	showSettings['ikh'] = mc.modelEditor( panelName, q=True, ikh=True )
	showSettings['df'] = mc.modelEditor( panelName, q=True, df=True )
	showSettings['dy'] = mc.modelEditor( panelName, q=True, dy=True )
	showSettings['fl'] = mc.modelEditor( panelName, q=True, fl=True )
	showSettings['hs'] = mc.modelEditor( panelName, q=True, hs=True )
	showSettings['fo'] = mc.modelEditor( panelName, q=True, fo=True )
	showSettings['ncl'] = mc.modelEditor( panelName, q=True, ncl=True )
	showSettings['nr'] = mc.modelEditor( panelName, q=True, nr=True )
	showSettings['dc'] = mc.modelEditor( panelName, q=True, dc=True )
	showSettings['lc'] = mc.modelEditor( panelName, q=True, lc=True )
	showSettings['manipulators'] = mc.modelEditor( panelName, q=True, manipulators=True )
	showSettings['dim'] = mc.modelEditor( panelName, q=True, dim=True )
	showSettings['ha'] = mc.modelEditor( panelName, q=True, ha=True )
	showSettings['pv'] = mc.modelEditor( panelName, q=True, pv=True )
	showSettings['tx'] = mc.modelEditor( panelName, q=True, tx=True )
	showSettings['strokes'] = mc.modelEditor( panelName, q=True, strokes=True )
	#showSettings['alo'] = mc.modelEditor( panelName, q=True, alo=True )


	showSettings['displayFilmGate'] = mc.getAttr("{0}.displayFilmGate".format(cameraShape) )
	showSettings['displayResolution'] = mc.getAttr("{0}.displayResolution".format(cameraShape) )
	showSettings['displayFieldChart'] = mc.getAttr("{0}.displayFieldChart".format(cameraShape) )
	showSettings['displaySafeAction'] = mc.getAttr("{0}.displaySafeAction".format(cameraShape) )
	showSettings['displaySafeTitle'] = mc.getAttr("{0}.displaySafeTitle".format(cameraShape) )
	showSettings['displayFilmPivot'] = mc.getAttr("{0}.displayFilmPivot".format(cameraShape) )
	showSettings['displayFilmOrigin'] = mc.getAttr("{0}.displayFilmOrigin".format(cameraShape) )


	for hud in huds:	
		hudSettings[hud] = mc.headsUpDisplay( hud, q=True, vis=True )
	
	if mode == 'show':
		return showSettings;
	elif mode == 'hud':
		return hudSettings;


def hideHUDAttributes():
	cameraShape = mc.listRelatives(CAM.getCurrentCamera(), shapes=True)[0]
	panelName = CAM.getCurrentPanel()
	huds = mc.headsUpDisplay( lh=True)

	#turn off the camera gates
	mc.setAttr("{0}.displayFilmGate".format(cameraShape), 0)
	mc.setAttr("{0}.displayResolution".format(cameraShape), 0)
	mc.setAttr("{0}.displayFieldChart".format(cameraShape), 0)
	mc.setAttr("{0}.displaySafeAction".format(cameraShape), 0)
	mc.setAttr("{0}.displaySafeTitle".format(cameraShape), 0)
	mc.setAttr("{0}.displayFilmPivot".format(cameraShape), 0)
	mc.setAttr("{0}.displayFilmOrigin".format(cameraShape), 0)

	#turn off everything but surfaces in the viewport
	mc.modelEditor( panelName, edit = True,
					nc = 0,
					ns = 1,
					pm = 1,
					sds = 1,
					pl = 0,
					lt = 0,
					ca = 0,
					cv = 0,
					gr = 0,
					hu = 0,
					j = 0,
					ikh = 0,
					df = 0,
					dy = 0,
					fl = 0,
					hs = 0,
					fo = 0,
					ncl = 0,
					nr = 0,
					dc = 0,
					lc = 0,
					manipulators = 0,
					dim = 0,
					ha = 0,
					pv = 0,
					tx = 0,
					strokes = 0 )

	for hud in huds:	
		mc.headsUpDisplay( hud, edit=True, vis=False )

def restoreHUDAttributes(showSettings, hudSettings):
	cameraShape = mc.listRelatives(CAM.getCurrentCamera(), shapes=True)[0]
	panelName = CAM.getCurrentPanel()
	huds = mc.headsUpDisplay( lh=True)

	#restore HUD values
	for i, hud in enumerate(huds):
		mc.headsUpDisplay( hud, edit=True, vis=hudSettings[hud])

	#restore viewport settings
	mc.modelEditor( panelName, edit=True,
			nc = showSettings['nc'],
			ns = showSettings['ns'],
			pm = showSettings['pm'],
			sds = showSettings['sds'],
			pl = showSettings['pl'],
			lt = showSettings['lt'],
			ca = showSettings['ca'],
			cv = showSettings['cv'],
			gr = showSettings['gr'],
			hu = showSettings['hu'],
			j = showSettings['j'],
			ikh = showSettings['ikh'],
			df = showSettings['df'],
			dy = showSettings['dy'],
			fl = showSettings['fl'],
			hs = showSettings['hs'],
			fo = showSettings['fo'],
			ncl = showSettings['ncl'],
			nr = showSettings['nr'],
			dc = showSettings['dc'],
			lc = showSettings['lc'],
			manipulators = showSettings['manipulators'],
			dim = showSettings['dim'],
			ha = showSettings['ha'],
			pv = showSettings['pv'],
			tx = showSettings['tx'],
			strokes = showSettings['strokes'])
			#alo = showSettings['alo']

	#restore camera gates
	mc.setAttr("{0}.displayFilmGate".format(cameraShape), showSettings['displayFilmGate'])
	mc.setAttr("{0}.displayResolution".format(cameraShape), showSettings['displayResolution'])
	mc.setAttr("{0}.displayFieldChart".format(cameraShape), showSettings['displayFieldChart'])
	mc.setAttr("{0}.displaySafeAction".format(cameraShape), showSettings['displaySafeAction'])
	mc.setAttr("{0}.displaySafeTitle".format(cameraShape), showSettings['displaySafeTitle'])
	mc.setAttr("{0}.displayFilmPivot".format(cameraShape), showSettings['displayFilmPivot'])
	mc.setAttr("{0}.displayFilmOrigin".format(cameraShape), showSettings['displayFilmOrigin'])
	mc.setAttr("{0}.overscan".format(cameraShape), 1.3)