def create_testable(ref,system,f_out):
	"""Creates a text file suitable for testing by appending the results of a classifier to a list of
	gold-standard annotated tokens line-by-line.
	The file created by this method will be formatted as follows:
	TOKENi GOLDi SYSTEMi
	TOKENj GOLDj SYSTEMj
	...
	TOKENn GOLDn SYSTEMn
	where GOLDi is the gold-standard annotation and SYSTEMi the result of the classifier for the ith token.
	:param ref: the location of the reference (gold-standard) file
	:type ref: str
	:param system: the location of the results of the classifier
	:type system: str
	:param f_out: the location of the file to write the results to
	:type f_out: str"""
	r_file = open(ref)
	r_lines = r_file.readlines()
	r_file.close()
	system_file = open(system)
	system_lines = system_file.readlines()
	system_file.close()
	assert len(r_lines) == len(system_lines)
	output = [r_lines[x][:-1]+" "+system_lines[x][:-1]+"\n" for x in xrange(len(r_lines))]
	output_file = open(f_out,"w")
	for x in xrange(len(output)):
		output_file.write(output[x])
	output_file.close()

def get_confusion(f):
	"""Takes a text file formatted in the manner produced by create_testable, above, and
	generates a confusion matrix from it. NOTE: currently only works for BIO/GPE-PER-ORG-O taggers.
	:param f: the location of the file to use in constructing the matrix
	:type f: str"""
	B_GPE = [0,0,0,0,0,0,0,0]
	I_GPE = [0,0,0,0,0,0,0,0]
	B_PER = [0,0,0,0,0,0,0,0]
	I_PER = [0,0,0,0,0,0,0,0]
	B_ORG = [0,0,0,0,0,0,0,0]
	I_ORG = [0,0,0,0,0,0,0,0]
	O = [0,0,0,0,0,0,0,0]
	f_file = open(f)
	fl = f_file.readlines()
	f_file.close()
	for x in xrange(len(fl)):
		gold = fl[x].split()[1]
		system = fl[x].split()[2]
		if gold == "B-GPE":
			B_GPE[7] +=1
			if system == "B-GPE":
				B_GPE[0]+=1
			elif system == "I-GPE":
				B_GPE[1]+=1
			elif system == "B-PER":
				B_GPE[2]+=1
			elif system == "I-PER":
				B_GPE[3] += 1
			elif system == "B-ORG":
				B_GPE[4] += 1
			elif system == "I-ORG":
				B_GPE[5] += 1
			elif system == "O":
				B_GPE[6] += 1
		elif gold == "I-GPE":
			I_GPE[7] += 1
			if system == "B-GPE":
				I_GPE[0]+=1
			elif system == "I-GPE":
				I_GPE[1]+=1
			elif system == "B-PER":
				I_GPE[2]+=1
			elif system == "I-PER":
				I_GPE[3] += 1
			elif system == "B-ORG":
				I_GPE[4] += 1
			elif system == "I-ORG":
				I_GPE[5] += 1
			elif system == "O":
				I_GPE[6] += 1
		elif gold == "B-PER":
			B_PER[7] += 1
			if system == "B-GPE":
				B_PER[0]+=1
			elif system == "I-GPE":
				B_PER[1]+=1
			elif system == "B-PER":
				B_PER[2]+=1
			elif system == "I-PER":
				B_PER[3] += 1
			elif system == "B-ORG":
				B_PER[4] += 1
			elif system == "I-ORG":
				B_PER[5] += 1
			elif system == "O":
				B_PER[6] += 1
		elif gold == "I-PER":
			I_PER[7] +=1
			if system == "B-GPE":
				I_PER[0]+=1
			elif system == "I-GPE":
				I_PER[1]+=1
			elif system == "B-PER":
				I_PER[2]+=1
			elif system == "I-PER":
				I_PER[3] += 1
			elif system == "B-ORG":
				I_PER[4] += 1
			elif system == "I-ORG":
				I_PER[5] += 1
			elif system == "O":
				I_PER[6] += 1
		elif gold == "B-ORG":
			B_ORG[7] += 1
			if system == "B-GPE":
				B_ORG[0]+=1
			elif system == "I-GPE":
				B_ORG[1]+=1
			elif system == "B-PER":
				B_ORG[2]+=1
			elif system == "I-PER":
				B_ORG[3] += 1
			elif system == "B-ORG":
				B_ORG[4] += 1
			elif system == "I-ORG":
				B_ORG[5] += 1
			elif system == "O":
				B_ORG[6] += 1
		elif gold == "I-ORG":
			I_ORG[7] += 1
			if system == "B-GPE":
				I_ORG[0]+=1
			elif system == "I-GPE":
				I_ORG[1]+=1
			elif system == "B-PER":
				I_ORG[2]+=1
			elif system == "I-PER":
				I_ORG[3] += 1
			elif system == "B-ORG":
				I_ORG[4] += 1
			elif system == "I-ORG":
				I_ORG[5] += 1
			elif system == "O":
				I_ORG[6] += 1	
		elif gold == "O":
			O[7] += 1
			if system == "B-GPE":
				O[0]+=1
			elif system == "I-GPE":
				O[1]+=1
			elif system == "B-PER":
				O[2]+=1
			elif system == "I-PER":
				O[3] += 1
			elif system == "B-ORG":
				O[4] += 1
			elif system == "I-ORG":
				O[5] += 1
			elif system == "O":
				O[6] += 1
	cm = [B_GPE,I_GPE,B_PER,I_PER,B_ORG,I_ORG,O]
	return cm

def print_CM(f):
	"""Calls get_confusion, above, and pretty-prints the result.
	:param f: the location of the file to use in the construction of the matrix
	:type f: str"""
	cm = get_confusion(f)
	print "{0:15}{1:*^56}".format("","Confusion Matrix")
	print "{0:15}{1:^56}".format("",f)
	print "{0:15}{1:^52}".format("","Reported")
	keys = ["B-GPE","I-GPE","B-PER","I-PER","B-ORG","I-ORG","O","TOTAL"]
	print "{0:15}{1[0]:^7}{1[1]:^7}{1[2]:^7}{1[3]:^7}{1[4]:^7}{1[5]:^7}{1[6]:^7}{1[7]:^7}".format("",keys)
	for x in xrange(len(cm)):
		if x == 3:
			print "{0:8}{1:^7}{2[0]:^7}{2[1]:^7}{2[2]:^7}{2[3]:^7}{2[4]:^7}{2[5]:^7}{2[6]:^7}{2[7]:^7}".format("Actual",keys[x],cm[x])
		else:
			print "{0:8}{1:^7}{2[0]:^7}{2[1]:^7}{2[2]:^7}{2[3]:^7}{2[4]:^7}{2[5]:^7}{2[6]:^7}{2[7]:^7}".format("",keys[x],cm[x])