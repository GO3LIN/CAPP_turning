import recognitionTools as r_tools
import config_control_design as stepCode
import ap238_arm_schema as ap238
import collections

class cylinderRecognition:

	def __init__(self, closed_s, stock):
		#reco.__init__(self, closed_s, stock)
		self.closed_s = closed_s
		self.stock = stock
		self.max_diameter = 0.0
		self.process(closed_s, stock)

	def process(self, closed_s, stock):
		#print closed_s.stepLine
		c_surfaces = closed_s.getSurfaceType(stepCode.cylindrical_surface)
		c_surfaces_step = r_tools.getStepFromObjects(c_surfaces)

		# Find duplicate cylindrical surfaces
		if len(c_surfaces_step) != len(set(c_surfaces_step)):
			duplicated_step = [x for x, y in collections.Counter(c_surfaces_step).items() if y > 1]
		duplicated_cs = []
		for ds in duplicated_step:
			for cs in c_surfaces:
				if cs.stepLine == ds:
					duplicated_cs.append(cs)
					break
		# 1th Rule :  Closed shell contains at least 2 advanced faces with the same cylindrical surface
		if duplicated_cs:
			# Find the cylindrical surface with the most diameter
			max_diameter_cs = duplicated_cs[0]
			for ds in duplicated_cs:
				if(max_diameter_cs.radius<ds.radius):
					max_diameter_cs=ds
			#print max_diameter_cs.radius
			# 2nd Rule
			if(stock.sd > (max_diameter_cs.radius*2)):
				related_advanced_faces = closed_s.getAdvancedFacesFromSurfaceType(max_diameter_cs)
				#print related_advanced_faces[0].getEdgeType(stepCode.line)[0].stepLine
				af_lines = af_circles = []
				for raf in related_advanced_faces:
					raf_lines = raf.getEdgeType(stepCode.line)
					raf_circles = raf.getEdgeType(stepCode.circle)
					if len(raf_lines)==2 and len(raf_circles) == 2:
						af_lines += raf_lines
				# 3rd Rule
				if(len(af_lines)%4==0):
					af_lines_step = r_tools.getStepFromObjects(af_lines)
					# 4th Rule
					if(len(set(af_lines_step))==(len(af_lines)/2)):
						circles = closed_s.getEdgeType(stepCode.circle)
						circles_max_radius = circles[0].radius
						for circle in circles:
							if(circles_max_radius<circle.radius):
								circles_max_radius = circle.radius
						# 5th Rule 
						if(circles_max_radius<=max_diameter_cs.radius):
							print '---------- Cylinder feature found !'
							wp = ap238.workpiece.__new__(ap238.workpiece)
							operations = ap238.machining_operation.__new__(ap238.machining_operation)

							ap238.outer_diameter('OD1', wp, set())
							self.max_diameter = max_diameter_cs.radius*2
							self.advanced_faces = related_advanced_faces
						else:
							print 'circles_max_radius>max_radius'
					else:
						print 'Doesnt contain 2 duplicated lines'
				else:
					print 'Advances faces doesnt contain 4 lines'
			else:
				print 'sd>max_diameter'
		else:
			print "Nooo"