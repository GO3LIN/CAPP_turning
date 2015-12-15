import config_control_design as stepCode
import recognitionTools as r_tools
import collections

class faceRecognition:

	def __init__(self, closed_s, stock):
		#reco.__init__(self, closed_s, stock)
		self.closed_s    = closed_s
		self.stock       = stock
		self.vp_min_z    = None
		self.vp_max_z    = None
		self.leftFound   = None
		self.rightFound  = None
		self.min_af_list = []
		self.max_af_list = []
		self.rule1()

	# Check if extremum surfaces type is a plane.
	def rule1(self):
		#print closed_s.stepLine
		processRule2 = False
		vertex_pts = self.closed_s.getVertexPoints()
		# Get the min z coordinate of the part vertex points
		vertex_pts_z = []
		for vp in vertex_pts:
			vertex_pts_z.append(vp.vertex_geometry.coordinates[2])
		self.vp_min_z = min(vertex_pts_z)
		# Get the list of vertex points that share minimum coordinate on z
		vp_min_list = []
		for vp in vertex_pts:
			if(vp.vertex_geometry.coordinates[2]==self.vp_min_z):
				vp_min_list.append(vp)
		# Get advanced faces that has plane as surface type from the min vertex points list 
		min_af_list_with_duplication =[]
		for vp in vp_min_list:
			# print vp.stepLine
			af = self.closed_s.getAdvancedFaceFromVertexPoint(vp)
			surfaceType = af.face_geometry
			if(isinstance(surfaceType, stepCode.plane)):
				min_af_list_with_duplication.append(af)
		# Remove duplicated advances faces
		if(min_af_list_with_duplication):
			self.min_af_list = r_tools.removeDuplication(min_af_list_with_duplication)
			processRule2 = True

		# Same logic for max z
		self.vp_max_z = max(vertex_pts_z)
		vp_max_list = []
		for vp in vertex_pts:
			if(vp.vertex_geometry.coordinates[2]==self.vp_max_z):
				vp_max_list.append(vp)
		max_af_list_with_duplication =[]
		for vp in vp_max_list:
			# print vp.stepLine
			af = self.closed_s.getAdvancedFaceFromVertexPoint(vp)
			surfaceType = af.face_geometry
			if(isinstance(surfaceType, stepCode.plane)):
				max_af_list_with_duplication.append(af)
		if(max_af_list_with_duplication):
			self.max_af_list = r_tools.removeDuplication(max_af_list_with_duplication)
			processRule2 = True
		# Go to rule2 if rule1
		if(processRule2):
			self.rule2()
	def rule2(self):
		stock_z = [self.stock.points[0][2], self.stock.points[1][2]]
		if(min(stock_z)<self.vp_min_z):
			print 'Left Face Feature'
			self.leftFound = True
		if(max(stock_z)>self.vp_max_z):
			print 'Right Face Feature'
			self.rightFound = True

		# for af in self.min_af_list:
		# 	print af.stepLine
		# for af in self.max_af_list:
		# 	print af.stepLine
