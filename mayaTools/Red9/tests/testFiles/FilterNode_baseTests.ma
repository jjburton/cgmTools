//Maya ASCII 2012 scene
//Name: FilterNode_baseTests.ma
//Last modified: Sun, Nov 25, 2012 08:44:37 PM
//Codeset: 1252
requires maya "2012";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2012";
fileInfo "version" "2012";
fileInfo "cutIdentifier" "001200000000-796618";
fileInfo "osv" "Microsoft Windows Vista Home Premium Edition, 32-bit Service Pack 2 (Build 6002)\n";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 2.2864638449695383 20.68030180685378 97.36279640175978 ;
	setAttr ".r" -type "double3" -2.7383527296031844 -2.1999999999997844 6.2166030182999049e-018 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 100.08893040405528;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 100.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 100.1 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 106.19317566267516;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 100.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 100.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "locator1";
createNode locator -n "locatorShape1" -p "locator1";
	setAttr -k off ".v";
createNode transform -n "locator3";
	setAttr ".t" -type "double3" 0 6.6427928089323434 0 ;
createNode locator -n "locatorShape3" -p "locator3";
	setAttr -k off ".v";
createNode transform -n "camera3";
	setAttr ".t" -type "double3" 19.151003247046212 8.7991095999942033 0 ;
createNode camera -n "cameraShape3" -p "camera3";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.41732 0.94488 ;
	setAttr ".ff" 0;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
createNode transform -n "pointLight3";
	setAttr ".t" -type "double3" 25.275873654885309 8.6265780392100027 0 ;
createNode pointLight -n "pointLightShape3" -p "pointLight3";
	setAttr -k off ".v";
createNode transform -n "pointLight4";
	setAttr ".t" -type "double3" 25.275873654885309 13.543727521559706 0 ;
createNode pointLight -n "pointLightShape4" -p "pointLight4";
	setAttr -k off ".v";
createNode transform -n "World_Root";
createNode joint -n "joint1" -p "World_Root";
	setAttr ".t" -type "double3" -3.6433793663688054 -0.012185215272137159 0 ;
	setAttr ".r" -type "double3" -4.2665688902068939e-007 -16.495013417216473 1.7309582018146534 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 89.999999999999986 ;
	setAttr ".radi" 0.61844869604190589;
createNode joint -n "joint2_Ctrl" -p "|World_Root|joint1";
	setAttr ".t" -type "double3" 3.2900081234768472 7.3052855397756017e-016 0 ;
	setAttr ".r" -type "double3" 1.0439685387335296e-014 42.983836676891734 3.7109899896632386e-013 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".pa" -type "double3" 0 89.999999897160009 0 ;
	setAttr ".radi" 0.63448438061649026;
createNode joint -n "joint3_AttrMarked" -p "|World_Root|joint1|joint2_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 3.6000313585854782 7.9936754073483622e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -89.999999999999986 ;
	setAttr ".radi" 0.63448438061649026;
	setAttr -k on ".MarkerAttr" -type "string" "left";
createNode ikEffector -n "effector1" -p "|World_Root|joint1|joint2_Ctrl";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "joint4" -p "World_Root";
	setAttr ".t" -type "double3" 4.0107393733741361 -0.080536935208317006 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 89.999999999999986 ;
	setAttr ".radi" 0.63323309947840856;
createNode joint -n "joint5_AttrMarked" -p "|World_Root|joint4";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 3.5758399232492319 7.9399596303302988e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".radi" 0.63823194373271785;
	setAttr -k on ".MarkerAttr";
createNode joint -n "joint6_Ctrl" -p "|World_Root|joint4|joint5_AttrMarked";
	setAttr ".t" -type "double3" 3.672484245499211 8.15455313385274e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -60.688103539485006 ;
	setAttr ".radi" 0.67751490982158769;
createNode joint -n "joint7_AttrMarked" -p "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 4.4319549232173605 6.6613381477509392e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -54.952902284820269 ;
	setAttr ".radi" 0.74790222180931787;
	setAttr -k on ".MarkerAttr" -type "string" "left";
createNode joint -n "joint8" -p "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked";
	setAttr ".t" -type "double3" 5.7927762883134761 -1.7763568394002505e-015 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 180 0 -65.283039528467512 ;
	setAttr ".radi" 0.58227284371501231;
createNode joint -n "joint9" -p "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8";
	setAttr ".t" -type "double3" 2.590608311823571 -2.3175905639050143e-015 -2.8349688781380116e-031 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 180 89.075954647227121 ;
	setAttr ".radi" 0.58227284371501231;
createNode transform -n "pCube3" -p "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl";
	setAttr ".t" -type "double3" -12.191867470387797 5.0737014995313521 0.11357408139026504 ;
	setAttr ".r" -type "double3" 0 0 -29.31189646051498 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1 ;
createNode mesh -n "pCubeShape3" -p "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|pCube3";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "nurbsCircle1" -p "World_Root";
	setAttr ".t" -type "double3" -15.607020480148948 2.1516474836710167 0 ;
createNode nurbsCurve -n "nurbsCircleShape1" -p "|World_Root|nurbsCircle1";
	setAttr -k off ".v";
	setAttr ".tw" yes;
createNode transform -n "Spine_Ctrl" -p "World_Root";
	setAttr ".t" -type "double3" -15.607020480148948 32.295623993885428 0 ;
createNode nurbsCurve -n "Spine_CtrlShape" -p "|World_Root|Spine_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "L_Foot_MarkerAttr_Ctrl" -p "|World_Root|Spine_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 0 -8.0639764503451907 0 ;
	setAttr -k on ".MarkerAttr";
createNode nurbsCurve -n "L_Foot_MarkerAttr_CtrlShape" -p "|World_Root|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "pCube2" -p "|World_Root|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl";
	setAttr ".t" -type "double3" 6.5029468039693565 -21.132228282434319 0.11357408139026504 ;
createNode mesh -n "pCubeShape2" -p "|World_Root|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl|pCube2";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "L_Wrist_Ctrl" -p "|World_Root|Spine_Ctrl";
	setAttr ".t" -type "double3" 1.7763568394002505e-015 -23.188486453180353 0 ;
createNode nurbsCurve -n "L_Wrist_CtrlShape" -p "|World_Root|Spine_Ctrl|L_Wrist_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "L_Pole_thingy" -p "|World_Root|Spine_Ctrl|L_Wrist_Ctrl";
	setAttr ".t" -type "double3" 15.607020480148948 0.71082667375467778 0 ;
createNode locator -n "L_Pole_thingyShape" -p "|World_Root|Spine_Ctrl|L_Wrist_Ctrl|L_Pole_thingy";
	setAttr -k off ".v";
createNode transform -n "R_Wrist_Ctrl" -p "|World_Root|Spine_Ctrl";
	setAttr ".t" -type "double3" 1.7763568394002505e-015 -15.986256374452974 0 ;
createNode nurbsCurve -n "R_Wrist_CtrlShape" -p "|World_Root|Spine_Ctrl|R_Wrist_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "R_Pole_AttrMarked_Ctrl" -p "|World_Root|Spine_Ctrl|R_Wrist_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 15.607020480148948 -6.4914034049727007 0 ;
	setAttr -k on ".MarkerAttr" -type "string" "right";
createNode locator -n "R_Pole_AttrMarked_CtrlShape" -p "|World_Root|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl";
	setAttr -k off ".v";
createNode transform -n "pCube1" -p "|World_Root|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl";
	setAttr ".t" -type "double3" -9.104073676179592 -9.2356576381542048 0.11357408139026504 ;
createNode mesh -n "pCubeShape1" -p "|World_Root|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl|pCube1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "R_Pole_Ctrl" -p "|World_Root|Spine_Ctrl";
	addAttr -ci true -sn "floatAttr" -ln "floatAttr" -at "double";
	setAttr ".t" -type "double3" 15.607020480148948 -22.477659779425675 0 ;
	setAttr -k on ".floatAttr" 2.53333;
createNode locator -n "R_Pole_CtrlShape" -p "|World_Root|Spine_Ctrl|R_Pole_Ctrl";
	setAttr -k off ".v";
createNode transform -n "L_Pole_Ctrl" -p "|World_Root|Spine_Ctrl";
	addAttr -ci true -sn "floatAttr" -ln "floatAttr" -at "double";
	setAttr ".t" -type "double3" 15.607020480148948 -19.204731212714822 0 ;
	setAttr -k on ".floatAttr";
createNode locator -n "L_Pole_CtrlShape" -p "|World_Root|Spine_Ctrl|L_Pole_Ctrl";
	setAttr -k off ".v";
createNode transform -n "camera1" -p "World_Root";
	addAttr -ci true -sn "export" -ln "export" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 19.151003247046212 0 0 ;
	setAttr -k on ".export";
createNode camera -n "cameraShape1" -p "|World_Root|camera1";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.41732 0.94488 ;
	setAttr ".ff" 0;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
createNode transform -n "camera2" -p "World_Root";
	addAttr -ci true -sn "export" -ln "export" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 19.151003247046212 4.0544916784287022 0 ;
	setAttr -k on ".export" yes;
createNode camera -n "cameraShape2" -p "|World_Root|camera2";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.41732 0.94488 ;
	setAttr ".ff" 0;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
createNode transform -n "pointLight1" -p "World_Root";
	setAttr ".t" -type "double3" 25.275873654885309 0 0 ;
createNode pointLight -n "pointLightShape1" -p "|World_Root|pointLight1";
	setAttr -k off ".v";
createNode transform -n "pointLight2" -p "World_Root";
	setAttr ".t" -type "double3" 25.275873654885309 4.0544916784287022 0 ;
createNode pointLight -n "pointLightShape2" -p "|World_Root|pointLight2";
	setAttr -k off ".v";
createNode transform -n "nurbsSphere1" -p "World_Root";
	setAttr ".t" -type "double3" -24.092390838288175 1.6667691774916349 0 ;
createNode nurbsSurface -n "nurbsSphereShape1" -p "|World_Root|nurbsSphere1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".tw" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 0;
	setAttr ".dvv" 0;
	setAttr ".cpr" 4;
	setAttr ".cps" 4;
	setAttr ".nufa" 4.5;
	setAttr ".nvfa" 4.5;
createNode transform -n "pCube4_AttrMarked" -p "World_Root";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" -9.104073676179592 8.2801814611384703 0.11357408139026504 ;
	setAttr -k on ".MarkerAttr" -type "string" "right";
createNode mesh -n "pCube4_AttrMarkedShape" -p "pCube4_AttrMarked";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "pCube5" -p "pCube4_AttrMarked";
	setAttr ".t" -type "double3" 0 2.9181213705469879 0 ;
createNode mesh -n "pCubeShape5" -p "|World_Root|pCube4_AttrMarked|pCube5";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "IK_Ctrl" -p "World_Root";
	setAttr ".t" -type "double3" -3.8359970113906416 6.361637895492386 -0.67156166760067837 ;
createNode locator -n "IK_CtrlShape" -p "|World_Root|IK_Ctrl";
	setAttr -k off ".v";
createNode ikHandle -n "ikHandle1" -p "|World_Root|IK_Ctrl";
	setAttr ".t" -type "double3" 0 8.8817841970012523e-016 0 ;
	setAttr ".r" -type "double3" 0 0 89.999999999999986 ;
	setAttr ".roc" yes;
createNode transform -n "World_Root2_chSet";
createNode joint -n "joint1" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" -3.6433793663688054 -0.012185215272137159 0 ;
	setAttr ".r" -type "double3" -4.2665688995361545e-007 -16.495013417216473 1.7309582018146501 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 89.999999999999986 ;
	setAttr ".radi" 0.61844869604190589;
createNode joint -n "joint2_Ctrl" -p "|World_Root2_chSet|joint1";
	setAttr ".r" -type "double3" 1.0439685387335298e-014 42.983836676891734 3.7109899896632391e-013 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".pa" -type "double3" 0 89.999999897160009 0 ;
	setAttr ".radi" 0.63448438061649026;
createNode joint -n "joint3_AttrMarked" -p "|World_Root2_chSet|joint1|joint2_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 3.6000313585854782 7.9936754073483622e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -89.999999999999986 ;
	setAttr ".radi" 0.63448438061649026;
	setAttr -k on ".MarkerAttr";
createNode ikEffector -n "effector1" -p "|World_Root2_chSet|joint1|joint2_Ctrl";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 3.6000313585854782 7.9936754073483622e-016 0 ;
	setAttr ".hd" yes;
createNode joint -n "joint4" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" 4.0107393733741361 -0.080536935208317006 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 89.999999999999986 ;
	setAttr ".radi" 0.63323309947840856;
createNode joint -n "joint5_AttrMarked" -p "|World_Root2_chSet|joint4";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".radi" 0.63823194373271785;
	setAttr -k on ".MarkerAttr";
createNode joint -n "joint6_Ctrl" -p "|World_Root2_chSet|joint4|joint5_AttrMarked";
	setAttr ".t" -type "double3" 3.672484245499211 8.15455313385274e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -60.688103539485006 ;
	setAttr ".radi" 0.67751490982158769;
createNode joint -n "joint7_AttrMarked" -p "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 4.4319549232173605 6.6613381477509392e-016 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -54.952902284820269 ;
	setAttr ".radi" 0.74790222180931787;
	setAttr -k on ".MarkerAttr";
createNode joint -n "joint8" -p "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked";
	setAttr ".t" -type "double3" 5.7927762883134761 -1.7763568394002505e-015 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 180 0 -65.283039528467512 ;
	setAttr ".radi" 0.58227284371501231;
createNode joint -n "joint9" -p "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8";
	setAttr ".t" -type "double3" 2.590608311823571 -2.3175905639050143e-015 -2.8349688781380116e-031 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 180 89.075954647227121 ;
	setAttr ".radi" 0.58227284371501231;
createNode transform -n "pCube3" -p "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl";
	setAttr ".t" -type "double3" -12.191867470387797 5.0737014995313521 0.11357408139026504 ;
	setAttr ".r" -type "double3" 0 0 -29.31189646051498 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1 ;
createNode mesh -n "pCubeShape3" -p "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|pCube3";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "nurbsCircle1" -p "World_Root2_chSet";
createNode nurbsCurve -n "nurbsCircleShape1" -p "|World_Root2_chSet|nurbsCircle1";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "Spine_Ctrl" -p "World_Root2_chSet";
createNode nurbsCurve -n "Spine_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "L_Foot_MarkerAttr_Ctrl" -p "|World_Root2_chSet|Spine_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr -k on ".MarkerAttr" -type "string" "right";
createNode nurbsCurve -n "L_Foot_MarkerAttr_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "pCube2" -p "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl";
	setAttr ".t" -type "double3" 6.5029468039693565 -21.132228282434319 0.11357408139026504 ;
createNode mesh -n "pCubeShape2" -p "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl|pCube2";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "L_Wrist_Ctrl" -p "|World_Root2_chSet|Spine_Ctrl";
createNode nurbsCurve -n "L_Wrist_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "L_Pole_thingy" -p "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl";
	setAttr ".t" -type "double3" 15.607020480148948 0.71082667375467778 0 ;
createNode locator -n "L_Pole_thingyShape" -p "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl|L_Pole_thingy";
	setAttr -k off ".v";
createNode transform -n "R_Wrist_Ctrl" -p "|World_Root2_chSet|Spine_Ctrl";
createNode nurbsCurve -n "R_Wrist_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		-2.4596483629390118 7.1274456003626816e-016 0
		-1.7392340367685659 -1.7392340367685648 0
		-7.411400545420654e-016 -2.4596483629390118 0
		1.7392340367685644 -1.7392340367685657 0
		2.4596483629390118 -1.3210819338553792e-015 0
		1.739234036768567 1.7392340367685644 0
		-2.8061646809873577e-016 2.4596483629390118 0
		-1.7392340367685657 1.7392340367685657 0
		;
createNode transform -n "R_Pole_AttrMarked_Ctrl" -p "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr ".t" -type "double3" 15.607020480148948 -6.4914034049727007 0 ;
	setAttr -k on ".MarkerAttr";
createNode locator -n "R_Pole_AttrMarked_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl";
	setAttr -k off ".v";
createNode transform -n "pCube1" -p "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl";
	setAttr ".t" -type "double3" -9.104073676179592 -9.2356576381542048 0.11357408139026504 ;
createNode mesh -n "pCubeShape1" -p "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl|pCube1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "R_Pole_Ctrl" -p "|World_Root2_chSet|Spine_Ctrl";
createNode locator -n "R_Pole_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl";
	setAttr -k off ".v";
createNode transform -n "L_Pole_Ctrl" -p "|World_Root2_chSet|Spine_Ctrl";
createNode locator -n "L_Pole_CtrlShape" -p "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl";
	setAttr -k off ".v";
createNode transform -n "camera1" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" 19.151003247046212 0 0 ;
createNode camera -n "cameraShape1" -p "|World_Root2_chSet|camera1";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.41732 0.94488 ;
	setAttr ".ff" 0;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
createNode transform -n "camera2" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" 19.151003247046212 4.0544916784287022 0 ;
createNode camera -n "cameraShape2" -p "|World_Root2_chSet|camera2";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.41732 0.94488 ;
	setAttr ".ff" 0;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
createNode transform -n "pointLight1" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" 25.275873654885309 0 0 ;
createNode pointLight -n "pointLightShape1" -p "|World_Root2_chSet|pointLight1";
	setAttr -k off ".v";
createNode transform -n "pointLight2" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" 25.275873654885309 4.0544916784287022 0 ;
createNode pointLight -n "pointLightShape2" -p "|World_Root2_chSet|pointLight2";
	setAttr -k off ".v";
createNode transform -n "nurbsSphere1" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" -24.092390838288175 1.6667691774916349 0 ;
createNode nurbsSurface -n "nurbsSphereShape1" -p "|World_Root2_chSet|nurbsSphere1";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".dvu" 0;
	setAttr ".dvv" 0;
	setAttr ".cpr" 4;
	setAttr ".cps" 4;
	setAttr ".cc" -type "nurbsSurface" 
		3 3 0 2 no 
		9 0 0 0 1 2 3 4 4 4
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		
		77
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		2.0257455296216898e-016 4.0514910592433874e-016 -2.1109267692085179
		0.42200970539075888 0.42200970539075966 -2.1109267692085179
		0.59681184881668603 2.0643722135865716e-018 -2.1109267692085179
		0.42200970539075927 -0.42200970539075922 -2.1109267692085179
		2.4309461079423687e-016 -0.59681184881668603 -2.1109267692085179
		-0.42200970539075905 -0.42200970539075944 -2.1109267692085179
		-0.59681184881668614 -2.4998452555986587e-016 -2.1109267692085179
		-0.42200970539075938 0.42200970539075888 -2.1109267692085179
		-3.9070227628161173e-016 0.59681184881668603 -2.1109267692085179
		0.42200970539075888 0.42200970539075966 -2.1109267692085179
		0.59681184881668603 2.0643722135865716e-018 -2.1109267692085179
		0.42200970539075927 -0.42200970539075922 -2.1109267692085179
		1.3012385454715274 1.3012385454715294 -1.6541467556458691
		1.8402291988884747 -3.2306525664204904e-016 -1.6541467556458691
		1.3012385454715281 -1.3012385454715281 -1.6541467556458691
		4.2013527419628378e-016 -1.8402291988884747 -1.6541467556458691
		-1.3012385454715278 -1.3012385454715285 -1.6541467556458691
		-1.8402291988884747 -4.4137986301385242e-016 -1.6541467556458691
		-1.3012385454715285 1.3012385454715274 -1.6541467556458691
		-8.7527358377944893e-016 1.8402291988884747 -1.6541467556458691
		1.3012385454715274 1.3012385454715294 -1.6541467556458691
		1.8402291988884747 -3.2306525664204904e-016 -1.6541467556458691
		1.3012385454715281 -1.3012385454715281 -1.6541467556458691
		1.8306008607330384 1.8306008607330413 2.5865343080019434e-017
		2.5888605645405263 -6.1240201568640807e-016 2.5865343080019434e-017
		1.8306008607330393 -1.8306008607330395 2.5865343080019434e-017
		4.3314304304600151e-016 -2.5888605645405263 2.5865343080019434e-017
		-1.8306008607330393 -1.8306008607330395 2.5865343080019434e-017
		-2.5888605645405267 -4.6303023222488329e-016 2.5865343080019434e-017
		-1.8306008607330395 1.8306008607330384 2.5865343080019434e-017
		-1.0734380790139113e-015 2.5888605645405263 2.5865343080019434e-017
		1.8306008607330384 1.8306008607330413 2.5865343080019434e-017
		2.5888605645405263 -6.1240201568640807e-016 2.5865343080019434e-017
		1.8306008607330393 -1.8306008607330395 2.5865343080019434e-017
		1.3012385454715281 1.3012385454715294 1.6541467556458695
		1.8402291988884751 -5.4755719878115377e-016 1.6541467556458695
		1.3012385454715285 -1.3012385454715287 1.6541467556458695
		1.9564333205717942e-016 -1.8402291988884751 1.6541467556458695
		-1.3012385454715285 -1.3012385454715287 1.6541467556458695
		-1.8402291988884751 -2.1688792087474788e-016 1.6541467556458695
		-1.3012385454715285 1.3012385454715281 1.6541467556458695
		-6.5078164164034464e-016 1.8402291988884751 1.6541467556458695
		1.3012385454715281 1.3012385454715294 1.6541467556458695
		1.8402291988884751 -5.4755719878115377e-016 1.6541467556458695
		1.3012385454715285 -1.3012385454715287 1.6541467556458695
		0.42200970539075938 0.42200970539075966 2.1109267692085174
		0.59681184881668625 -2.8441930797718016e-016 2.1109267692085174
		0.42200970539075927 -0.4220097053907596 2.1109267692085174
		-4.3389069396529736e-017 -0.59681184881668625 2.1109267692085174
		-0.42200970539075949 -0.42200970539075938 2.1109267692085174
		-0.59681184881668636 3.6499154630900733e-017 2.1109267692085174
		-0.42200970539075938 0.42200970539075938 2.1109267692085174
		-1.0421859609084527e-016 0.59681184881668625 2.1109267692085174
		0.42200970539075938 0.42200970539075966 2.1109267692085174
		0.59681184881668625 -2.8441930797718016e-016 2.1109267692085174
		0.42200970539075927 -0.4220097053907596 2.1109267692085174
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		3.6729436284540931e-016 1.6471980988324028e-016 2.1109267692085179
		
		;
	setAttr ".nufa" 4.5;
	setAttr ".nvfa" 4.5;
createNode transform -n "pCube4_AttrMarked_Bingo" -p "World_Root2_chSet";
	addAttr -ci true -sn "MarkerAttr" -ln "MarkerAttr" -dt "string";
	setAttr -k on ".MarkerAttr" -type "string" "right";
createNode mesh -n "pCube4_AttrMarked_BingoShape" -p "pCube4_AttrMarked_Bingo";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "pCube5" -p "pCube4_AttrMarked_Bingo";
	setAttr ".t" -type "double3" 0 2.9181213705469879 0 ;
createNode mesh -n "pCubeShape5" -p "|World_Root2_chSet|pCube4_AttrMarked_Bingo|pCube5";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.375
		 0.25 0.625 0.25 0.375 0.5 0.625 0.5 0.375 0.75 0.625 0.75 0.375 1 0.625 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
createNode transform -n "IK_Ctrl" -p "World_Root2_chSet";
	setAttr ".t" -type "double3" -3.8359970113906416 6.361637895492386 -0.67156166760067837 ;
createNode locator -n "IK_CtrlShape" -p "|World_Root2_chSet|IK_Ctrl";
	setAttr -k off ".v";
createNode ikHandle -n "ikHandle1" -p "|World_Root2_chSet|IK_Ctrl";
	setAttr ".t" -type "double3" 0 8.8817841970012523e-016 0 ;
	setAttr ".r" -type "double3" 0 0 89.999999999999986 ;
	setAttr ".roc" yes;
createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
createNode ikRPsolver -n "ikRPsolver";
createNode makeNurbSphere -n "makeNurbSphere1";
	setAttr ".ax" -type "double3" 0 0 1 ;
	setAttr ".r" 2.1109267692085179;
createNode makeNurbCircle -n "makeNurbCircle1";
	setAttr ".r" 2.2195102542155296;
createNode polyCube -n "polyCube1";
	setAttr ".w" 1.6934999976697931;
	setAttr ".h" 1.1646131526110912;
	setAttr ".d" 3.5094196260200547;
	setAttr ".cuv" 4;
createNode script -n "uiConfigurationScriptNode";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"top\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n"
		+ "                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 8192\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -rendererName \"base_OpenGL_Renderer\" \n"
		+ "                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -joints 1\n                -ikHandles 1\n"
		+ "                -deformers 1\n                -dynamics 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -shadows 0\n                $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n"
		+ "            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 1\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 8192\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n            -rendererName \"base_OpenGL_Renderer\" \n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n"
		+ "            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n"
		+ "            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -shadows 0\n            $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"side\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n"
		+ "                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 8192\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -rendererName \"base_OpenGL_Renderer\" \n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n"
		+ "                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -dimensions 1\n"
		+ "                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -shadows 0\n                $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 1\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n"
		+ "            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 8192\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n            -rendererName \"base_OpenGL_Renderer\" \n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n"
		+ "            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -shadows 0\n            $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" == $panelName) {\n"
		+ "\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"front\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 8192\n"
		+ "                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -rendererName \"base_OpenGL_Renderer\" \n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n"
		+ "                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -shadows 0\n                $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 1\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 8192\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n"
		+ "            -rendererName \"base_OpenGL_Renderer\" \n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -fluids 1\n"
		+ "            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -shadows 0\n            $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n"
		+ "                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 8192\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -rendererName \"base_OpenGL_Renderer\" \n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n"
		+ "                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -fluids 1\n"
		+ "                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -shadows 0\n                $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n"
		+ "            -bufferMode \"double\" \n            -twoSidedLighting 1\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 8192\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -maxConstantTransparency 1\n            -rendererName \"base_OpenGL_Renderer\" \n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n"
		+ "            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n"
		+ "            -shadows 0\n            $editorName;\nmodelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            outlinerEditor -e \n                -docTag \"isolOutln_fromSeln\" \n                -showShapes 0\n                -showAttributes 0\n                -showConnected 0\n                -showAnimCurvesOnly 0\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 1\n                -showAssets 1\n                -showContainedOnly 1\n                -showPublishedAsConnected 0\n                -showContainerContents 1\n                -ignoreDagHierarchy 0\n"
		+ "                -expandConnections 0\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 0\n                -highlightActive 1\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"defaultSetFilter\" \n                -showSetMembers 1\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n"
		+ "                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 0\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n"
		+ "            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"graphEditor\" -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n"
		+ "                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n"
		+ "                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n"
		+ "                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n"
		+ "                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dopeSheetPanel\" -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels `;\n"
		+ "\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n"
		+ "                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n"
		+ "                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n"
		+ "                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n"
		+ "                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" == $panelName) {\n"
		+ "\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"clipEditorPanel\" -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 0 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n"
		+ "                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"sequenceEditorPanel\" -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 1 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"hyperGraphPanel\" -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n"
		+ "                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n"
		+ "            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"hyperShadePanel\" -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"visorPanel\" -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"createNodePanel\" -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Texture Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"polyTexturePlacementPanel\" -l (localizedPanelLabel(\"UV Texture Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Texture Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"renderWindowPanel\" -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"blendShapePanel\" (localizedPanelLabel(\"Blend Shape\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\tblendShapePanel -unParent -l (localizedPanelLabel(\"Blend Shape\")) -mbv $menusOkayInPanels ;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tblendShapePanel -edit -l (localizedPanelLabel(\"Blend Shape\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dynRelEdPanel\" -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"relationshipPanel\" -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"referenceEditorPanel\" -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"componentEditorPanel\" -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dynPaintScriptedPanelType\" -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"scriptEditorPanel\" -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"Stereo\" -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels `;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n"
		+ "                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 8192\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n"
		+ "                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -shadows 0\n"
		+ "                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                $editorName;\nstereoCameraView -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n"
		+ "                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 8192\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -maxConstantTransparency 1\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n"
		+ "                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -shadows 0\n                -displayMode \"centerEye\" \n"
		+ "                -viewColor 0 0 0 1 \n                $editorName;\nstereoCameraView -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-defaultImage \"vacantCell.xpm\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"vertical2\\\" -ps 1 34 100 -ps 2 66 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Outliner\")) \n\t\t\t\t\t\"outlinerPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\\\"Outliner\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\noutlinerEditor -e \\n    -docTag \\\"isolOutln_fromSeln\\\" \\n    -showShapes 0\\n    -showAttributes 0\\n    -showConnected 0\\n    -showAnimCurvesOnly 0\\n    -showMuteInfo 0\\n    -organizeByLayer 1\\n    -showAnimLayerWeight 1\\n    -autoExpandLayers 1\\n    -autoExpand 0\\n    -showDagOnly 1\\n    -showAssets 1\\n    -showContainedOnly 1\\n    -showPublishedAsConnected 0\\n    -showContainerContents 1\\n    -ignoreDagHierarchy 0\\n    -expandConnections 0\\n    -showUpstreamCurves 1\\n    -showUnitlessCurves 1\\n    -showCompounds 1\\n    -showLeafs 1\\n    -showNumericAttrsOnly 0\\n    -highlightActive 1\\n    -autoSelectNewObjects 0\\n    -doNotSelectNewObjects 0\\n    -dropIsParent 1\\n    -transmitFilters 0\\n    -setFilter \\\"defaultSetFilter\\\" \\n    -showSetMembers 1\\n    -allowMultiSelection 1\\n    -alwaysToggleSelect 0\\n    -directSelect 0\\n    -displayMode \\\"DAG\\\" \\n    -expandObjects 0\\n    -setsIgnoreFilters 1\\n    -containersIgnoreFilters 0\\n    -editAttrName 0\\n    -showAttrValues 0\\n    -highlightSecondary 0\\n    -showUVAttrsOnly 0\\n    -showTextureNodesOnly 0\\n    -attrAlphaOrder \\\"default\\\" \\n    -animLayerFilterOptions \\\"allAffecting\\\" \\n    -sortOrder \\\"none\\\" \\n    -longNames 0\\n    -niceNames 1\\n    -showNamespace 1\\n    -showPinIcons 0\\n    -mapMotionTrails 0\\n    $editorName\"\n"
		+ "\t\t\t\t\t\"outlinerPanel -edit -l (localizedPanelLabel(\\\"Outliner\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\noutlinerEditor -e \\n    -docTag \\\"isolOutln_fromSeln\\\" \\n    -showShapes 0\\n    -showAttributes 0\\n    -showConnected 0\\n    -showAnimCurvesOnly 0\\n    -showMuteInfo 0\\n    -organizeByLayer 1\\n    -showAnimLayerWeight 1\\n    -autoExpandLayers 1\\n    -autoExpand 0\\n    -showDagOnly 1\\n    -showAssets 1\\n    -showContainedOnly 1\\n    -showPublishedAsConnected 0\\n    -showContainerContents 1\\n    -ignoreDagHierarchy 0\\n    -expandConnections 0\\n    -showUpstreamCurves 1\\n    -showUnitlessCurves 1\\n    -showCompounds 1\\n    -showLeafs 1\\n    -showNumericAttrsOnly 0\\n    -highlightActive 1\\n    -autoSelectNewObjects 0\\n    -doNotSelectNewObjects 0\\n    -dropIsParent 1\\n    -transmitFilters 0\\n    -setFilter \\\"defaultSetFilter\\\" \\n    -showSetMembers 1\\n    -allowMultiSelection 1\\n    -alwaysToggleSelect 0\\n    -directSelect 0\\n    -displayMode \\\"DAG\\\" \\n    -expandObjects 0\\n    -setsIgnoreFilters 1\\n    -containersIgnoreFilters 0\\n    -editAttrName 0\\n    -showAttrValues 0\\n    -highlightSecondary 0\\n    -showUVAttrsOnly 0\\n    -showTextureNodesOnly 0\\n    -attrAlphaOrder \\\"default\\\" \\n    -animLayerFilterOptions \\\"allAffecting\\\" \\n    -sortOrder \\\"none\\\" \\n    -longNames 0\\n    -niceNames 1\\n    -showNamespace 1\\n    -showPinIcons 0\\n    -mapMotionTrails 0\\n    $editorName\"\n"
		+ "\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 1\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 8192\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -maxConstantTransparency 1\\n    -rendererName \\\"base_OpenGL_Renderer\\\" \\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -shadows 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 1\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 8192\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -maxConstantTransparency 1\\n    -rendererName \\\"base_OpenGL_Renderer\\\" \\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -shadows 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        setFocus `paneLayout -q -p1 $gMainPane`;\n        sceneUIReplacement -deleteRemaining;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels yes -displayOrthographicLabels yes -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 24 -ast 1 -aet 48 ";
	setAttr ".st" 6;
createNode character -n "TestChSet";
	addAttr -ci true -h true -sn "aal" -ln "attributeAliasList" -dt "attributeAlias";
	setAttr -s 30 ".dnsm";
	setAttr -s 30 ".lv[2:30]"  -19.204731212714822 15.607020480148948 0 
		-22.477659779425675 15.607020480148948 0 -15.986256374452974 1.7763568394002505e-015 
		0 -23.188486453180353 1.7763568394002505e-015 0 -8.0639764503451907 0 0 7.3052855397756017e-016 
		3.2900081234768472 0 7.9399596303302988e-016 3.5758399232492319 0.11357408139026504 
		8.2801814611384703 -9.104073676179592 0 32.295623993885428 -15.607020480148948 0 
		2.1516474836710167 -15.607020480148948;
	setAttr -s 30 ".lv";
	setAttr ".am" -type "characterMapping" 30 "World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.translateZ" 
		1 1 "World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.translateY" 1 2 "World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.translateX" 
		1 3 "World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.translateZ" 1 4 "World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.translateY" 
		1 5 "World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.translateX" 1 6 "World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.translateZ" 
		1 7 "World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.translateY" 1 8 "World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.translateX" 
		1 9 "World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.translateZ" 1 10 "World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.translateY" 
		1 11 "World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.translateX" 1 12 "World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.translateZ" 
		1 13 "World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.translateY" 1 
		14 "World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.translateX" 1 15 "World_Root2_chSet|joint1|joint2_Ctrl.translateZ" 
		1 16 "World_Root2_chSet|joint1|joint2_Ctrl.translateY" 1 17 "World_Root2_chSet|joint1|joint2_Ctrl.translateX" 
		1 18 "World_Root2_chSet|joint4|joint5_AttrMarked.translateZ" 1 19 "World_Root2_chSet|joint4|joint5_AttrMarked.translateY" 
		1 20 "World_Root2_chSet|joint4|joint5_AttrMarked.translateX" 1 21 "pCube4_AttrMarked_Bingo.translateZ" 
		1 22 "pCube4_AttrMarked_Bingo.translateY" 1 23 "pCube4_AttrMarked_Bingo.translateX" 
		1 24 "World_Root2_chSet|Spine_Ctrl.translateZ" 1 25 "World_Root2_chSet|Spine_Ctrl.translateY" 
		1 26 "World_Root2_chSet|Spine_Ctrl.translateX" 1 27 "World_Root2_chSet|nurbsCircle1.translateZ" 
		1 28 "World_Root2_chSet|nurbsCircle1.translateY" 1 29 "World_Root2_chSet|nurbsCircle1.translateX" 
		1 30  ;
	setAttr ".aal" -type "attributeAlias" {"L_Wrist_Ctrl_translateZ","linearValues[10]"
		,"L_Wrist_Ctrl_translateY","linearValues[11]","L_Wrist_Ctrl_translateX","linearValues[12]"
		,"L_Foot_MarkerAttr_Ctrl_translateZ","linearValues[13]","L_Foot_MarkerAttr_Ctrl_translateY"
		,"linearValues[14]","L_Foot_MarkerAttr_Ctrl_translateX","linearValues[15]","joint2_Ctrl_translateZ"
		,"linearValues[16]","joint2_Ctrl_translateY","linearValues[17]","joint2_Ctrl_translateX"
		,"linearValues[18]","joint5_AttrMarked_translateZ","linearValues[19]","L_Pole_Ctrl_translateZ"
		,"linearValues[1]","joint5_AttrMarked_translateY","linearValues[20]","joint5_AttrMarked_translateX"
		,"linearValues[21]","pCube4_AttrMarked_Bingo_translateZ","linearValues[22]","pCube4_AttrMarked_Bingo_translateY"
		,"linearValues[23]","pCube4_AttrMarked_Bingo_translateX","linearValues[24]","Spine_Ctrl_translateZ"
		,"linearValues[25]","Spine_Ctrl_translateY","linearValues[26]","Spine_Ctrl_translateX"
		,"linearValues[27]","nurbsCircle1_translateZ","linearValues[28]","nurbsCircle1_translateY"
		,"linearValues[29]","L_Pole_Ctrl_translateY","linearValues[2]","nurbsCircle1_translateX"
		,"linearValues[30]","L_Pole_Ctrl_translateX","linearValues[3]","R_Pole_Ctrl_translateZ"
		,"linearValues[4]","R_Pole_Ctrl_translateY","linearValues[5]","R_Pole_Ctrl_translateX"
		,"linearValues[6]","R_Wrist_Ctrl_translateZ","linearValues[7]","R_Wrist_Ctrl_translateY"
		,"linearValues[8]","R_Wrist_Ctrl_translateX","linearValues[9]"} ;
createNode script -n "sceneReviewData";
	setAttr ".b" -type "string" "try:\r\timport Red9.core.Red9_Tools as r9Tools;\r\tr9Tools.SceneReviewerUI.show();\rexcept:\r\tpass";
	setAttr ".st" 1;
	setAttr ".stp" 1;
select -ne :time1;
	addAttr -ci true -sn "sceneReport" -ln "sceneReport" -dt "string";
	setAttr ".o" 1;
	setAttr ".unw" 1;
	setAttr ".sceneReport" -type "string" "{\"date\": \"Sun Nov 25 20:41:21 2012\", \"comment\": \"UnitTest support file:\\n======================\\nThis is designed to run the Red9_CoreUtilTests.py\\ntests that validate the r9Core.FilterNode() class\", \"history\": \"\", \"author\": \"Red\"}";
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :initialShadingGroup;
	setAttr -s 12 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultShaderList1;
	setAttr -s 2 ".s";
select -ne :lightList1;
	setAttr -s 6 ".l";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :renderGlobalsList1;
select -ne :defaultLightSet;
	setAttr -s 6 ".dsm";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :defaultHardwareRenderGlobals;
	setAttr ".fn" -type "string" "im";
	setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
select -ne :characterPartition;
select -ne :ikSystem;
connectAttr "|World_Root|joint1.s" "|World_Root|joint1|joint2_Ctrl.is";
connectAttr "|World_Root|joint1|joint2_Ctrl.s" "|World_Root|joint1|joint2_Ctrl|joint3_AttrMarked.is"
		;
connectAttr "|World_Root|joint1|joint2_Ctrl|joint3_AttrMarked.tx" "|World_Root|joint1|joint2_Ctrl|effector1.tx"
		;
connectAttr "|World_Root|joint1|joint2_Ctrl|joint3_AttrMarked.ty" "|World_Root|joint1|joint2_Ctrl|effector1.ty"
		;
connectAttr "|World_Root|joint1|joint2_Ctrl|joint3_AttrMarked.tz" "|World_Root|joint1|joint2_Ctrl|effector1.tz"
		;
connectAttr "|World_Root|joint4.s" "|World_Root|joint4|joint5_AttrMarked.is";
connectAttr "|World_Root|joint4|joint5_AttrMarked.s" "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl.is"
		;
connectAttr "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl.s" "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked.is"
		;
connectAttr "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked.s" "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8.is"
		;
connectAttr "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8.s" "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8|joint9.is"
		;
connectAttr "makeNurbCircle1.oc" "|World_Root|nurbsCircle1|nurbsCircleShape1.cr"
		;
connectAttr "polyCube1.out" "|World_Root|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl|pCube1|pCubeShape1.i"
		;
connectAttr "makeNurbSphere1.os" "|World_Root|nurbsSphere1|nurbsSphereShape1.cr"
		;
connectAttr "|World_Root|joint1.msg" "|World_Root|IK_Ctrl|ikHandle1.hsj";
connectAttr "|World_Root|joint1|joint2_Ctrl|effector1.hp" "|World_Root|IK_Ctrl|ikHandle1.hee"
		;
connectAttr "ikRPsolver.msg" "|World_Root|IK_Ctrl|ikHandle1.hsv";
connectAttr "|World_Root2_chSet|joint1.s" "|World_Root2_chSet|joint1|joint2_Ctrl.is"
		;
connectAttr "TestChSet.lv[16]" "|World_Root2_chSet|joint1|joint2_Ctrl.tz";
connectAttr "TestChSet.lv[17]" "|World_Root2_chSet|joint1|joint2_Ctrl.ty";
connectAttr "TestChSet.lv[18]" "|World_Root2_chSet|joint1|joint2_Ctrl.tx";
connectAttr "|World_Root2_chSet|joint1|joint2_Ctrl.s" "|World_Root2_chSet|joint1|joint2_Ctrl|joint3_AttrMarked.is"
		;
connectAttr "|World_Root2_chSet|joint4.s" "|World_Root2_chSet|joint4|joint5_AttrMarked.is"
		;
connectAttr "TestChSet.lv[19]" "|World_Root2_chSet|joint4|joint5_AttrMarked.tz";
connectAttr "TestChSet.lv[20]" "|World_Root2_chSet|joint4|joint5_AttrMarked.ty";
connectAttr "TestChSet.lv[21]" "|World_Root2_chSet|joint4|joint5_AttrMarked.tx";
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked.s" "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl.is"
		;
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl.s" "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked.is"
		;
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked.s" "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8.is"
		;
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8.s" "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|joint7_AttrMarked|joint8|joint9.is"
		;
connectAttr "TestChSet.lv[28]" "|World_Root2_chSet|nurbsCircle1.tz";
connectAttr "TestChSet.lv[29]" "|World_Root2_chSet|nurbsCircle1.ty";
connectAttr "TestChSet.lv[30]" "|World_Root2_chSet|nurbsCircle1.tx";
connectAttr "TestChSet.lv[25]" "|World_Root2_chSet|Spine_Ctrl.tz";
connectAttr "TestChSet.lv[26]" "|World_Root2_chSet|Spine_Ctrl.ty";
connectAttr "TestChSet.lv[27]" "|World_Root2_chSet|Spine_Ctrl.tx";
connectAttr "TestChSet.lv[13]" "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.tz"
		;
connectAttr "TestChSet.lv[14]" "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.ty"
		;
connectAttr "TestChSet.lv[15]" "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.tx"
		;
connectAttr "TestChSet.lv[10]" "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.tz";
connectAttr "TestChSet.lv[11]" "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.ty";
connectAttr "TestChSet.lv[12]" "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.tx";
connectAttr "TestChSet.lv[7]" "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.tz";
connectAttr "TestChSet.lv[8]" "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.ty";
connectAttr "TestChSet.lv[9]" "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.tx";
connectAttr "TestChSet.lv[4]" "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.tz";
connectAttr "TestChSet.lv[5]" "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.ty";
connectAttr "TestChSet.lv[6]" "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.tx";
connectAttr "TestChSet.lv[1]" "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.tz";
connectAttr "TestChSet.lv[2]" "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.ty";
connectAttr "TestChSet.lv[3]" "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.tx";
connectAttr "TestChSet.lv[22]" "pCube4_AttrMarked_Bingo.tz";
connectAttr "TestChSet.lv[23]" "pCube4_AttrMarked_Bingo.ty";
connectAttr "TestChSet.lv[24]" "pCube4_AttrMarked_Bingo.tx";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.tz" "TestChSet.dnsm[0]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.ty" "TestChSet.dnsm[1]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Pole_Ctrl.tx" "TestChSet.dnsm[2]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.tz" "TestChSet.dnsm[3]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.ty" "TestChSet.dnsm[4]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Pole_Ctrl.tx" "TestChSet.dnsm[5]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.tz" "TestChSet.dnsm[6]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.ty" "TestChSet.dnsm[7]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl.tx" "TestChSet.dnsm[8]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.tz" "TestChSet.dnsm[9]";
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.ty" "TestChSet.dnsm[10]"
		;
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Wrist_Ctrl.tx" "TestChSet.dnsm[11]"
		;
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.tz" "TestChSet.dnsm[12]"
		;
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.ty" "TestChSet.dnsm[13]"
		;
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl.tx" "TestChSet.dnsm[14]"
		;
connectAttr "|World_Root2_chSet|joint1|joint2_Ctrl.tz" "TestChSet.dnsm[15]";
connectAttr "|World_Root2_chSet|joint1|joint2_Ctrl.ty" "TestChSet.dnsm[16]";
connectAttr "|World_Root2_chSet|joint1|joint2_Ctrl.tx" "TestChSet.dnsm[17]";
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked.tz" "TestChSet.dnsm[18]"
		;
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked.ty" "TestChSet.dnsm[19]"
		;
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked.tx" "TestChSet.dnsm[20]"
		;
connectAttr "pCube4_AttrMarked_Bingo.tz" "TestChSet.dnsm[21]";
connectAttr "pCube4_AttrMarked_Bingo.ty" "TestChSet.dnsm[22]";
connectAttr "pCube4_AttrMarked_Bingo.tx" "TestChSet.dnsm[23]";
connectAttr "|World_Root2_chSet|Spine_Ctrl.tz" "TestChSet.dnsm[24]";
connectAttr "|World_Root2_chSet|Spine_Ctrl.ty" "TestChSet.dnsm[25]";
connectAttr "|World_Root2_chSet|Spine_Ctrl.tx" "TestChSet.dnsm[26]";
connectAttr "|World_Root2_chSet|nurbsCircle1.tz" "TestChSet.dnsm[27]";
connectAttr "|World_Root2_chSet|nurbsCircle1.ty" "TestChSet.dnsm[28]";
connectAttr "|World_Root2_chSet|nurbsCircle1.tx" "TestChSet.dnsm[29]";
connectAttr "|World_Root|nurbsSphere1|nurbsSphereShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl|pCube1|pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl|pCube2|pCubeShape2.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root|joint4|joint5_AttrMarked|joint6_Ctrl|pCube3|pCubeShape3.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "pCube4_AttrMarkedShape.iog" ":initialShadingGroup.dsm" -na;
connectAttr "|World_Root|pCube4_AttrMarked|pCube5|pCubeShape5.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root2_chSet|joint4|joint5_AttrMarked|joint6_Ctrl|pCube3|pCubeShape3.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root2_chSet|Spine_Ctrl|L_Foot_MarkerAttr_Ctrl|pCube2|pCubeShape2.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root2_chSet|Spine_Ctrl|R_Wrist_Ctrl|R_Pole_AttrMarked_Ctrl|pCube1|pCubeShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root2_chSet|nurbsSphere1|nurbsSphereShape1.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "pCube4_AttrMarked_BingoShape.iog" ":initialShadingGroup.dsm" -na;
connectAttr "|World_Root2_chSet|pCube4_AttrMarked_Bingo|pCube5|pCubeShape5.iog" ":initialShadingGroup.dsm"
		 -na;
connectAttr "|World_Root|pointLight1|pointLightShape1.ltd" ":lightList1.l" -na;
connectAttr "|World_Root|pointLight2|pointLightShape2.ltd" ":lightList1.l" -na;
connectAttr "pointLightShape3.ltd" ":lightList1.l" -na;
connectAttr "pointLightShape4.ltd" ":lightList1.l" -na;
connectAttr "|World_Root2_chSet|pointLight1|pointLightShape1.ltd" ":lightList1.l"
		 -na;
connectAttr "|World_Root2_chSet|pointLight2|pointLightShape2.ltd" ":lightList1.l"
		 -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "|World_Root|pointLight1.iog" ":defaultLightSet.dsm" -na;
connectAttr "|World_Root|pointLight2.iog" ":defaultLightSet.dsm" -na;
connectAttr "pointLight3.iog" ":defaultLightSet.dsm" -na;
connectAttr "pointLight4.iog" ":defaultLightSet.dsm" -na;
connectAttr "|World_Root2_chSet|pointLight1.iog" ":defaultLightSet.dsm" -na;
connectAttr "|World_Root2_chSet|pointLight2.iog" ":defaultLightSet.dsm" -na;
connectAttr "TestChSet.pa" ":characterPartition.st" -na;
connectAttr "ikRPsolver.msg" ":ikSystem.sol" -na;
// End of FilterNode_baseTests.ma
