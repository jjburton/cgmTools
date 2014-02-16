import maya.cmds as mc
from cgm.core import cgm_Meta as cgmMeta

from cgm.core import cgm_General as cgmGeneral


#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



def add_UV_grid_location_attr(*args,**kws):
	class fncWrap(cgmGeneral.cgmFuncCls):
		''' Some times there is a need to know what grid space your UVs are in.
		UVs are not always going to be in the 0-1 grid space and are placed 
		in another grid space.(using Mari) This function checks where they are and adds 
		and attrabut with that data.'
		kws - Object''' 
	
		def __init__(self,*args,**kws):
			super(fncWrap,self).__init__(*args,**kws)
			self._str_funcName = 'ad_UV_grid_location_attr'
			#self._b_reportTimes = 1
			self._b_autoProgressBar = True
			self._l_ARGS_KWS_DEFAULTS = [{'kw':'Object','argType':'string or mObject',
			                              'help':'this is your poly object'}]
			self.__dataBind__(*args,**kws)
			self.l_funcSteps = [{'step':'Validating','call':self._validate_},
							    {'step':'Do IT','call':self.add_UV_grid_atter}]
		
		def _validate_(self):
			self.m_object = cgmMeta.validateObjArg(arg=self.d_kws['Object'], mayatype = 'mesh')
       	    
       	    ## check the object type
			mayaObjectType = self.m_object.getMayaType()
			
			#log.debug("this is my maya object Type ",m_object.mNode)
			if mayaObjectType != "mesh":
				log.error("{0} is not a mesh object Type".format(m_object.mNode))
				raise StandardError("This function only suports Polygon Meshs, {0} is not a Poly".format(self.d_kws['Object']))
        	
		
		def add_UV_grid_atter(self):
			## make m_object local
			m_object = self.m_object

			
			## get all UVs	
			UV_locations = mc.polyEditUV(m_object.mNode +".map[:]",
			 							  q=True,u=True,v=False)
		 
			## make a list for U and one for V
			U_gridSpaces = []
			V_gridSpaces = []
			for i in range(len(UV_locations)):
				if i%2 == 0:
					#Check U'''
					GridSpace = int(UV_locations[i])
					if GridSpace not in U_gridSpaces:
						U_gridSpaces.append(GridSpace)
				else:
					GridSpace = int(UV_locations[i])
					if GridSpace not in V_gridSpaces:
						V_gridSpaces.append(GridSpace)
				
			## add atter to metaObject
			m_object.addAttr("U_gridSpace",U_gridSpaces)
			m_object.addAttr("V_gridSpace",V_gridSpaces)
	
	return fncWrap(*args,**kws).go()  
     



  