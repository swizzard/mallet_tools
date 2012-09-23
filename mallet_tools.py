import string
import re	
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
	def Mallet_test_and_write(self,input=None,file_out=None,verbose=True):
		"""Tests whether input is Mallet-compliant and, if so, writes it to a file.
		:param input: the input to be tested and written
		:type input: EITHER a file name OR a list
		NOTE: if Mallet_test_and_write is passed a file object, it will fail. Sorry.
		:param file_out: the file to write to
		:type file_out: str (name of target file)
		:param verbose: if True, prints each line written to the screen before proceeding
		:type verbose: bool (defaults to True)"""
		if not input:
			assert self.file_in or self.features
			if self.file_in:
				input = self.file_in
			elif self.features_list:
				input = self.features
		if not file_out:
			file_out = self.file_out
		assert file_out == True
		if isinstance(input,str):
			source_name = "file " + str(input)
			infile = open(input)
			source = infile.readlines()
			infile.close()
		elif isinstance(input,list):
			source_name = "supplied input"
			source = input
		else:
			raise ValueError("input must be valid filename or list!")
		output = open(file_out,"w")
		for i in xrange(len(source)):
			line = source[i]
			if re.match(acceptable,line):
				output.write(line)
			#if not re.match(acceptable,line):
				#raise MalletIOError(source_name,line,source.index(line)+1)
			elif re.match(whitespace,line):
				pass
			else:
				raise MalletIOError(source_name,line,i)			
				#if input.index(line)+1 < len(input) and not re.match(r'\n$',line):
				#	output.write("\n")
		output.close()
		if verbose:	
			for line in source:
				print "Successfully wrote\n",line,"to",file_out
		print "Done."
	def write_features(self,file_in=None,file_out=None,features=None,verbose=True,test=False):
		"""Write a Mallet-compliant list of features
		:param file_in: an input file. 
		:param file_out: the name of the file to write to
		:param features: a list formatted in the following way:
			[[token1,[feature1,feature2...featureN,label]],[token2,[feature1,feature2...featureN,label]],...]
			NOTE: there should be the same number of features for each word.
			NOTE: set features to None if using file_in
		:param test: whether or not the data to be written is for testing purposes"""
		assert not (file_in and self.file_in),"Source file already present!"
		assert not (file_out and self.file_out),"Output file already present!"
		assert not (features and self.features),"List of features already present!"
		if self.file_in:
			file_in = self.file_in
		if file_in:	
			Mallet_test_and_write(file_in,file_out)
		if self.file_out:
			file_out = self.file_out
		if self.feature_list:
			features = self.features
		else:
			output_list = []
			for j in xrange(len(features)):
				output_string = ""
				i = 0
				output_string += features[j][0]+"\t"
				for k in xrange(len(features[j][1])):
					feature = features[j][1][k]
					output_string += feature
					i += 1
					if i < len(features[1]):
						output_string += "\t"
					elif test:
						pass	
				output_string += "\n"
				output_list.append(output_string)
			Mallet_test_and_write(output_list,file_out,verbose)
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
		assert not feature_list or not self.features,"Feature list already present!"
		assert not output_list or not self.output_list
		if self.features:
			feature_list = self.features
		if self.output_list:
			output_list = self.output_list		
		assert len(feature_list) == len(output_list),\
		 "length of {list1} is {list1.len}, length of {list2} is {list2.len}".format(\
		list1=feature_list,list2=output_list)
		for i in xrange(len(output_list)):
			feats = output_list[i][1]
			new_feature = str(feature_list[i])
			token = output_list[i][0]
			assert position <= len(feats),\
			"""Per Mallet specifications, the final tag in an entry should be that entry's
			NE tag."""
			if re.match(self.NERtag,new_feature) and not re.match(self.IN,new_feature) and position > 0:
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
	class MalletIOError(Exception):
		def __init__(self,source_name,line,line_no):
			"""A custom error class for Mallet-related tasks.
			:param source_name: the name of the source of the error.
			:type source_name: str
			NOTE: as implemented here (see below), source_name is going to be either the name of
			the file supplied (if Mallet_test_and_write is passed a file name), or "supplied input"
			(if it's passed a list)
			:param line: the offending line
			:type line: str
			:param line_no: the number of the offending line
			:type line_no: int
			NOTE: as implemented here (see below), line_no counts from 0, as this error is only
			raised AFTER read_lines is called"""
			self.source_name = source_name
			self.line = line
			self.line_no = line_no
			print "The line:\n",self.line,"\n","line number",self.line_no,"in",self.source_name,"\nis improperly formatted"