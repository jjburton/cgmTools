//make a simple d3 nurbs surface
string $plane[] = `nurbsPlane -ch on -o on -po 0 -ax 0 1 0 -w 5 -lr .1` ;
//deform the surface at each CV along V
select -r nurbsPlane1.cv[0][0:3] ;
CreateCluster;
select -r nurbsPlane1.cv[1][0:3] ;
CreateCluster;
select -r nurbsPlane1.cv[2][0:3] ;
CreateCluster;
select -r nurbsPlane1.cv[3][0:3] ;
CreateCluster;
//make a hierarchy of the clusters
parent cluster2Handle cluster1Handle;
parent cluster3Handle cluster4Handle;
//make and connect a pointOnSurtfaceInfo node
string $posi = `createNode pointOnSurfaceInfo`;
connectAttr ($plane[0] + ".worldSpace[0]") ($posi + ".inputSurface");
//add a reader group and give it attr for controlling the read point of the posi node,
//make the local axis visible and make it grabbable
string $readr = `group -em -n "reader"`;
addAttr -ln "posU" -dv .5 -at double $readr;
setAttr -e-keyable true ($readr + ".posU");
addAttr -ln "posV" -dv .5 -at double $readr;
setAttr -e-keyable true ($readr + ".posV");
setAttr ($readr + ".displayHandle") 1;
setAttr ($readr +".displayLocalAxis") 1;
//make the aim constraint for conversion of the output vectors of the posi node to euler rotations
string $aim = `createNode aimConstraint`;
//drive the reader’s translation
connectAttr ($posi + ".position") ($readr + ".t") ;
//hook up the UV driver attrs to the posi node
connectAttr ($readr + ".posU" ) ($posi + ".parameterU" );
connectAttr ($readr + ".posV" ) ($posi + ".parameterV" );
//connect aim constrain as specified
connectAttr ($posi + ".tangentU") ($aim + ".target[0].targetTranslate") ;
connectAttr ($posi + ".tangentV") ($aim + ".worldUpVector") ;
connectAttr ($aim + ".constraintRotate" ) ($readr + ".r" );
//set some keys
setKeyframe -breakdown 0 |cluster4Handle.rotate;
currentTime 24 ;
setAttr cluster4Handle.ry 70;
setKeyframe -breakdown 0 |cluster4Handle.rotate;
//playback the scene. the z rotation does not work in a useful way, although the
//x axis is pinned to the U isoparm. The rotation does not "follow" the V isoparm of the surface
//one way this can be remedied by using a normal constraint (from the surface to the reader)
//instead of an aim constraint, and feeding the .tangentV of the posi node into the
//.worldUpVector of the normal constraint
//This could have been setup so that we "follow" the U parameter instead of the V,
//by altering the clusters and the length/ratio of the surface, however, what we are seeing
//is a shearing of the U and V parameter vectors in relation to each other. There will never
//be shearing between U (or V) and the surface normal: that will always be 90 degrees, so
//it’s probably a superior method of reading the vectors produced by the surface and posi node.