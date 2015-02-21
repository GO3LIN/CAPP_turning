def getStepFromObjects(objects):
	ret = []
	for cs in objects:
		ret.append(cs.stepLine)
	return ret
def removeDuplication(objectsList):
	ret = []
	objects_step = getStepFromObjects(objectsList)
	for o in list(set(objects_step)):
		for oo in objectsList:
			if(o == oo.stepLine):
				ret.append(oo)
				break
	return ret
