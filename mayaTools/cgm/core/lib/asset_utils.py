import maya.cmds as mc
import os.path
import re

class Asset(object):
    '''
Asset class.

Class to manipulate and access data for an asset

| outputs Asset

example:
.. python::
    
    import pyunify.pipe.metaTag as metaTag
    import pyunify.lib.node as node
    
    x = metaTag.MetaTag(node.Selected[0], "type", "Character")
    
    # Returns type
    print x.data["type"]
    '''

    name = ""

    def __init__(self, transform):
        self.transform = transform

    @property
    def referenceFile(self):
      return mc.referenceQuery(self.transform, filename=True)

    @property
    def assetFile(self):
      return os.path.basename(self.referenceFile)
    
    @property
    def referenceNode(self):
      return mc.referenceQuery(self.transform, referenceNode=True)
    
    @property
    def name(self):
      return self.referenceFile.split('/')[-2]

    @property
    def type(self):
      return self.referenceFile.split('/')[-3]

    @property
    def versions(self):
      versions = []
      for f in os.listdir( os.path.dirname(self.referenceFile) ):
          if f.split('.')[-1] in ['ma','mb']:
              result = re.search('%s_.*[0-9]+\.m[b|a]' % '_'.join(os.path.basename(self.referenceFile).split('_')[:2]), f)
              if result:
                  versions.append(f)

      versions.sort()

      return versions

    def UpdateToLatest(self):
      if self.versions[-1] != self.assetFile.split('{')[0]:
        self.ChangeVersion(self.versions[-1])
        return True

      return False

    def ChangeVersion(self, version):
      mc.file(os.path.join(os.path.dirname(self.referenceFile), version), loadReference=self.referenceNode)

class AssetDirectory(object):
    name = ""

    def __init__(self, dir,assetName = None, assetType = 'rig'):
        self.directory = dir
        self.name = assetName if assetName else os.path.basename(dir)
        self.assetType = assetType


    @property
    def versions(self):
      versions = []
      for f in os.listdir(self.directory):
          result = re.search('%s_%s_.*[0-9]+\.m[b|a]' % (self.name, self.assetType), f)
          if result:
              versions.append(f)

      versions.sort()

      return versions

    def GetFullPaths(self):
      return [os.path.join(self.directory, x) for x in self.versions]