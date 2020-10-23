//inputFolder = getDirectory("Choose the folder containing images to process:");
//print(inputFolder);
inputFolder = '/Volumes/ShaoheGtech2/2019-DLD-1-and-L-engineering-and-characterization/191025-D193-D266-D267-Ecad-b1integrin/191025-D193-D267-D266-b1integrin-for-quantification/';
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All");
run("Clear Results");
setBatchMode(true);

// Create a text file to store measurement results; use time stamp to keep different versions
timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
f = File.open(outputFolder + inputFolderPrefix + "-mean-intensity-" + timeStamp + ".txt");
print(f, "file_name" + "\t" + "mean_intensity_b1int");

flist = getFileList(inputFolder);
for (i=0; i<flist.length; i++) {
	if ( endsWith(flist[i], ".nd2") || endsWith(flist[i], ".czi") || endsWith(flist[i], ".tif") ) {
		outputPrefix = getFilenamePrefix(flist[i]);
		open(inputFolder + flist[i]); id0 = getImageID();

		// Use the DAPI channel to segment a cell-positive area
		idROI = get_cell_positive_ROI(id0, 1);
		selectImage(idROI); run("Select None"); run("Create Selection");
		// Measure the intensities of the beta1-integrin signal
		selectImage(id0); run("Restore Selection");
		Stack.setChannel(4); run("Measure");
		
		// Obtain the vlaues from the Results table
		mean_intensity_b1int = getResult("Mean", 0);
		
		print(f, outputPrefix + "\t" + mean_intensity_b1int);
		
		// Clear the results table
		run("Clear Results");
		// Close images
		run("Close All");
	}
}
File.close(f);

function get_cell_positive_ROI(id, channel) {
	selectImage(id); run("Duplicate...", "duplicate channels="+channel); id1 = getImageID();
	selectImage(id1); run("Gaussian Blur...", "sigma=10");
	setAutoThreshold("Huang dark");
	setOption("BlackBackground", false);
	call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
	run("Convert to Mask");

	return id1;
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