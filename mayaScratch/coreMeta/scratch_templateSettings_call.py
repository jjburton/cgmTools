cgm.core._reload()
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM

#puppet...
p1 = cgmPM.cgmPuppet('M1_puppetNetwork')
p1.templateSettings_call('markStarterData')
p1.templateSettings_call('query')
p1.templateSettings_call('store')
p1.templateSettings_call('reset')
p1.templateSettings_call('load')
p1.templateSettings_call('update')

p1.templateSettings_call('export')
p1.templateSettings_call('import')

p1.mirrorSetup_verify(mode = 'template')

"""
store -- store current pose
load -- load stored pose
query -- query the pose
update -- this mode is if the base data has been updated
markStarterData -- this mode is for testing and will mark the base point data
            
"""
m1 = cgmMeta.cgmNode('l_eye_part')
m1 = cgmMeta.cgmNode('spine_part')
m1 = cgmMeta.cgmNode('l_arm_part')
m1 = cgmMeta.cgmNode('l_index_part')
m1.templateSettings_call('query')
m1.templateSettings_call('store')
m1.templateSettings_call('reset')
m1.templateSettings_call('update')
m1.templateSettings_call('markStarterData')

m1.get_controls('template')
m1.isTemplated()

#rigblocks need to get controls
r1 = cgmMeta.asMeta('l_eye_rigHelper')
r1.get_controls(asMeta = False)