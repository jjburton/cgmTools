'''
	Batch File Maker
	0.2.2
	
	Copyright (c) 2010 Bohdon Sayre
	All Rights Reserved.
	bsayre@c.ringling.edu
	
	Description:
		Generates batch files easily for command line rendering with Maya.
	
	Instructions:
		>>> import boBatchFileMaker
		>>> boBatchFileMaker.doIt()
    
	Version 0.2.2:
		> Rough 2011 compatibility
		> Render Settings display maintained between window sessions
		> File List maintained between window sessions
		> Right click menu for adding/removing batch file and render settings options
    
    Feel free to email me with any bugs, comments, or requests!
'''

import maya.cmds as cmds
import maya.mel as mel
import os, re, glob


def doIt():
    win = BatchFileMakerWindow()
    win.show()
    del win

def pyError( errorString ):
	""" print an error message """
	import maya.mel as mel
	try: 
		mel.eval(r'error "%s"' % errorString)
	except: 
		pass
def pyWarning( warningString ):
	""" print a warning message """
	import maya.mel as mel
	try: 
		mel.eval(r'warning "%s"' % warningString)
	except: 
		pass

def getMAFrameRange( maFile ):
	#check ext
	if not os.path.exists( maFile ):
		print 'file not found: %s' % maFile
		return
	root, ext = os.path.splitext( maFile )
	if ext != '.ma':
		print 'filetype is not mayaAscii: %s' % maFile
		return
	
	startFrame, endFrame = None, None
	
	fsock = open( maFile , 'r')
	try:
		lines =  fsock.readlines()
		for line in lines:
			if re.search('setAttr ".fs"', line):
				split = line.split(' ')
				try:
					startFrame = int(re.match('[0-9]*', split[2]).group())
				except:
					pass
			if re.search('setAttr ".ef"', line):
				split = line.split(' ')
				try:
					endFrame = int(re.match('[0-9]*', split[2]).group())
				except:
					pass
	except:
		pass
	finally:
		fsock.close()
	
	return [startFrame, endFrame]

class BatchFileMakerError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
	

class BatchFileMakerWindow():
	
	_name = 'bbfmWin'
	_title = 'Batch File Maker 0.2.1'
	
	#GUI element names
	_mainForm = 'bbfmWin_MainForm'
	_winWidth = 640
	_winHeight = 600
	_frameHeights = 308
	_fl_form = 'bbfmWin_FileListForm'
	_fl_list = 'bbfmWin_FileList'
	_fl_addBtn = 'bbfmWin_AddFileBtn'
	_fl_remBtn = 'bbfmWin_RemoveFileBtn'
	_fl_clearBtn = 'bbfmWin_ClearListBtn'
	_fl_loadBtn = 'bbfmWin_LoadFolderBtn'
	_rs_centerLine = -32
	_rs_frame = 'bbfmWin_RenderSettingsFrame'
	_rs_form = 'bbfmWin_RenderSettingsForm'
	_rs_popup = 'bbfmWin_RenderSettingsPopup'
	_rs_mm_range = 'bbfmWin_RSMM_FrameRangeItem'
	_rs_mm_pad = 'bbfmWin_RSMM_PaddingItem'
	_rs_mm_res = 'bbfmWin_RSMM_ResolutionItem'
	_rs_mm_fnc = 'bbfmWin_RSMM_FileNameFormatItem'
	_rs_mm_of = 'bbfmWin_RSMM_OutputFormatItem'
	_rs_mm_r = 'bbfmWin_RSMM_RendererItem'
	_rs_mm_pd = 'bbfmWin_RSMM_ProjectItem'
	_rs_mm_rd = 'bbfmWin_RSMM_RenderDirectoryItem'
	_rs_noOptsText = 'bbfmWin_RenderSettingsNoOptionsText'
	_rs_rangeText1 = 'bbfmWin_FrameRangeText1'
	_rs_start = 'bbfmWin_FrameRangeStartField'
	_rs_rangeText2 = 'bbfmWin_FrameRangeText2'
	_rs_end = 'bbfmWin_FrameRangeEndField'
	_rs_getRangeText = 'bbfmWin_GetFrameRangeText'
	_rs_getRangeBtn = 'bbfmWin_GetFrameRangeBtn'
	_rs_padText = 'bbfmWin_PaddingText'
	_rs_pad = 'bbfmWin_PaddingField'
	_rs_resText = 'bbfmWin_ResText'
	_rs_resW = 'bbfmWin_ResWidthField'
	_rs_resH = 'bbfmWin_ResHeightField'
	_rs_fncText = 'bbfmWin_FileNamingText'
	_rs_fncOpt = 'bbfmWin_FileNamingOption'
	_rs_ofText = 'bbfmWin_OutputFormatText'
	_rs_ofOpt = 'bbfmWin_OutputFormatOption'
	_rs_pdText = 'bbfmWin_ProjectText'
	_rs_pdField = 'bbfmWin_ProjectField'
	_rs_pdBtn = 'bbfmWin_ProjectBtn'
	_rs_rdText = 'bbfmWin_RenderDirectoryText'
	_rs_rdField = 'bbfmWin_RenderDirectoryField'
	_rs_rdBtn = 'bbfmWin_RenderDirectoryBtn'
	_rs_rText = 'bbfnWin_RendererText'
	_rs_rOpt = 'bbfmWin_RendererOption'
	_bfs_centerLine = -32
	_bfs_frame = 'bbfmWin_BatchFileSettingsFrame'
	_bfs_form = 'bbfmWin_BatchFileSettingsForm'
	_bfs_popup = 'bbfmWin_BatchFileSettingsPopup'
	_bfs_nameText = 'bbfmWin_NamingConventionText'
	_bfs_prefixText = 'bbfmWin_Naming_PrefixText'
	_bfs_prefixField = 'bbfmWin_Naming_PrefixField'
	_bfs_sceneCheck = 'bbfmWin_Naming_SceneNameCheck'
	_bfs_rangeCheck = 'bbfmWin_Naming_FrameRangeCheck'
	_bfs_numberedCheck = 'bbfmWin_Naming_NumberedCheck'
	_bfs_previewText = 'bbfmWin_Naming_previewText'
	_bfs_sep1 = 'bbfmWin_RS_Sep1'
	_bfs_divText = 'bbfmWin_FrameRangeDivisionsText'
	_bfs_divField = 'bbfmWin_FrameRangeDivisionsField'
	_bfs_divText2 = 'bbfmWin_FrameRangeDivisionsText2'
	_bfs_sep2 = 'bbfmWin_RS_Sep2'
	_bfs_saveText = 'bbfmWin_SaveLocationText'
	_bfs_saveField = 'bbfmWin_SaveLocationField'
	_bfs_saveBtn = 'bbfmWin_SaveLocationBtn'
	
	_makeBtn = 'bbfmWin_MakeBatchFilesBtn'
	
	mel.eval('global string $bbfmWin_fileList[];')
	mel.eval('global int $bbfmWin_renderSettingsCheck[];')
	mel.eval('global int $bbfmWin_renderSettingsInts[];')
	mel.eval('global string $bbfmWin_renderSettingsStrings[];')
	
	def sendToMel(self, value, var):
		'''Sends a python variable to mel'''
		cmd = '$%s = %s' % (var, value)
		mel.eval(cmd)
		
	def getFromMel(self, var, tempVar='temp'):
		'''Returns the value of a mel veriable'''
		cmd = '$%s = $%s;' % (tempVar, var)
		return mel.eval(cmd)
	
	def show(self):
		if cmds.window(self._name, exists=True):
			cmds.deleteUI(self._name)
		
		cmds.window(self._name, s=True, mb=True, rtf=False, t=self._title)
		
		if cmds.menu(l='Edit'):
			cmds.menuItem(l='Reset All Settings', c=self.resetSettings)
		if cmds.menu(l='Help'):
			cmds.menuItem(l='Help on Batch File Maker', en=False)
		
		if cmds.formLayout(self._mainForm, nd=100):
			#file list form
			if cmds.formLayout(self._fl_form, nd=100):
				fileList = self.getFromMel('bbfmWin_fileList', 'tempArray')
				cmds.textScrollList(self._fl_list, ams=True, sc=self.fl_listSelectCommand, append=fileList)
				cmds.button(self._fl_addBtn, l='Add Files...', c=self.fl_addFiles)
				cmds.button(self._fl_loadBtn, l='Add Folder...', c=self.fl_addFolder)
				cmds.button(self._fl_remBtn, l='Remove Selected Files', c=self.fl_remSelFiles)
				cmds.button(self._fl_clearBtn, l='Clear List', c=self.fl_clearFiles)
				cmds.setParent(self._mainForm)
				del fileList
			cmds.formLayout(self._fl_form, e=True, af=[(self._fl_list, 'left', 0), (self._fl_list, 'right', 0), (self._fl_list, 'top', 0)], ac=[(self._fl_list, 'bottom', 2, self._fl_addBtn)])
			cmds.formLayout(self._fl_form, e=True, af=[(self._fl_addBtn, 'bottom', 8), (self._fl_loadBtn, 'bottom', 8), (self._fl_remBtn, 'bottom', 8), (self._fl_clearBtn, 'bottom', 8)])
			cmds.formLayout(self._fl_form, e=True, ap=[(self._fl_addBtn, 'left', 4, 0), (self._fl_addBtn, 'right', 2, 25)])
			cmds.formLayout(self._fl_form, e=True, ap=[(self._fl_loadBtn, 'left', 4, 25), (self._fl_loadBtn, 'right', 2, 50)])
			cmds.formLayout(self._fl_form, e=True, ap=[(self._fl_remBtn, 'left', 4, 50), (self._fl_remBtn, 'right', 2, 75)])
			cmds.formLayout(self._fl_form, e=True, ap=[(self._fl_clearBtn, 'left', 4, 75), (self._fl_clearBtn, 'right', 2, 100)])
			
			#render settings frame/form
			if cmds.frameLayout(self._rs_frame, l='Render Settings', bs='etchedOut', li=10, height=self._frameHeights):
				if cmds.popupMenu(self._rs_popup, mm=True):
					checkList = self.getFromMel('bbfmWin_renderSettingsCheck', 'tempIntArray')
					if len(checkList) != 8:
						checkList = [0, 0, 0, 0, 0, 0, 0, 0]
					cmds.menuItem(self._rs_mm_range, l='Frame Range', cb=checkList[0], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_pad, l='Padding', cb=checkList[1], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_res, l='Resolution', cb=checkList[2], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_fnc, l='File Naming Format', cb=checkList[3], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_of, l='Output Format', cb=checkList[4], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_r, l='Renderer', cb=checkList[5], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_pd, l='Project', cb=checkList[6], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(self._rs_mm_rd, l='Render Directory', cb=checkList[7], c=self.rs_updateRenderSettingsDisplay)
					cmds.menuItem(d=True)
					cmds.menuItem(l='Add All', c=self.rs_addRenderSettingsAll)
					cmds.menuItem(l='Remove All', c=self.rs_removeRenderSettingsAll)
					del checkList
				if cmds.formLayout(self._rs_form, nd=100):
					#renderSettingInts = 
					cmds.text(self._rs_noOptsText, l='Right Click to Add Settings...', al='center')
					cmds.text(self._rs_rangeText1, l='Frame Range')
					cmds.intField(self._rs_start, v=1, w=60)
					cmds.text(self._rs_rangeText2, l='-')
					cmds.intField(self._rs_end, v=10, w=60)
					cmds.button(self._rs_getRangeBtn, l='get range from file', c=self.rs_getRangeBtnCommand)
					cmds.text(self._rs_getRangeText, l='(requires .ma)', en=False)
					cmds.text(self._rs_padText, l='Padding')
					cmds.intField(self._rs_pad, v=4, w=60)
					cmds.text(self._rs_resText, l='Resolution')
					cmds.intField(self._rs_resW, v=853, w=60)
					if cmds.popupMenu(mm=True):
						cmds.menuItem(l='853x480', c=self.rs_setResPreset480)
						cmds.menuItem(l='1280x720', c=self.rs_setResPreset720)
						cmds.menuItem(l='1920x1080', c=self.rs_setResPreset1080)
					cmds.intField(self._rs_resH, v=480, w=60)
					if cmds.popupMenu(mm=True):
						cmds.menuItem(l='853x480', c=self.rs_setResPreset480)
						cmds.menuItem(l='1280x720', c=self.rs_setResPreset720)
						cmds.menuItem(l='1920x1080', c=self.rs_setResPreset1080)
					cmds.text(self._rs_fncText, l='File Naming Format')
					if cmds.optionMenu(self._rs_fncOpt):
						cmds.menuItem(l='name')
						cmds.menuItem(l='name.ext')
						cmds.menuItem(l='name.#.ext')
						cmds.menuItem(l='name.ext.#')
						cmds.menuItem(l='name.#')
						cmds.menuItem(l='name#.ext')
						cmds.menuItem(l='name_#.ext')
					cmds.optionMenu(self._rs_fncOpt, e=True, sl=3)
					cmds.text(self._rs_ofText, l='Output Format')
					if cmds.optionMenu(self._rs_ofOpt):
						cmds.menuItem(l='Targa')
						cmds.menuItem(l='Tiff8')
						cmds.menuItem(l='Tiff16')
						cmds.menuItem(l='Tiff32')
						cmds.menuItem(l='OpenEXR')
						cmds.menuItem(l='MayaIFF')
					cmds.text(self._rs_rText, l='Renderer')
					if cmds.optionMenu(self._rs_rOpt):
						cmds.menuItem(l='RenderMan')
						cmds.menuItem(l='Maya Software')
						cmds.menuItem(l='Mental Ray')
					cmds.text(self._rs_pdText, l='Project Directory')
					cmds.textField(self._rs_pdField, width=210, cc=self.rs_pdFieldChange)
					if cmds.popupMenu(mm=True):
						cmds.menuItem(l='Add to favorites (coming soon)', en=False)
						cmds.menuItem(l='Manage project directory favorites...', en=False)
					cmds.button(self._rs_pdBtn, l='browse...', c=self.rs_pdBrowse)
					cmds.text(self._rs_rdText, l='Render Directory')
					cmds.textField(self._rs_rdField, width=210, cc=self.rs_rdFieldChange)
					if cmds.popupMenu(mm=True):
						cmds.menuItem(l='Add to favorites (coming soon)', en=False)
						cmds.menuItem(l='Manage render directory favorites...', en=False)
					cmds.button(self._rs_rdBtn, l='browse...', c=self.rs_rdBrowse)
					
					#no opts text
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_noOptsText, 'left', -75, 50), (self._rs_noOptsText, 'top', -20, 50)])
					#frame range
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_start, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_rangeText1, 'right', 2, self._rs_start), (self._rs_rangeText2, 'left', 2, self._rs_start), (self._rs_end, 'left', 2, self._rs_rangeText2)])
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_rangeText1, 'top', 8, 0), (self._rs_start, 'top', 6, 0), (self._rs_rangeText2, 'top', 8, 0), (self._rs_end, 'top', 6, 0)])
					#get frame range
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_getRangeBtn, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_getRangeText, 'left', 4, self._rs_getRangeBtn)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_getRangeText, 'top', 5, self._rs_start), (self._rs_getRangeBtn, 'top', 2, self._rs_start)])
					#padding
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_pad, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_padText, 'right', 2, self._rs_pad)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_padText, 'top', 8, self._rs_getRangeBtn), (self._rs_pad, 'top', 6, self._rs_getRangeBtn)])
					#resolution
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_resW, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_resText, 'right', 2, self._rs_resW), (self._rs_resH, 'left', 2, self._rs_resW)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_resText, 'top', 8, self._rs_pad), (self._rs_resW, 'top', 6, self._rs_pad), (self._rs_resH, 'top', 6, self._rs_pad)])
					#file naming convention
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_fncOpt, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_fncText, 'right', 2, self._rs_resW)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_fncOpt, 'top', 6, self._rs_resW), (self._rs_fncText, 'top', 8, self._rs_resW)])
					#output format
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_ofOpt, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_ofText, 'right', 2, self._rs_ofOpt)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_ofOpt, 'top', 6, self._rs_fncOpt), (self._rs_ofText, 'top', 8, self._rs_fncOpt)])
					#renderer
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_rOpt, 'left', self._rs_centerLine, 50)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_rText, 'right', 2, self._rs_rOpt)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_rOpt, 'top', 6, self._rs_ofOpt), (self._rs_rText, 'top', 8, self._rs_ofOpt)])
					#project text
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_pdText, 'left', 12, 0)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_pdText, 'bottom', 2, self._rs_pdField)])
					#project directory field
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_pdField, 'left', 4, 0)], ac=[(self._rs_pdField, 'right', 2, self._rs_pdBtn)])
					cmds.formLayout(self._rs_form, e=True, af=[(self._rs_pdBtn, 'right', 6)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_pdField, 'bottom', 3, self._rs_rdText), (self._rs_pdBtn, 'bottom', 3, self._rs_rdText)])
					#render directory text
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_rdText, 'left', 12, 0)])
					cmds.formLayout(self._rs_form, e=True, ac=[(self._rs_rdText, 'bottom', 2, self._rs_rdField)])
					#render directory field
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_rdField, 'left', 4, 0)], ac=[(self._rs_rdField, 'right', 2, self._rs_rdBtn)])
					cmds.formLayout(self._rs_form, e=True, af=[(self._rs_rdBtn, 'right', 6)])
					cmds.formLayout(self._rs_form, e=True, ap=[(self._rs_rdField, 'bottom', 4, 100), (self._rs_rdBtn, 'bottom', 4, 100)])
					
					cmds.setParent(self._mainForm)
			
			#batch file settings frame/form
			if cmds.frameLayout(self._bfs_frame, l='Batch File Settings', bs='etchedOut', li=10, height=self._frameHeights):
				if cmds.formLayout(self._bfs_form, nd=100):
					cmds.text(self._bfs_nameText, l='Naming Convention')
					cmds.text(self._bfs_prefixText, l='Prefix')
					cmds.textField(self._bfs_prefixField, cc=self.bfs_namingConventionUpdate)
					cmds.checkBox(self._bfs_sceneCheck, l='Scene Name', v=True, cc=self.bfs_namingConventionUpdate)
					cmds.checkBox(self._bfs_rangeCheck, l='Frame Range', v=True, cc=self.bfs_namingConventionUpdate)
					cmds.checkBox(self._bfs_numberedCheck, l='Numbered', v=False, cc=self.bfs_namingConventionUpdate)
					cmds.text(self._bfs_previewText, l='preview: prefix_sceneFile_1-100_[1].bat', al='center', en=False)
					cmds.separator(self._bfs_sep1, st='in')
					cmds.text(self._bfs_divText, l='Divide frame range into segments:')
					cmds.intField(self._bfs_divField, min=1, max=10000, v=1, cc=self.bfs_divFieldChange)
					cmds.text(self._bfs_divText2, l='Ex, 1-100 with 2 segments: 1-50, 51-100', al='center', en=False)
					cmds.separator(self._bfs_sep2, st='in')
					cmds.text(self._bfs_saveText, l='Save Location (existing .bat files will be overwritten)')
					cmds.textField(self._bfs_saveField, cc=self.bfs_saveFieldChange)
					if cmds.popupMenu(mm=True):
						cmds.menuItem(l='Add to favorites (coming soon)', en=False)
						cmds.menuItem(l='Manage save location favorites..', en=False)
						cmds.menuItem(d=True)
						cmds.menuItem(l='Open Folder', c=self.bfs_saveLocationOpen)
					cmds.button(self._bfs_saveBtn, l='browse...', c=self.bfs_saveBrowse)
					
					#naming text
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_nameText, 'left', 8, 0), (self._bfs_nameText, 'top', 8, 0)])
					#prefix
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_prefixText, 'left', 12, 0)])
					cmds.formLayout(self._bfs_form, e=True, ac=[(self._bfs_prefixField, 'left', 6, self._bfs_prefixText)], ap=[(self._bfs_prefixField, 'right', 12, 100)])
					cmds.formLayout(self._bfs_form, e=True, ac=[(self._bfs_prefixText, 'top', 8, self._bfs_nameText), (self._bfs_prefixField, 'top', 6, self._bfs_nameText)])
					#scene
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_sceneCheck, 'left', -130, 50)])
					cmds.formLayout(self._bfs_form, e=True, ac=[(self._bfs_rangeCheck, 'left', 3, self._bfs_sceneCheck), (self._bfs_numberedCheck, 'left', 3, self._bfs_rangeCheck)])
					cmds.formLayout(self._bfs_form, e=True, ac=[(self._bfs_sceneCheck, 'top', 4, self._bfs_prefixField), (self._bfs_rangeCheck, 'top', 4, self._bfs_prefixField), (self._bfs_numberedCheck, 'top', 4, self._bfs_prefixField)])
					#preview
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_previewText, 'left', 12, 0), (self._bfs_previewText, 'right', 12, 100)], ac=[(self._bfs_previewText, 'top', 6, self._bfs_numberedCheck)])
					#sep1
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_sep1, 'left', 12, 0), (self._bfs_sep1, 'right', 12, 100)], ac=[(self._bfs_sep1, 'top', 8, self._bfs_previewText)])
					#divisions
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_divText, 'left', -115, 50)])
					cmds.formLayout(self._bfs_form, e=True, ac=[(self._bfs_divField, 'left', 3, self._bfs_divText)])
					cmds.formLayout(self._bfs_form, e=True, ac=[(self._bfs_divText, 'top', 8, self._bfs_sep1), (self._bfs_divField, 'top', 6, self._bfs_sep1)])
					#divisions help
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_divText2, 'left', -105, 50)], ac=[(self._bfs_divText2, 'top', 3, self._bfs_divField)])
					#sep2
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_sep2, 'left', 12, 0), (self._bfs_sep2, 'right', 12, 100)], ac=[(self._bfs_sep2, 'top', 8, self._bfs_previewText)])
					#save location text
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_saveText, 'left', 8, 0)], ac=[(self._bfs_saveText, 'bottom', 3, self._bfs_saveField)])
					#save location field
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_saveField, 'left', 4, 0)], ac=[(self._bfs_saveField, 'right', 2, self._bfs_saveBtn)])
					cmds.formLayout(self._bfs_form, e=True, af=[(self._bfs_saveBtn, 'right', 6)])
					cmds.formLayout(self._bfs_form, e=True, ap=[(self._bfs_saveField, 'bottom', 4, 100), (self._bfs_saveBtn, 'bottom', 4, 100)])
					
					cmds.setParent(self._mainForm)
			
		cmds.button(self._makeBtn, l='Make Batch File (no files selected)', en=False, h=25, c=self.makeButtonCommand)
		
		cmds.formLayout(self._mainForm, e=True, af=[(self._fl_form, 'left', 4), (self._fl_form, 'right', 4), (self._fl_form, 'top', 4)], ac=[(self._fl_form, 'bottom', 6, self._bfs_frame)])
		cmds.formLayout(self._mainForm, e=True, af=[(self._rs_frame, 'left', 4)], ap=[(self._rs_frame, 'right', 2, 50)], ac=[(self._rs_frame, 'bottom', 4, self._makeBtn)])
		cmds.formLayout(self._mainForm, e=True, af=[(self._bfs_frame, 'right', 4)], ap=[(self._bfs_frame, 'left', 2, 50)], ac=[(self._bfs_frame, 'bottom', 4, self._makeBtn)])
		cmds.formLayout(self._mainForm, e=True, af=[(self._makeBtn, 'left', 4), (self._makeBtn, 'right', 4), (self._makeBtn, 'bottom', 4)])
		
		self.rs_updateRenderSettingsDisplay()
		cmds.showWindow(self._name)
	
	def resetSettings(self, *args):
		cmds.window(self._name, e=True, width=self._winWidth, height=self._winHeight)
	
	def fl_addFiles(self, *args):
		cmds.fileBrowserDialog(m=0, fc=self.fl_addFilesHandler, an='Choose...', om='Import')
		
	def fl_addFilesHandler(self, fileName, fileType):
		self.fl_addFileToList(fileName)
		
	def fl_addFolder(self, *args):
		cmds.fileBrowserDialog(m=4, fc=self.fl_addFolderHandler, an='Select a folder...', om='Import')
		
	def fl_addFolderHandler(self, folderName, fileType):
		#get all the ma/mb files from the folder and add them
		if os.path.exists(folderName) and os.path.isdir(folderName):
			fileList = glob.glob('%s/*.m[a|b]' % folderName)
			fileList.sort()
			for f in fileList:
				self.fl_addFileToList(f)
	
	def fl_addFileToList(self, fileName):
		root, ext = os.path.splitext(fileName)
		if ext == '.ma' or ext == '.mb':
			curList = cmds.textScrollList(self._fl_list, q=True, ai=True)
			if curList:
				if fileName in curList:
					return
			cmds.textScrollList(self._fl_list, e=True, append=fileName)
		
		self.fl_updateGlobalVar()
	
	def fl_updateGlobalVar(self):
		#update global var
		curList = cmds.textScrollList(self._fl_list, q=True, ai=True)
		if curList == None:
			value = '{}'
		else:
			value = '{"%s"}' % '", "'.join(curList)
		self.sendToMel(var='bbfmWin_fileList', value=value )
	
	def fl_remSelFiles(self, *args):
		selFiles = cmds.textScrollList(self._fl_list, q=True, si=True)
		if selFiles:
			for f in selFiles:
				cmds.textScrollList(self._fl_list, e=True, ri=f)
		
		self.fl_updateGlobalVar()
		
	def fl_clearFiles(self, *args):
		cmds.textScrollList(self._fl_list, e=True, ra=True)
		self.fl_updateGlobalVar()
	
	def fl_listSelectCommand(self, *args):
		self.updateMakeButton()
	
	def rs_addRenderSettingsAll(self, *args):
		self.rs_setRenderSettingsDisplay([1, 1, 1, 1, 1, 1, 1, 1])
		
	def rs_removeRenderSettingsAll(self, *args):
		self.rs_setRenderSettingsDisplay([0, 0, 0, 0, 0, 0, 0, 0])
		
	def rs_setRenderSettingsDisplay(self, settings):
		cmds.menuItem(self._rs_mm_range, e=True, cb=settings[0])
		cmds.menuItem(self._rs_mm_pad, e=True, cb=settings[1])
		cmds.menuItem(self._rs_mm_res, e=True, cb=settings[2])
		cmds.menuItem(self._rs_mm_fnc, e=True, cb=settings[3])
		cmds.menuItem(self._rs_mm_of, e=True, cb=settings[4])
		cmds.menuItem(self._rs_mm_r, e=True, cb=settings[5])
		cmds.menuItem(self._rs_mm_pd, e=True, cb=settings[6])
		cmds.menuItem(self._rs_mm_rd, e=True, cb=settings[7])
		self.rs_updateRenderSettingsDisplay()
		
	def rs_updateRenderSettingsDisplay(self, *args):
		"""Checks the render settings menu and sets control visibilities accordingly"""
		fr = cmds.menuItem(self._rs_mm_range, q=True, cb=True)
		pad = cmds.menuItem(self._rs_mm_pad, q=True, cb=True)
		res = cmds.menuItem(self._rs_mm_res, q=True, cb=True)
		fnc = cmds.menuItem(self._rs_mm_fnc, q=True, cb=True)
		of = cmds.menuItem(self._rs_mm_of, q=True, cb=True)
		r = cmds.menuItem(self._rs_mm_r, q=True, cb=True)
		pd = cmds.menuItem(self._rs_mm_pd, q=True, cb=True)
		rd = cmds.menuItem(self._rs_mm_rd, q=True, cb=True)
		#range
		cmds.text(self._rs_rangeText1, e=True, vis=fr)
		cmds.intField(self._rs_start, e=True, vis=fr)
		cmds.text(self._rs_rangeText2, e=True, vis=fr)
		cmds.intField(self._rs_end, e=True, vis=fr)
		cmds.button(self._rs_getRangeBtn, e=True, vis=fr)
		cmds.text(self._rs_getRangeText, e=True, vis=fr)
		#padding
		cmds.text(self._rs_padText, e=True, vis=pad)
		cmds.intField(self._rs_pad, e=True, vis=pad)
		#res
		cmds.text(self._rs_resText, e=True, vis=res)
		cmds.intField(self._rs_resW, e=True, vis=res)
		cmds.intField(self._rs_resH, e=True, vis=res)
		#fnc
		cmds.text(self._rs_fncText, e=True, vis=fnc)
		cmds.optionMenu(self._rs_fncOpt, e=True, vis=fnc)
		#of
		cmds.text(self._rs_ofText, e=True, vis=of)
		cmds.optionMenu(self._rs_ofOpt, e=True, vis=of)
		#renderer
		cmds.text(self._rs_rText, e=True, vis=r)
		cmds.optionMenu(self._rs_rOpt, e=True, vis=r)
		#pd
		cmds.text(self._rs_pdText, e=True, vis=pd)
		cmds.textField(self._rs_pdField, e=True, vis=pd)
		cmds.button(self._rs_pdBtn, e=True, vis=pd)
		#rd
		cmds.text(self._rs_rdText, e=True, vis=rd)
		cmds.textField(self._rs_rdField, e=True, vis=rd)
		cmds.button(self._rs_rdBtn, e=True, vis=rd)
		#no options text visibility
		if fr or pad or res or fnc or of or r or pd or rd:
			cmds.text(self._rs_noOptsText, e=True, vis=False)
		else:
			cmds.text(self._rs_noOptsText, e=True, vis=True)
		
		self.bfs_namingConventionUpdate()
		cmds.frameLayout(self._rs_frame, e=True, h=self._frameHeights)
		
		self.rs_updateGlobalVar([fr, pad, res, fnc, of, r, pd, rd])
	
	def rs_updateGlobalVar(self, settings=None):
		#update global var
		for i in range(len(settings)):
			if settings[i] is False or settings[i] is True:
				settings[i] = int(settings[i])
		if settings == None:
			value = '{}'
		else:
			value = '{%s}' % ', '.join([str(num) for num in settings])
		self.sendToMel(var='bbfmWin_renderSettingsCheck', value=value )
	
	def rs_getRangeBtnCommand(self, *args):
		sel = cmds.textScrollList(self._fl_list, q=True, si=True)[-1]
		if sel:
			fr = getMAFrameRange(sel)
			if fr[0]:
				cmds.intField(self._rs_start, e=True, v=fr[0])
			if fr[1]:
				cmds.intField(self._rs_end, e=True, v=fr[1])
	
	def rs_setResPreset480(self, *args):
		self.rs_setResPreset([853,480])
	
	def rs_setResPreset720(self, *args):
		self.rs_setResPreset([1280,720])
	
	def rs_setResPreset1080(self, *args):
		self.rs_setResPreset([1920,1080])
	
	def rs_setResPreset(self, res):
		cmds.intField(self._rs_resW, e=True, v=res[0])
		cmds.intField(self._rs_resH, e=True, v=res[1])
	
	def rs_pdBrowse(self, *args):
		cmds.fileBrowserDialog(m=4, fc=self.rs_pdBrowseHandler, an='Select a folder...', om='Import')
	
	def rs_pdBrowseHandler(self, folderName, fileType):
		if os.path.exists(folderName) and os.path.isdir(folderName):
			cmds.textField(self._rs_pdField, e=True, tx=folderName)
	
	def rs_pdFieldChange(self, *args):
		val = cmds.textField(self._rs_pdField, q=True, tx=True)
		if val != '':
			val = os.path.abspath(val).replace('\\', '/')
		cmds.textField(self._rs_pdField, e=True, tx=val)
	
	def rs_rdBrowse(self, *args):
		cmds.fileBrowserDialog(m=4, fc=self.rs_rdBrowseHandler, an='Select a folder...', om='Import')
	
	def rs_rdBrowseHandler(self, folderName, fileType):
		if os.path.exists(folderName) and os.path.isdir(folderName):
			cmds.textField(self._rs_rdField, e=True, tx=folderName)
	
	def rs_rdFieldChange(self, *args):
		val = cmds.textField(self._rs_rdField, q=True, tx=True)
		if val != '':
			val = os.path.abspath(val).replace('\\', '/')
		cmds.textField(self._rs_rdField, e=True, tx=val)
		
	def bfs_namingConventionUpdate(self, *args):
		"""Checks the check boxes and prefix and updates the preview text"""
		rs_fr = cmds.menuItem(self._rs_mm_range, q=True, cb=True)
		cmds.checkBox(self._bfs_rangeCheck, e=True, en=rs_fr)
		cmds.intField(self._bfs_divField, e=True, en=rs_fr)
		
		prefix = cmds.textField(self._bfs_prefixField, q=True, tx=True)
		scene = cmds.checkBox(self._bfs_sceneCheck, q=True, v=True)
		fr = cmds.checkBox(self._bfs_rangeCheck, q=True, v=True)
		num = cmds.checkBox(self._bfs_numberedCheck, q=True, v=True)
		
		prevElems = []
		if prefix:
			prevElems.append(prefix)
		if scene:
			prevElems.append('myMayaFile')
		if fr and rs_fr:
			prevElems.append('1-100')
		if num:
			prevElems.append('[1]')
		prevStr = '_'.join(prevElems) + '.bat'
		
		cmds.text(self._bfs_previewText, e=True, l=prevStr)
		
	def bfs_divFieldChange(self, *args):
		self.updateMakeButton()
	
	def bfs_saveBrowse(self, *args):
		cmds.fileBrowserDialog(m=4, fc=self.bfs_saveBrowseHandler, an='Select a folder...', om='Import')
	
	def bfs_saveBrowseHandler(self, folderName, fileType):
		if os.path.exists(folderName) and os.path.isdir(folderName):
			cmds.textField(self._bfs_saveField, e=True, tx=folderName)
	
	def bfs_saveFieldChange(self, *args):
		val = cmds.textField(self._bfs_saveField, q=True, tx=True)
		if val != '':
			val = os.path.abspath(val).replace('\\', '/')
		cmds.textField(self._bfs_saveField, e=True, tx=val)
	
	def bfs_saveLocationOpen(self, *args):
		path = os.path.abspath(cmds.textField(self._bfs_saveField, q=True, tx=True)).replace('\\', '/')
		cmd = r'system("load "+encodeString("%s")+"");' % path
		mel.eval(cmd)
	
	def updateMakeButton(self):
		selList = cmds.textScrollList(self._fl_list, q=True, si=True)
		if selList:
			count = len(selList)
			countPlural = count > 1 and 's' or ''
			cmds.button(self._makeBtn, e=True, l='Make Batch File%s (%d file%s selected)' % (countPlural, count, countPlural), en=True)
		else:
			cmds.button(self._makeBtn, e=True, l='Make Batch Files (no files selected)', en=False)
	
	def getRenderSettings(self):
		#get render settings
		frCheck = cmds.menuItem(self._rs_mm_range, q=True, cb=True)
		padCheck = cmds.menuItem(self._rs_mm_pad, q=True, cb=True)
		resCheck = cmds.menuItem(self._rs_mm_res, q=True, cb=True)
		fncCheck = cmds.menuItem(self._rs_mm_fnc, q=True, cb=True)
		ofCheck = cmds.menuItem(self._rs_mm_of, q=True, cb=True)
		rCheck = cmds.menuItem(self._rs_mm_r, q=True, cb=True)
		pdCheck = cmds.menuItem(self._rs_mm_pd, q=True, cb=True)
		rdCheck = cmds.menuItem(self._rs_mm_rd, q=True, cb=True)
		fr, pad, res, fnc, of, r, pd, rd = None, None, None, None, None, None, None, None
		renderers = ['default', 'rman', 'sw', 'mr']
		if frCheck:
			fr = [cmds.intField(self._rs_start, q=True, v=True), cmds.intField(self._rs_end, q=True, v=True)]
		if padCheck:
			pad = cmds.intField(self._rs_pad, q=True, v=True)
		if resCheck:
			res = [cmds.intField(self._rs_resW, q=True, v=True), cmds.intField(self._rs_resH, q=True, v=True)]
		if fncCheck:
			fnc = cmds.optionMenu(self._rs_fncOpt, q=True, v=True)
		if ofCheck:
			of = cmds.optionMenu(self._rs_ofOpt, q=True, v=True)
		if rCheck:
			r = renderers[cmds.optionMenu(self._rs_rOpt, q=True, sl=True)]
		if pdCheck:
			pd = cmds.textField(self._rs_pdField, q=True, tx=True)
		if rdCheck:
			rd = cmds.textField(self._rs_rdField, q=True, tx=True)
		
		return {'range':fr, 'pad':pad, 'res':res, 'fnc':fnc, 'of':of, 'r':r, 'pd':pd, 'rd':rd}
		
	def getBatchFileSettings(self):
		#get batch file settings
		prefix = cmds.textField(self._bfs_prefixField, q=True, tx=True)
		sceneCheck = cmds.checkBox(self._bfs_sceneCheck, q=True, v=True)
		frCheck = cmds.checkBox(self._bfs_rangeCheck, q=True, v=True)
		numCheck = cmds.checkBox(self._bfs_numberedCheck, q=True, v=True)
		div = cmds.intField(self._bfs_divField, q=True, v=True)
		save = cmds.textField(self._bfs_saveField, q=True, tx=True)
		return {'prefix':prefix, 'includeScene':sceneCheck, 'includeRange':frCheck, 'includeNum':numCheck, 'div':div, 'sd':save}
	
	def makeButtonCommand(self, *args):
		"""Gathers the necessary information, then creates and runs a BatchFileMaker object"""
		#get file list
		fileList = cmds.textScrollList(self._fl_list, q=True, si=True)
		rs = self.getRenderSettings()
		bfs = self.getBatchFileSettings()
		
		bfm = BatchFileMaker(fileList, rs, bfs)
		bfm.run()

class BatchFileMaker(object):
	
	def __init__(self, fileList, rs, bfs):
		self.fileList = fileList
		self.rs = rs
		self.bfs = bfs
		self.rangeList = None
		self.flags = None
		self.batCmds = None

	def run(self):
		#check file list
		if not self.fileList:
			pyError('no files were specified')
			return
		#check paths
		self.checkPaths()
		#generate flags that are the same for every .bat
		self.buildStaticFlags()
		#get the divided frame ranges, if any
		self.buildRangeDivs()
		#build the bat commands, 1 per file per range
		self.buildBatCmds()
		#write the bats to files
		self.writeBatCmds()
	
	def checkPaths(self):
		"""Checks/creates destination folders if necessary"""
		if self.bfs['sd']:
			if not os.path.exists(self.bfs['sd']):
				result = cmds.confirmDialog(t='Creating Directory...', m='The specified Save Location does not exist, create?\n%s' % self.bfs['sd'], b=['Yes', 'No'], db='Ok', cb='No')
				if result == 'Yes':
					os.makedirs(self.bfs['sd'])
					print 'save directory has been created: %s' % self.bfs['sd']
		else:
			result = cmds.confirmDialog(t='Save Location', ma='center', m='No save location was specified for the batch files.\nThey will be saved to the last working directory.\nDo you want to continue?', b=['Yes', 'No'], db='Ok', cb='No')
			if result == 'Yes':
				pyWarning('no save location specified: batch files will be saved to the last working directory, check script editor for details')
			else:
				raise BatchFileMakerError('cancelled by request')
		
		if self.rs['pd']:
			if not os.path.exists(self.rs['pd']):
				result = cmds.confirmDialog(t='Creating Directory...', m='The specified Project Directory does not exist, create?\n%s' % self.rs['pd'], b=['Yes', 'No'], db='Ok', cb='No')
				if result == 'Yes':
					os.makedirs(self.rs['pd'])
					print 'project directory has been created: %s' % self.rs['pd']
		
		if self.rs['rd']:
			if not os.path.exists(self.rs['rd']):
				result = cmds.confirmDialog(t='Creating Directory...', m='The specified Render Directory does not exist, create?\n%s' % self.rs['rd'],b=['Yes', 'No'], db='Ok', cb='No')
				if result == 'Yes':
					os.makedirs(self.rs['rd'])
					print 'render directory has been created: %s' % self.rs['rd']
	
	def buildStaticFlags(self):
		"""Creates the flags that will be the same for every .bat"""
		self.flags = []
		if self.rs['r']:
			self.flags.append('-r %s' % self.rs['r'])
		if self.rs['pad']:
			self.flags.append('-pad %d' % self.rs['pad'])
		if self.rs['res']:
			self.flags.append('-res %d %d' % (self.rs['res'][0], self.rs['res'][1]))
		if self.rs['fnc']:
			self.flags.append('-fnc %s' % self.rs['fnc'])
		if self.rs['of']:
			self.flags.append('-of %s' % self.rs['of'])
		if self.rs['pd']:
			self.flags.append('-proj %s' % self.rs['pd'])
		if self.rs['rd']:
			self.flags.append('-rd %s' % self.rs['rd'])
	
	def buildRangeDivs(self):
		if self.rs['range']:
			if self.bfs['div']:
				fr = self.rs['range']
				div = self.bfs['div']
				rangeLen = fr[1] - fr[0] + 1
				if div > rangeLen:
					div = rangeLen
				unit = (rangeLen / div)
				ex = (rangeLen) - (div * unit)
				unit -= 1
				st = fr[0]
				frList = []
				for i in range(0, div):
					end = st + unit
					if ex > 0:
						end += 1
						ex -= 1
					frList.append([st, end])
					st = end + 1
				self.rangeList = frList
	
	def buildBatCmds(self):
		self.batCmds = {}
		for f in self.fileList:
			if self.rangeList:
				i=1
				for r in self.rangeList:
					curFlags = list(self.flags)
					curFlags.append('-s %s' % r[0])
					curFlags.append('-e %s' % r[1])
					batCmd = 'render^\n %s^\n %s\npause' % ('^\n '.join(curFlags), f)
					batName = self.getBatName(f, r, i)
					self.batCmds[batName] = batCmd
					i+=1
			else:
				sep = len(self.flags)>0 and '^\n ' or ''
				batCmd = 'render^\n %s%s %s' % ('^\n '.join(self.flags), sep, f)
				batName = self.getBatName(f, None, None)
				self.batCmds[batName] = batCmd
	
	def getBatName(self, scene, fr, num):
		elems = []
		if self.bfs['prefix']:
			elems.append(self.bfs['prefix'])
		if self.bfs['includeScene']:
			sceneRoot = os.path.basename(scene)
			sceneRoot, ext = os.path.splitext(sceneRoot)
			elems.append(sceneRoot)
		if self.bfs['includeRange'] and fr:
			rangeStr = '%d-%d' % (fr[0], fr[1])
			elems.append(rangeStr)
		if self.bfs['includeNum'] and num:
			numStr = '[%d]' % num
			elems.append(numStr)
		
		returnStr = '_'.join(elems)
		return returnStr
	
	def writeBatCmds(self):
		files = self.batCmds.keys()
		for f in files:
			filePath = os.path.abspath(os.path.join(self.bfs['sd'], '%s.bat' % f))
			self.writeFile(filePath, self.batCmds[f])
	
	def writeFile(self, fileName, data):
		try:
			fsock = open(fileName, 'w')
			try:
				fsock.write(data+'\n')
				print '// wrote batch file successfully: %s' % fileName
			finally:
				fsock.close()
		except IOError:
			pyWarning(r'// could not open file %s' % fileName)
