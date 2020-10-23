inputFolder = getDirectory("Choose the folder containing images to process:");

// get parent folder path and the input folder prefix
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
//outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
//if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

// make a text file handle to store cell counts of each image file
f = File.open(parentFolder + inputFolderPrefix + "-cell-counts.txt");
print(f, "file_name" + "\t" + "cell_number");

run("Close All");
run("Clear Results");
setBatchMode(true);

flist = getFileList(inputFolder);
//for (i=0; i<1; i++) {//for testing
for (i=0; i<flist.length; i++) {
	filename = inputFolder + flist[i];
	outputPrefix = getFilenamePrefix(flist[i]);
	
	if ( endsWith(filename, ".nd2") || endsWith(filename, ".czi") || endsWith(filename, ".tif") ) {
		open(filename); id = getImageID();
		//lowT = 150;// threshold value worked well for mNeonGreen set (D193, D301)
		lowT = 300;// threshold value worked well for D193 mNeonGreen set 1h or 2 h
		//lowT = 66;// threshold value worked well for overnight mNeonGreen set (D193, D301)
		//lowT = 1000;// threshold value worked well for mScarlet (D266, D267)
		cell_number = countCells(id, 2, lowT);
		print(f, outputPrefix + "\t" + cell_number);
		run("Close All");
		run("Clear Results");
	}
}
File.close(f);

function countCells(id, channel_N, lowT) {
	selectImage(id);
	Stack.setChannel(channel_N);
	run("Duplicate...", " ");
	run("Grays");
	run("Gaussian Blur...", "sigma=2");
	run("Morphological Filters", "operation=[White Top Hat] element=Disk radius=10");
	setThreshold(lowT, 65535);
	setOption("BlackBackground", false);
	run("Convert to Mask");
	run("Watershed");
	//run("Analyze Particles...", "display exclude clear");
	run("Analyze Particles...", "size=50-Infinity display exclude clear");
	N_cells = nResults;
	return N_cells;
}

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
