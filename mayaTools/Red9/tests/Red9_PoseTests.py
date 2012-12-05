'''
------------------------------------------
Red9 Studio Pack : Maya Pipeline Solutions
email: rednineinfo@gmail.com
-------------------------------------------

This is the main unittest for the Red9_Meta module and a good
example of what's expected and what the systems can do on simple data
================================================================

'''


import pymel.core as pm
import maya.cmds as cmds
import os

#import Red9_Meta as r9Meta
import Red9.core.Red9_Meta as r9Meta
import Red9.startup.setup as r9Setup


    
class Test_MetaRig():
    
    def setup(self):
        cmds.file(os.path.join(r9Setup.red9ModulePath(),'tests','testFiles','MetaRig_baseTests_MetaWired.ma'),open=True,f=True)
        self.mRig=self.addMetaRig()
        
    def teardown(self):
        self.setup()   
        