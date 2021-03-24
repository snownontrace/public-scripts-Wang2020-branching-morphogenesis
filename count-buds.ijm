inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

flist = getFileList(inputFolder);

timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
f = File.open(parentFolder + inputFolderPrefix + "-" + timeStamp + "-budCount.txt");
print(f, "file_name" + "\t" + "bud_number");

run("Clear Results");

for (i=0; i<flist.length; i++) {
	showProgress(i+1, flist.length);
	filename = inputFolder+flist[i];
	if ( endsWith(filename, ".tif") || endsWith(filename, ".nd2") ) {
		setBatchMode(true);
		open(filename); id0 = getImageID();
		run("Duplicate...", "duplicate channels=1"); idPh = getImageID();
		selectImage(id0); close();
		
		setBatchMode(false);
		selectImage(idPh);
		//run("Enhance Contrast", "saturated=0.01"); getMinAndMax(min1, max1);
		satu=1.0; run("Enhance Contrast", "saturated="+satu); getMinAndMax(min2, max2);
		//setMinAndMax(min1-2000, max2);
		setMinAndMax(0, max2);
		//run("Enhance Contrast", "saturated=0.0");
		
		setTool("multipoint");
		run("Point Tool...", "type=Hybrid color=Green size=Large label counter=0");
		waitForUser("Mark all  buds that you think are buds:");
		run("Measure");
		print(f, flist[i] + "\t" + nResults);
		selectImage(idPh); save(outputFolder + getPathFilenamePrefix(flist[i]) + "-record.tif");
		
		run("Clear Results"); run("Close All");
	}
}
File.close(f);

// reset default tools
setTool("rectangle");

function getPath(pathFileOrFolder) {
	// this one takes full path of the file (input can also be a folder) and returns the parent folder path
	temp = split(pathFileOrFolder, File.separator);
	if ( File.separator == "/" ) {
	// Mac and unix system
		pathTemp = File.separator;
		for (i=0; i<temp.length-1; i++) {pathTemp = pathTemp + temp[i] + File.separator;}
	}
	if ( File.separator == "\\" ) {
	// Windows system
		pathTemp = temp[0] + File.separator;
		for (i=1; i<temp.length-1; i++) {pathTemp = pathTemp + temp[i] + File.separator;}
	}
	return pathTemp;
}

function getPathFilenamePrefix(pathFileOrFolder) {
	// this one takes full path of the file
	temp = split(pathFileOrFolder, File.separator);
	temp = temp[temp.length-1];
	temp = split(temp, ".");
	return temp[0];
}

function getFilenamePrefix(filename) {
	// this one takes just the file name without folder path
	temp = split(filename, ".");
	return temp[0];
}