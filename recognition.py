import config_control_design as stepCode
import collections
import cylinderRecognition
import faceRecognition

class recognition(object):

	
	def __init__(self, closed_s, stock):
		# Recognition process start
		self.closed_s = closed_s
		self.stock = stock
		#cylinderRecognition(closed_s, stock)
	def process(self, feature_name):
		results = {
		'cylinder' : cylinderRecognition.cylinderRecognition,
		'face' : faceRecognition.faceRecognition
		}
		return results[feature_name](self.closed_s, self.stock)

	# def reco_cylinder(self, closed_s, stock):
	# 	#print closed_s.stepLine
	# 	c_surfaces = closed_s.getSurfaceType(stepCode.cylindrical_surface)
	# 	c_surfaces_step = self.getStepFromObjects(c_surfaces)

	# 	# Find duplicate cylindrical surfaces
	# 	if len(c_surfaces_step) != len(set(c_surfaces_step)):
	# 		duplicated_step = [x for x, y in collections.Counter(c_surfaces_step).items() if y > 1]
	# 	duplicated_cs = []
	# 	for ds in duplicated_step:
	# 		for cs in c_surfaces:
	# 			if cs.stepLine == ds:
	# 				duplicated_cs.append(cs)
	# 				break
	# 	# 1th Rule :  Closed shell contains at least 2 advanced faces with the same cylindrical surface
	# 	if duplicated_cs:
	# 		# Find the cylindrical surface with the most diameter
	# 		max_diameter_cs = duplicated_cs[0]
	# 		for ds in duplicated_cs:
	# 			if(max_diameter_cs.radius<ds.radius):
	# 				max_diameter_cs=ds
	# 		#print max_diameter_cs.radius
	# 		if(stock.sd != (max_diameter_cs.radius*2)):
	# 			related_advanced_faces = closed_s.getAdvancedFacesFromSurfaceType(max_diameter_cs)
	# 			#print related_advanced_faces[0].getEdgeType(stepCode.line)[0].stepLine
	# 			af_lines = af_circles = []
	# 			for raf in related_advanced_faces:
	# 				raf_lines = raf.getEdgeType(stepCode.line)
	# 				raf_circles = raf.getEdgeType(stepCode.circle)
	# 				if len(raf_lines)==2 and len(raf_circles) == 2:
	# 					af_lines += raf_lines
	# 			if(len(af_lines)==4):
	# 				af_lines_step = self.getStepFromObjects(af_lines)
	# 				if(len(set(af_lines_step))==2):
	# 					print '---------- Cylinder feature found !'
	# 					self.max_diameter = max_diameter_cs.radius*2
	# 	else:
	# 		print "Nooo"


		


