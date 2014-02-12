import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta

def add_UV_grid_location_attr(metaObject):
    ''' Sometimes there is a need to know what grid space your UVs are in.
        UVs are not always going to be in the 0-1 grid space and are placed 
        in another grid space. This function checks where they are and adds 
        and attrabut with that data.'''
    
    ## check if it a mesh type
    meta_shape = metaObject.getShapes()
    mc.objectType(meta_shape) == 'mesh'
    
    ##  get all the UV shell points locations  
    UV_locations = mc.polyEditUV(metaObject.mNode +".map[:]",
                                  q=True,u=True,v=False)
 
    ## make a new list for U and one for V
    U_gridSpaces = []
    V_gridSpaces = []
    
    ## iterate the UV locations(list comes back Uvalue,Vvalue,Uvalue,Vvalue,...)
    for i in range(len(UV_locations)):
        if i%2 == 0:
            #Check U , I am using int as a way to round to the lowest whole number 
            GridSpace = int(UV_locations[i])
            # check if it is alreay in the list
            if GridSpace not in U_gridSpaces:
                U_gridSpaces.append(GridSpace)
        else:
            #Check V, I am using int as a way to round to the lowest whole number 
            GridSpace = int(UV_locations[i])
            # check if it is alreay in the list
            if GridSpace not in V_gridSpaces:
                V_gridSpaces.append(GridSpace)
    
    ## add atter to metaObject
    metaObject.addAttr("U_gridSpace",U_gridSpaces)
    metaObject.addAttr("V_gridSpace",V_gridSpaces)


### example test 
#testCube = mc.polyCube(n='TestCube')[0]### make poly object
#meta_testCube = cgmMeta.cgmObject(testCube)### mata it 
#add_UV_grid_location_attr(meta_testCube)### add 2 new attrs that tell you what UV grids they are in

### move UVS around to and rund again to see what happens
#mc.polyEditUV(meta_testCube.mNode+".map[:]",u=10,v=7)
#add_UV_grid_location_attr(meta_testCube)