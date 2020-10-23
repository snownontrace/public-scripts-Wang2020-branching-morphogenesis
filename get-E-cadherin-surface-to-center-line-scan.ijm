inputFolder = getDirectory("Choose the folder containing images to process:");

// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-line-scan-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }
tifFolder = parentFolder + inputFolderPrefix + "-tif-output" + File.separator;
if ( !(File.exists(tifFolder)) ) { File.makeDirectory(tifFolder); }

line_width = 20; // in microns; the script will use image-embedded pixel size information to convert into pixels

run("Close All"); run("Collect Garbage"); // Release occupied memory
run("Clear Results");
setBatchMode(false); // always needs user input (draw line)

fileList = getFileList(inputFolder);
for (i=0; i<fileList.length; i++) {
//for (i=0; i<1; i++) {// uncomment to run only 1 image for testing
	// loop through the file list
	filename = inputFolder + fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	if ( endsWith(filename, ".nd2") || endsWith(filename, ".czi") || endsWith(filename, ".tif") ) {
		// only process image files that ends with nd2, czi or tif
		textRecord = outputFolder + outputPrefix + "-E-cadherin-line-scan.txt";
		tifFileRecord = tifFolder + outputPrefix + ".tif";
		if ( File.exists(textRecord) ) {
			continue;
		}
		if ( File.exists(tifFileRecord) ) {
			open(tifFileRecord);
		}
		else {
			open(filename);
		}
		id = getImageID();
		// get pixel size and convert desired micron-unit of line width to pixel size
		getPixelSize(unit, pixelWidth, pixelHeight);
		if (unit == "microns") {
			line_width_px = round(line_width / pixelWidth);
		}
		else {
			print("WARNING: pixel size is not in microns. Check image scaling.");
			line_width_px = 100; // assuming pixel size is ~0.2 micron, a close estimate for most high-resolution immunostaining images
		}

		// open a text file to store the line scan profile
		f = File.open(textRecord);
		print(f, "distance_to_surface_in_micron" + "," + "E-cad_intensity");
		
		// ask user to draw a box in the mesenchyme region to get a measure of background intensity
		setTool("rectangle");
		waitForUser("Go to the E-cad channel at the center slice,\ndraw a box in the mesenchyme to obtain background value");
		run("Measure");
		bg = getResult("Mean", 0);
		run("Clear Results");
		
		// ask user to draw a line to get the line scan profile
		setTool("line"); run("Line Width...", "line="+line_width_px); // line width can be adjusted to what you think is appropriate
		waitForUser("Draw a line >50 um from bud tip to center");
		profile = getProfile();
		for (j=0; j<profile.length; j++) {
			x = j * pixelWidth;
			y = profile[j] - bg;
			print(f, x + "," + y);
		} 
		File.close(f); // Close the file after saving all line scan values

		// Duplicate the single slice image and save for record (or re-run line scan on a smaller data set if necessary)
		selectImage(id); run("Select None");
		run("Duplicate...", " ");
		saveAs("Tiff", tifFileRecord);
		
		run("Close All"); run("Collect Garbage"); // Release occupied memory
	}
}

setTool("rectangle");
run("Close All");
run("Clear Results");


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

function deleteFolder(folder) {
	// Delete all the files inside the folder, then the folder itself
	list = getFileList(folder);
	// Delete the files and the folder
	for (i=0; i<list.length; i++){
		ok = File.delete(folder+list[i]);
	}
	ok = File.delete(folder);
	if (File.exists(folder))
		exit("Unable to delete the folder: " + folder);
	else
		print("Successfully deleted: " + folder);
}