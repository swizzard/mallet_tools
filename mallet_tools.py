import string
import re	
import nltk
class MalletTools:	
	def __init__(self,file_in=None,file_out=None,features=None):
		self.acceptable = re.compile(r'(\S*?\t)*(([A-Z])(-[A-Z]{3})?)')
		self.whitespace = re.compile(r'\s*?')
		self.NERtag = re.compile(r'(B|I|O)(-PER|-ORG|-GPE)?')
		self.IN = re.compile(r'IN')
		self.file_in = file_in
		if self.file_in:
			self.read_features(self.file_in)
		self.file_out = file_out
		self.features = features
	def add_list(self,list_name,l):
		setattr(self,list_name,l)	
	def read_features(self,file_in=None,dest="output_list",verbose=True):
		"""Read features from a properly-formatted text file and convert them to a list
		of format [[token1,[feature1,feature2,...,featureN]],[token2,[feature1,feature2,...,
		featureN]],...]
		:param file_in: name of the file to be read from
		:type file_in: str
		NOTE: passing read_features an open file will fail. Sorry.
		:param verbose: if True, print each read line
		:type verbose: bool (defaults to True)"""
		if self.file_in:
			file_in = self.file_in
		f_in = open(file_in,"r")
		feature_lines = f_in.readlines()
		f_in.close()
		output_list = []
		for i in xrange(len(feature_lines)):
			line = feature_lines[i]
			if re.match(self.acceptable,line):
				line_list =[]
				line_list.append(line.split()[0])
				line_list.append([line.split()[x] for x in xrange(1,len(line.split()))])
				if verbose:
					print "reading line %d of file %s as"%(i,file_in)
					print str(line_list)
				output_list.append(line_list)
			elif re.match(self.whitespace,line):
				pass
			else:
				raise MalletIOError(file_in,line,i)
		self.add_list(dest,output_list)
	def add_feature(self,feature_list=None,output_list=None,replace_NE_tags=False,position=0,verbose=False):
		"""Add features from a list of features to a list of [token,[features]]
		NOTE: if the lists are of different lengths, will raise an error.
		:param feature_list: the list of new features
		:type feature_list: list
		NOTE: one feature per item, please.
		:param output_list: the [token,[features]] list to be written to
		:type output_list: list
		:param replace_NE_tags: set to True to automatically replace NE tags to the end
		of each list of features in output_list
		:type replace_NE_tags: bool (defaults to False)
		NOTE: if set to False, user will be prompted each time a pre-existing NE tag is to be
		replaced.
		:param position: the position before which the new feature is to be added
		:type position: int (defaults to 0, e.g. new feature will be added at the beginning
		of the feature list)
		NOTE: if position is greater than the length of the feature list (i.e. if the user is
		trying to add a feature to the very end of the list), an error will be raised.
		(Mallet requires the NE tag to be the final feature on any line.)
		:param verbose: if True, prints the results, as well as the modified list
		:type verbose: bool (defaults to False)"""
		#assert not feature_list or not self.features,"Feature list already present!"
		#assert not output_list or not self.output_list
		if self.features:
			feature_list = self.features
		if self.output_list:
			output_list = self.output_list		
		#assert len(feature_list) == len(output_list),\
		 #"length of {list1} is {list1.len}, length of {list2} is {list2.len}".format(\
		#list1=feature_list,list2=output_list)
		for i in xrange(len(output_list)):
			feats = output_list[i][1]
			new_feature = str(feature_list[i])
			token = output_list[i][0]
			#assert position <= len(feats),\
			#"""Per Mallet specifications, the final tag in an entry should be that entry's
			#NE tag."""
			if re.match(self.NERtag,str(new_feature)) and not re.match(self.IN,str(new_feature)) and position > 0:
				print "It looks like you're trying add a NE tag!"
				NEtag = re.match(self.NERtag,feats[-1])
				if NEtag:
					if replace_NE_tags == True:
						resp = "y"
					else:
						resp = raw_input("Replace NE tag for token {}? (y/n)".format(token))
					if resp != "y":
						print "Ok. Keeping tag {} for token {}".format(NEtag.groups(),token)
					else:
						for tag in feats:
							re.sub(self.NERtag,new_feature,tag)
					if verbose:
						print "Replacing NE tag {} of token {} with {}".format(\
						NEtag.groups(),token,new_feature)
				else:
					print "Token {} appears to lack an NE tag".format(token)
					if replace_NE_tags:
						resp = "y"
					else:	
						resp = raw_input("Tag token {} with tag {}? (y/n)".format(token,new_feature))
					if resp != "y":
						print "All tokens should have NE tags. Aborting..."
						break
					else:
						feats.append(new_feature)
					if verbose:
						print "Tagging token {} with NE tag {}".format(token,new_feature)
			else:
				feats.insert(position,new_feature)
				if verbose:
					print "Adding feature {} to features of token {} in position {}".format(\
					new_feature,token,(position-1))
			self.output_list=output_list
			print "Done!"
			if verbose:
				print self.output_list
	def get_pos(self):
		if not self.words:
			self.get_words()
		punc = string.punctuation
		pos = nltk.tag.pos_tag(self.words)
		for x in xrange(len(pos)):
			if pos[x][0] == pos[x][1] and not pos[x][1].isalpha():
				punc+=pos[x][1]
		self.POS = []
		for x in xrange(len(pos)):
			if pos[x][1] in punc:
				self.POS.append("PUNC")
			else:
				self.POS.append(pos[x][1])
	def get_prevPOS(self):
		self.prevPOS=["FIRST"]
		for x in xrange(1,len(self.POS)):
			self.prevPOS.append(self.POS[x-1])
	def get_postPOS(self):
		self.postPOS=["LAST"]
		for x in xrange(len(self.POS)-1):
			self.postPOS.insert(-1,self.POS[x+1])
	def get_cap(self):
		if not self.words:
			self.get_words()
		self.cap = []
		for x in xrange(len(self.words)):
			if self.words[x].isupper():
				self.cap.append("allcaps")
			elif self.words[x].istitle():
				self.cap.append("titled")
			else:
				self.cap.append("noncapitalized")
	def get_prevCap(self):
		self.prevCap = ["FIRST"]
		for x in xrange(1,len(self.cap)):
			self.prevCap.append(self.cap[x-1])
	def get_postCap(self):
		self.postCap = ["LAST"]
		for x in xrange(len(self.cap)-1):
			self.postCap.insert(-1,self.cap[x+1])
	def get_words(self):
		self.words = [self.output_list[x][0] for x in xrange(len(self.output_list))]
	def write_out(self,file_out,test=False):
		with open(file_out,"w") as f:
			for x in xrange(len(self.output_list)):
				f.write(self.output_list[x][0]+" ")
				for i in xrange(len(self.output_list[x][1])-1):
					f.write(self.output_list[x][1][i] + " ")
				if test==False:
					f.write(self.output_list[x][1][-1]+"\n")
				else:
					f.write("\n")
def train_all():
	mt = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/train_nwire.txt")
	mt.get_words()
	mt.get_pos()
	mt.get_cap()
	mt.get_prevPOS()
	mt.get_postPOS()
	mt.get_prevCap()
	mt.get_postCap()
	mt.add_feature(mt.POS)
	mt.add_feature(mt.prevPOS)
	mt.add_feature(mt.postPOS)
	mt.add_feature(mt.cap)
	mt.add_feature(mt.prevCap)
	mt.add_feature(mt.postCap)
	mt.write_out(file_out="/Users/samuelraker/Desktop/name_data/train_all.txt")
	return mt
def test_all():
	mtest = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/test_nwire.txt")
	mtest.get_words()
	mtest.get_pos()
	mtest.get_cap()
	mtest.get_prevPOS()
	mtest.get_postPOS()
	mtest.get_prevCap()
	mtest.get_postCap()
	mtest.add_feature(mtest.POS)
	mtest.add_feature(mtest.prevPOS)
	mtest.add_feature(mtest.postPOS)
	mtest.add_feature(mtest.cap)
	mtest.add_feature(mtest.prevCap)
	mtest.add_feature(mtest.postCap)
	mtest.write_out(file_out="/Users/samuelraker/Desktop/name_data/test_all.txt",test=True)
def mscore_setup():
	mscore = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/test_nwire.txt")
	mscore.write_out(file_out="/Users/samuelraker/Desktop/name_data/score_nwire.txt")
def train_noPOS():
	train_noPOS = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/train_nwire.txt")
	train_noPOS.get_words()
	train_noPOS.get_cap()
	train_noPOS.get_prevCap()
	train_noPOS.get_postCap()
	train_noPOS.add_feature(train_noPOS.cap)
	train_noPOS.add_feature(train_noPOS.prevCap)
	train_noPOS.add_feature(train_noPOS.postCap)
	train_noPOS.write_out(file_out="/Users/samuelraker/Desktop/name_data/train_noPOS.txt")
def test_noPOS():
	test_noPOS = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/test_nwire.txt")
	test_noPOS.get_words()
	test_noPOS.get_cap()
	test_noPOS.get_prevCap()
	test_noPOS.get_postCap()
	test_noPOS.add_feature(test_noPOS.cap)
	test_noPOS.add_feature(test_noPOS.prevCap)
	test_noPOS.add_feature(test_noPOS.postCap)
	test_noPOS.write_out(file_out="/Users/samuelraker/Desktop/name_data/test_noPOS.txt",test=True)
def train_noContext():
	train_noContext = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/train_nwire.txt")
	train_noContext.get_words()
	train_noContext.get_cap()
	train_noContext.get_pos()
	train_noContext.add_feature(train_noContext.POS)
	train_noContext.add_feature(train_noContext.cap)
	train_noContext.write_out(file_out="/Users/samuelraker/Desktop/name_data/train_noContext.txt")
def test_noContext():
	test_noContext = MalletTools(file_in="/Users/samuelraker/Desktop/name_data/test_nwire.txt")
	test_noContext.get_words()
	test_noContext.get_cap()
	test_noContext.get_pos()
	test_noContext.add_feature(test_noContext.POS)
	test_noContext.add_feature(test_noContext.cap)
	test_noContext.write_out(file_out="/Users/samuelraker/Desktop/name_data/test_noContext.txt")
train_all()
test_all()
mscore_setup()
train_noPOS()
test_noPOS()
train_noContext()
test_noContext()