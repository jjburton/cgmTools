import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools import Project as Project
import os.path
from difflib import SequenceMatcher
from shutil import copyfile

def FindAndRemapTextures():
    optionVarProjectStore = cgmMeta.cgmOptionVar("cgmVar_projectCurrent", varType = "string")

    project = Project.data(filepath=optionVarProjectStore.getValue())

    content = os.path.normpath(project.userPaths_get()['content'])
    export = os.path.normpath(project.userPaths_get()['export'])

    for f in mc.ls(type='file'):
        texturePath = os.path.normpath(mc.getAttr('%s.fileTextureName' % f))
        if not os.path.exists(texturePath):
            match = SequenceMatcher(None,texturePath, content).find_longest_match(0,len(texturePath), 0, len(content))
            newPath = content + texturePath[match.size+match.a:]
            if os.path.exists(newPath):
                print "changing %s.fileTexturePath to %s" % (f, newPath)
                mc.setAttr( '%s.fileTextureName' % f, newPath, type='string' )
            else:
                match = SequenceMatcher(None,texturePath, export).find_longest_match(0,len(texturePath), 0, len(export))
                newPath = export + texturePath[match.size+match.a:]
                
                if os.path.exists(newPath):
                    print "changing %s.fileTexturePath to %s" % (f, newPath)
                    mc.setAttr( '%s.fileTextureName' % f, newPath, type='string' )
                else:
                    print "Can't find %s" % texturePath

def LocalizeTextures():
    optionVarProjectStore       = cgmMeta.cgmOptionVar("cgmVar_projectCurrent", varType = "string")

    project = Project.data(filepath=optionVarProjectStore.getValue())

    content = os.path.normpath(project.userPaths_get()['content'])
    export = os.path.normpath(project.userPaths_get()['export'])

    for f in mc.ls(type='file'):
        textureName = mc.getAttr('%s.fileTextureName' % f)
        
        if content not in textureName and os.path.exists(textureName) and os.path.isfile(textureName):
            newPath = os.path.dirname(mc.file(q=True, loc=True))
            if mc.referenceQuery(f, inr=True):
                newPath = of.path.basedir(mc.referenceQuery(f, filename=True))
            
            newFilename = os.path.join(newPath, 'textures', os.path.split(textureName)[1])
            
            if not os.path.exists(os.path.dirname(newFilename)):
                os.makedirs(os.path.dirname(newFilename))
            
            if os.path.normpath(textureName) != os.path.normpath(newFilename):
                copyfile(textureName, newFilename)
            
                print 'remapped %s to %s' % (textureName, newFilename)
                mc.setAttr('%s.fileTextureName' % f, newFilename, type='string')