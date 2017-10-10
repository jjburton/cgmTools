"""
Copyright (C) 2011 Autodesk, Inc.  All rights reserved.

Developer Tip:
To auto-reload the entire package when maya is running, a shelf button can be
created with the following content.

import sys
bulletScriptPath = '<Bullet src location>/Bullet/scripts'
if (not bulletScriptPath in sys.path):
    sys.path.insert(0,bulletScriptPath)

import maya.app.mayabullet
import maya.app.mayabullet.BulletUtils
import maya.app.mayabullet.CommandWithOptionVars
import maya.app.mayabullet.Ragdoll
import maya.app.mayabullet.RigidBody
import maya.app.mayabullet.RigidBodyConstraint
import maya.app.mayabullet.SoftBody
import maya.app.mayabullet.SoftBodyConstraint

reload(maya.app.mayabullet)
reload(maya.app.mayabullet.BulletUtils)
reload(maya.app.mayabullet.CommandWithOptionVars)
reload(maya.app.mayabullet.Ragdoll)
reload(maya.app.mayabullet.RigidBody)
reload(maya.app.mayabullet.RigidBodyConstraint)
reload(maya.app.mayabullet.SoftBody)
reload(maya.app.mayabullet.SoftBodyConstraint)
"""

logger = None


