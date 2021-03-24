//inputFolder = getDirectory("Choose the folder containing images to process:");
inputFolder = "/Volumes/ShaoheGtech2/2019-DLD-1-and-L-engineering-and-characterization/191220-IF-DLD-1-cells-E-cadherin-integrin/D193-D301-D304-b1integrin-Ecad-for-background-estimation/";
print(inputFolder);
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All");
run("Clear Results");
setBatchMode(false);

// Create a text file to store measurement results; use time stamp to keep different versions
timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
f = File.open(outputFolder + inputFolderPrefix + "-mean-intensity-" + timeStamp + ".txt");
print(f, "file_name" + "\t" + "mean_BG_intensity_NLS_mNG" + "\t" + "mean_BG_intensity_Ecad" + "\t" + "mean_BG_intensity_b1int");

flist = getFileList(inputFolder);
for (i=0; i<flist.length; i++) {
	if ( endsWith(flist[i], ".nd2") || endsWith(flist[i], ".czi") || endsWith(flist[i], ".tif") ) {
		outputPrefix = getFilenamePrefix(flist[i]);
		open(inputFolder + flist[i]); id0 = getImageID();
		
		adjustImageConstrast(id0);

		setTool("rectangle");
		waitForUser("Draw a box in the cell-free area");
		
		// Measure the intensities of the NLS-mNG or NLS-mSL signal, the E-cadherin and beta1-integrin background signal
		Stack.setChannel(1);
		run("Measure");
		Stack.setChannel(2);
		run("Measure");
		Stack.setChannel(3);
		run("Measure");
		
		// Obtain the vlaues from the Results table
		mean_BG_intensity_NLS_FP = getResult("Mean", 0);
		mean_BG_intensity_Ecad = getResult("Mean", 1);
		mean_BG_intensity_b1int = getResult("Mean", 2);
		
		print(f, outputPrefix + "\t" + mean_BG_intensity_NLS_FP + "\t" + mean_BG_intensity_Ecad + "\t" + mean_BG_intensity_b1int);
		
		// Clear the results table
		run("Clear Results");
		// Close images
		run("Close All");
	}
}
File.close(f);


function adjustImageConstrast(id) {
	selectImage(id);
	Stack.setChannel(1); run("Blue"); satu=2; run("Enhance Contrast", "saturated="+satu);
	Stack.setChannel(2); run("Red"); satu=2; run("Enhance Contrast", "saturated="+satu);
	Stack.setChannel(3); run("Green"); satu=2; run("Enhance Contrast", "saturated="+satu);
	run("Make Composite");
	return id;
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