import config_control_design as stepCode
import recognitionTools as r_tools
import collections

class faceRecognition:

	def __init__(self, closed_s, stock):
		#reco.__init__(self, closed_s, stock)
		self.closed_s    = closed_s
		self.stock       = stock
		self.vp_min_y    = None
		self.vp_max_y    = None
		self.leftFound   = None
		self.rightFound  = None
		self.min_af_list = []
		self.max_af_list = []
		self.rule1()

	def rule1(self):
		#print closed_s.stepLine
		processRule2 = False
		vertex_pts = self.closed_s.getVertexPoints()
		vertex_pts_y = []
		for vp in vertex_pts:
			vertex_pts_y.append(vp.vertex_geometry.coordinates[1])
		self.vp_min_y = min(vertex_pts_y)
		vp_min_list = []
		for vp in vertex_pts:
			if(vp.vertex_geometry.coordinates[1]==self.vp_min_y):
				vp_min_list.append(vp)
		min_af_list_with_duplication =[]
		for vp in vp_min_list:
			# print vp.stepLine
			af = self.closed_s.getAdvancedFaceFromVertexPoint(vp)
			surfaceType = af.face_geometry
			if(isinstance(surfaceType, stepCode.plane)):
				min_af_list_with_duplication.append(af)
		if(min_af_list_with_duplication):
			self.min_af_list = r_tools.removeDuplication(min_af_list_with_duplication)
			processRule2 = True

		self.vp_max_y = max(vertex_pts_y)
		vp_max_list = []
		for vp in vertex_pts:
			if(vp.vertex_geometry.coordinates[1]==self.vp_max_y):
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
		if(processRule2):
			self.rule2()
	def rule2(self):
		stock_y = [self.stock.points[0][1], self.stock.points[1][1]]
		if(min(stock_y)<self.vp_min_y):
			print 'Left Face Feature'
			self.leftFound = True
		if(max(stock_y)>self.vp_max_y):
			print 'Right Face Feature'
			self.rightFound = True

		# for af in self.min_af_list:
		# 	print af.stepLine
		# for af in self.max_af_list:
		# 	print af.stepLine
