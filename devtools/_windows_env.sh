
if [ "$OS" == "Windows_NT" ]; then
	if [ ! /c/Python34/python.exe ]; then
		echo "Error: C:\\Python34 was not found!"
		exit 1
	else
		alias python3="/c/Python34/python.exe"
		
		# this will probably break things, so only do it on Windows
		shopt -s expand_aliases
	fi
fi

