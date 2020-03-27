import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools import Project as Project
import os.path
from difflib import SequenceMatcher

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