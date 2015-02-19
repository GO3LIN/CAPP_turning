import sys
import config_control_design as stepCode
from StringIO import StringIO

# stepFile = open(sys.argv[1], 'r').read()
# step_lines = stepFile.splitlines()

step_lines = ''

def printStep(cs):
	sys.stdout = stdout = StringIO()
	print cs.stepLine
	for af in cs.cfs_faces:
		print '  '+af.stepLine
		#print '  Face geometry : '+af.face_geometry.__class__.__name__
		af.face_geometry.printer()
		#print '  Face bounds :'
		for fb in af.bounds:
			print '    '+fb.stepLine
			print '      '+fb.bound.stepLine
			for oe in fb.bound.edge_list:
				print '        '+oe.stepLine
				print '          '+oe.edge_element.stepLine
				print '            '+oe.edge_element.edge_start.stepLine
				print '              '+oe.edge_element.edge_start.vertex_geometry.stepLine
				print '            '+oe.edge_element.edge_end.stepLine
				print '              '+oe.edge_element.edge_end.vertex_geometry.stepLine
				print '            '+oe.edge_element.edge_geometry.stepLine
				oe.edge_element.edge_geometry.printer()
	return stdout.getvalue()

def readStep(fileName):
	global step_lines
	stepFile = open(fileName, 'r').read()
	step_lines = stepFile.splitlines()
	# Find Closed Shell line & object params
	cs_line = None
	for step_line in step_lines:
		if("CLOSED_SHELL" in step_line):
			cs_line = step_line

	start = cs_line.find("('")+2
	end = cs_line.find("',")
	cs_name = cs_line[start:end]

	start = end+3
	end = cs_line.find('))')
	cfs_faces_ids = cs_line[start:end].split(',')
	cfs_faces = []

	for cfs_faces_id in cfs_faces_ids:
		cfs_faces.append(process_cfs_faces(searchLineStartsWith(cfs_faces_id)))


	cs = stepCode.closed_shell(cs_name, cfs_faces)	
	cs.stepLine = cs_line
	return cs







# Function that instantiates advanced_face objects from a list of pointers 
# and returns the set of objects
def process_cfs_faces(stepLine):
	start = stepLine.find("('")+2
	end = stepLine.find("',")
	cfs_name = stepLine[start:end] # inherited0__name
	start = stepLine.find(",(")+2
	end = stepLine.find("),")
	cfs_bounds_ids = stepLine[start:end].split(',')
	cfs_bounds = set() #inherited1__bounds
	for cfs_bounds_id in cfs_bounds_ids:
		cfs_bounds.add(process_cfs_bounds(searchLineStartsWith(cfs_bounds_id)))

	start = end+2
	end = stepLine.find(',.')
	cfs_fg_id = stepLine[start:end]
	cfs_fg = process_cfs_fg(searchLineStartsWith(cfs_fg_id))

	start = stepLine.find(',.')+2
	end = stepLine.find('.) ;')
	cfs_same_sense = stepLine[start:end]
	if(cfs_same_sense == 'T'):
		cfs_same_sense = True
	else:
		cfs_same_sense = False
	af = stepCode.advanced_face("", cfs_bounds, cfs_name, cfs_fg, cfs_same_sense)
	af.stepLine = stepLine
	return af

def process_cfs_bounds(stepLine):
	bound_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(',.')
	bound = process_bound(searchLineStartsWith(stepLine[start:end]))

	start = stepLine.find(',.')+2
	end = start+1
	bound_orientation = stepLine[start:end]
	if(bound_orientation=='T'):
		bound_orientation = True
	else:
		bound_orientation = False
	start = stepLine.find('=')+1
	end = stepLine.find("('")
	class_name = stepLine[start:end].lower()
	options = {"face_bound": stepCode.face_bound,
				"face_outer_bound": stepCode.face_outer_bound
				}
	ret_cfs_b = options[class_name](bound_name, bound, bound_orientation)
	ret_cfs_b.stepLine = stepLine
	return ret_cfs_b
	
def process_bound(stepLine):
	bound_name = getLabelFromStepLine(stepLine)
	start = stepLine.find(',(')+2
	end = stepLine.find('))')
	oriented_edge_ids = stepLine[start:end].split(',')
	bound_oe_list = []
	for oriented_edge_id in oriented_edge_ids:
		bound_oe_list.append(process_oriented_edge(searchLineStartsWith(oriented_edge_id)))
	el = stepCode.edge_loop("", bound_name, bound_oe_list)
	el.stepLine = stepLine
	return el

def process_oriented_edge(stepLine):
	oe_name = getLabelFromStepLine(stepLine)
	start = stepLine.find('*,*,')+4
	end = stepLine.find(',.')
	ec_id = stepLine[start:end]
	oe_edge_curve = process_edge_curve(searchLineStartsWith(ec_id))

	start = stepLine.find(',.')+2
	end = start+1
	oe_orientation = stepLine[start:end]
	if(oe_orientation=='T'):
		oe_orientation = True
	else:
		oe_orientation = False
	oe = stepCode.oriented_edge(oe_name, '*', '*', oe_edge_curve, oe_orientation)
	oe.stepLine = stepLine
	return oe

def process_edge_curve(stepLine):
	ec_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(',.')
	params = stepLine[start:end].split(',')

	ec_start = process_vertex_point(searchLineStartsWith(params[0]))
	ec_end = process_vertex_point(searchLineStartsWith(params[1]))

	ec_curve_line = searchLineStartsWith(params[2])
	options = {"line" : process_line,
			   "circle" : process_circle,
			   "b_spline_curve_with_knots" : process_bscwk,
			   "ellipse" : process_ellipse
			}
	start = ec_curve_line.find('=')+1
	end = ec_curve_line.find('(')
	class_name = ec_curve_line[start:end].lower()

	ec_edge_geometry = options[class_name](ec_curve_line)


	start = stepLine.find(',.')+2
	end = start+1
	ec_same_sense = stepLine[start:end]
	if(ec_same_sense=='T'):
		ec_same_sense = True
	else:
		ec_same_sense = False

	ec = stepCode.edge_curve('', ec_start, ec_end, ec_name, ec_edge_geometry , ec_same_sense)
	ec.stepLine = stepLine
	return ec

def process_line(stepLine):
	line_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	line_pnt = process_cartesian_point(searchLineStartsWith(params[0]))
	line_dir = process_vector(searchLineStartsWith(params[1]))
	li = stepCode.line(line_name, line_pnt, line_dir)
	li.stepLine = stepLine
	return li


def process_circle(stepLine):
	circle_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;');
	params = stepLine[start:end].split(',')
	circle_position = process_axis2p3d(searchLineStartsWith(params[0]))
	circle_radius = stepCode.positive_length_measure(params[1])
	ci = stepCode.circle(circle_name, circle_position, circle_radius)
	ci.stepLine = stepLine
	return ci

def process_ellipse(stepLine):
	ellipse_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end]
	ellipse_position = process_axis2p3d(searchLineStartsWith(params[0]))
	ellipse_semi_axis_1 = stepCode.positive_length_measure(params[1])
	ellipse_semi_axis_2 = stepCode.positive_length_measure(params[2])
	el = stepCode.ellipse(ellipse_name, ellipse_semi_axis_1, ellipse_semi_axis_2)
	el.stepLine = stepLine
	return el


def process_vector(stepLine):
	vector_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	vector_orientation = process_direction(searchLineStartsWith(params[0]))
	vector_magnitude = stepCode.length_measure(params[1])
	ve = stepCode.vector(vector_name, vector_orientation, vector_magnitude)
	ve.stepLine = stepLine
	return ve

def process_vertex_point(stepLine):
	vp_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(')')
	vp_cp = process_cartesian_point(searchLineStartsWith(stepLine[start:end]))
	vp = stepCode.vertex_point('', vp_name, vp_cp)
	vp.stepLine = stepLine
	return vp

def process_cfs_fg(stepLine):
	start = stepLine.find('=')+1
	end = stepLine.find('(')
	class_name = stepLine[start:end].lower()
	options = { "plane" : process_plane,
				"cylindrical_surface" : process_cylindrical_surface,
				"conical_surface" : process_conical_surface,
				"spherical_surface" : process_spherical_surface,
				"toroidal_surface" : process_toroidal_surface,
				"surface_of_revolution" : process_sor,
				"b_spline_surface_with_knots" : process_bsswk,
				"surface_of_linear_extrusion" : process_sole,
				}
	# Check if its a valid class
	if(class_name in dir(stepCode)):
		cf = options[class_name](stepLine)
		cf.stepLine = stepLine
		return cf

def process_plane(stepLine):
	plane_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	axis_line = searchLineStartsWith(stepLine[start:end])
	plane_axis = process_axis2p3d(axis_line)
	pl = stepCode.plane(plane_name, plane_axis)
	pl.stepLine = stepLine
	return pl


def process_cylindrical_surface(stepLine):
	cs_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	cs_location_line = searchLineStartsWith(params[0])
	cs_location = process_axis2p3d(cs_location_line)
	cs_radius = stepCode.positive_length_measure(params[1])
	cs = stepCode.cylindrical_surface(cs_name, cs_location, cs_radius)
	cs.stepLine = stepLine
	return cs

def process_conical_surface(stepLine):
	cs_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	cs_position_line = searchLineStartsWith(params[0])
	cs_position = process_axis2p3d(cs_position_line)
	cs_radius = stepCode.length_measure(params[1])
	cs_semi_angle = stepCode.plane_angle_measure(params[2])
	cs = stepCode.conical_surface(cs_name, cs_position, cs_radius, cs_semi_angle)
	cs.stepLine = stepLine
	return cs

def process_spherical_surface(stepLine):
	ss_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	ss_position = process_axis2p3d(searchLineStartsWith(params[0]))
	ss_radius = stepCode.positive_length_measure(params[1])
	ss = stepCode.spherical_surface(ss_name, ss_position, ss_radius)
	ss.stepLine = stepLine
	return ss


def process_toroidal_surface(stepLine):
	ts_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	ts_location = process_axis2p3d(searchLineStartsWith(params[0]))
	ts_maj_radius = stepCode.positive_length_measure(params[1])
	ts_min_radius = stepCode.positive_length_measure(params[2])
	ts = stepCode.toroidal_surface(ts_name, ts_location, ts_maj_radius, ts_min_radius)
	ts.stepLine = stepLine
	return ts
	

def process_sor(stepLine):
	sor_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	sor_swept_curve = process_bscwk(searchLineStartsWith(params[0]))
	sor_axis_position = process_axis1p(searchLineStartsWith(params[1]))
	sor = stepCode.surface_of_revolution(sor_name, sor_swept_curve, sor_axis_position)
	sor.stepLine = stepLine
	return sor

def process_bsswk(stepLine):
	print stepLine

def process_sole(stepLine):
	print stepLine

def process_bscwk(stepLine):
	bscwk_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(",(")
	bscwk_degree = int(stepLine[start:end])
	start = end+2
	end = stepLine.find('),')
	control_point_ids = stepLine[start:end].split(',')
	bscwk_cp = []
	for cp_id in control_point_ids:
		bscwk_cp.append(process_cartesian_point(searchLineStartsWith(cp_id)))
	start = end+3
	end = stepLine.find('.,')
	bscwk_curve_form = stepCode.b_spline_curve_form(stepLine[start:end])
	start = end+3
	end = start+1
	if(stepLine[start:end]=="T"):
		bscwk_closed_curve = True
	else:
		bscwk_closed_curve = False

	start = end+3
	end = stepLine[start:].find('.,')+start
	bscwk_self_intersect = stepLine[start:end]

	start = end+3
	end = stepLine[start:].find('),')+start
	knot_multiplicities_list = stepLine[start:end].split(',')
	bscwk_knot_multiplicities = []
	for km in knot_multiplicities_list:
		bscwk_knot_multiplicities.append(int(km))

	start = end+3
	end = stepLine[start:].find('),')+start
	knots_list = stepLine[start:end].split(',')
	bscwk_knots = []
	for kn in knots_list:
		bscwk_knots.append(stepCode.REAL(kn))

	start = end+3
	end = stepLine.find('.) ;')
	bscwk_knot_spec = stepCode.knot_type(stepLine[start:end])

	bs = stepCode.b_spline_curve_with_knots(bscwk_name, bscwk_degree, bscwk_cp, bscwk_curve_form, bscwk_closed_curve, bscwk_self_intersect, bscwk_knot_multiplicities, bscwk_knots, bscwk_knot_spec)
	bs.stepLine = stepLine
	return bs



	#print stepCode.LOGICAL(stepLine[start:end])

	#print bscwk_curve_form



def process_axis1p(stepLine):
	ax_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	ax_location = process_cartesian_point(searchLineStartsWith(params[0]))
	ax_axis = process_direction(searchLineStartsWith(params[1]))
	ax = stepCode.axis1_placement(ax_name, ax_location, ax_axis)
	ax.stepLine = stepLine
	return ax

def process_axis2p3d(stepLine):
	axis2p3d_name = getLabelFromStepLine(stepLine)
	start = stepLine.find("',")+2
	end = stepLine.find(') ;')
	params = stepLine[start:end].split(',')
	location_line = searchLineStartsWith(params[0])
	axis_line = searchLineStartsWith(params[1])
	if(params[2] != '$'):
		ref_direction_line = searchLineStartsWith(params[2])
		refd_axis = process_direction(ref_direction_line)
	else:
		refd_axis = None
	ax_location = process_cartesian_point(location_line)
	ax_axis = process_direction(axis_line)
	ax = stepCode.axis2_placement_3d(axis2p3d_name, ax_location, ax_axis, refd_axis)
	ax.stepLine = stepLine
	return ax

def process_cartesian_point(stepLine):
	cp_name = getLabelFromStepLine(stepLine)
	start = stepLine.find(',(')+2
	end = stepLine.find('))')
	params = stepLine[start:end].split(',')
	x = stepCode.REAL(params[0])
	y = stepCode.REAL(params[1])
	z = stepCode.REAL(params[2])
	cp = stepCode.cartesian_point(cp_name, [x,y,z])
	cp.stepLine = stepLine
	return cp

def process_direction(stepLine):
	direction_name = getLabelFromStepLine(stepLine)
	start = stepLine.find(',(')+2
	end = stepLine.find('))')
	params = stepLine[start:end].split(',')
	x = stepCode.REAL(params[0])
	y = stepCode.REAL(params[1])
	z = stepCode.REAL(params[2])
	di = stepCode.direction(direction_name, [x,y,z])
	di.stepLine = stepLine
	return di

def searchLineStartsWith(string):
	global step_lines
	string += '='
	for step_line in step_lines:
		if(step_line.startswith(string)):
			return step_line			

def getLabelFromStepLine(stepLine):
	start = stepLine.find("('")+2
	end = stepLine.find("',")
	return stepLine[start:end]


