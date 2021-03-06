import sys
import re
import os

def ParseDesignVariables_Plain (filename):
	
	try:
		fil = open(filename, 'r');
	except:
		sys.stderr.write("  ## ERROR : Could not open %s\n\n" % filename);
		sys.exit(0);
	
	fil = open(filename, 'r');
	
	DV_List        = [];	# List of design variables
	OutputCode     = [];  # List of request codes for the output functions
	Derivatives_DV = [];  # identify the subset of variables that are active for deriv. computation
	
	id_line = 0;
	
	for line in fil:
		
		id_line = id_line+1;
		hdl = line.split();
		
		if len(hdl) != 1 :
			sys.stderr.write("  ## ERROR : Unexpected input design variables format (line %d of %s).\n\n" % (id_line, filename));
			sys.exit(0);
			
		DV_List.append(float(hdl[0]));
		
	return DV_List, OutputCode, Derivatives_DV;
	
def ParseDesignVariables_Dakota (filename):
	
	try:
		fil = open(filename, 'r');
	except:
		sys.stderr.write("  ## ERROR : Could not open %s\n\n" % filename);
		sys.exit(0);
	
	fil = open(filename, 'r');
	
	# --- Outputs
	
	DV_List        = [];	# List of design variables
	OutputCode     = [];  # List of request codes for the output functions
	Derivatives_DV = [];  # identify the subset of variables that are active for deriv. computation
	
	# --- Regular expressions
	
	# setup regular expressions for parameter/label matching
	e = '-?(?:\\d+\\.?\\d*|\\.\\d+)[eEdD](?:\\+|-)?\\d+' # exponential notation
	f = '-?\\d+\\.\\d*|-?\\.\\d+'                        # floating point
	i = '-?\\d+'                                         # integer
	value = e+'|'+f+'|'+i                                # numeric field
	tag = '\\w+(?::\\w+)*'                               # text tag field
	
	# for aprepro parameters format
	aprepro_regex = re.compile('^\s*\{\s*(' + tag + ')\s*=\s*(' + value +')\s*\}$')
	# for standard parameters format
	standard_regex = re.compile('^\s*(' + value +')\s+(' + tag + ')$')
	
	#--- Extract data from file
	
	FilTab = [];
	
	cpt = 0;
	
	for line in fil:
 		m = aprepro_regex.match(line)
		
		if not m:
			m = standard_regex.match(line)
		
		if m :
			
			hdl = [];
			hdl.append(m.group(1));
			hdl.append(m.group(2));
			
			FilTab.append(hdl);
	
	NbrLin = len(FilTab);
	
	# --- Get design variables
	
	NbrVar = -1;
	
	for i in range(0,NbrLin):
		
		if (
		FilTab[i][1] == 'variables'
		or FilTab[i][1] == 'DAKOTA_VARS'
		):
			NbrVar = int(FilTab[i][0]);
			id = i;
			break;
	
	if NbrVar < 0 :
		sys.stderr.write("  ## ERROR : No variables given in %s\n\n" % filename);
		sys.exit(0);
	
	
	if NbrLin < id+NbrVar+1 :
		sys.stderr.write("  ## ERROR : Wrong variable definition in %s\n\n" % filename);
		sys.exit(0);
	
	for i in range(id+1,id+NbrVar+1):
		#print "%s %s" % (FilTab[i][0],FilTab[i][1]);
		DV_List.append(float(FilTab[i][0]));
	
	# --- Get number of output functions
	
	NbrOut = -1;
	
	for i in range(0,NbrLin):
		
		if (
		FilTab[i][1] == 'functions'
		):
			NbrOut = int(FilTab[i][0]);
			id = i;
			break;
	
	if NbrOut < 0 :
		sys.stderr.write("  ## ERROR : No output function given in %s\n\n" % filename);
		sys.exit(0);
	
	if NbrLin < id+NbrOut+1 :
		sys.stderr.write("  ## ERROR : Wrong output function  definition in %s\n\n" % filename);
		sys.exit(0);
	
	# --- Get request for each output function
  
	# 6 Get Hessian, gradient, and value Get Hessian and gradient
	# 5 Get Hessian and value
	# 4 Get Hessian
	# 3 Get gradient and value
	# 2 Get gradient
	# 1 Get value
	# 0 No data required, function is inactive
		
	for i in range(id,id+NbrOut+1):
		code = int(FilTab[i][0]);
		OutputCode.append(code);
		#print "%s %s" % (FilTab[i][0],FilTab[i][1]);
	
	# --- Get derivative variables
	
	NbrDer = -1;
	
	for i in range(0,NbrLin):
		
		if (
		FilTab[i][1] == 'derivative_variables'
		):
			NbrDer = int(FilTab[i][0]);
			id = i;
			break;
	
	if NbrDer > 0 :
		for i in range(id,id+NbrDer+1):
			Derivatives_DV.append(int(FilTab[i][0]));	
	
	return DV_List, OutputCode, Derivatives_DV;