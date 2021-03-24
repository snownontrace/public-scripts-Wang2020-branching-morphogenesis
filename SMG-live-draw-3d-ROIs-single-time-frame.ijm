// This macro opens the image sequence, make it into a hyperstack as color composite,
// set red/green colors for the channels, auto-contrast to be easily visible,
// then it advances every tStep in time frames and every zStep in the z-direction,
// wait for the user to draw a segmented line along the bud surface,
// and saves the x-y coordinates in a txt file in a folder named after the image name.
// The file name of each txt file contains the t and z information.

nChannel = 1;
nSlice = 372;
zStart = 30; // inspect the file first to determine
zStop = 330; // inspect the file first to determine
zStep = 10; // in slice number

t_specified = 192; // specify the frame number of the current stack
//z_interval = 2; // for regular stacks, z interval is usually 2 um
z_interval = 0.62; // for resliced image stacks, z interval is usually 0.62 um

// Clean up workspace
run("Close All"); run("Collect Garbage"); // Release occupied memory
if ( isOpen("Synchronize Windows") ) { selectWindow("Synchronize Windows"); run("Close"); }
if ( isOpen("Log") ) { selectWindow("Log"); run("Close"); }
if ( isOpen("Debug") ) { selectWindow("Debug"); run("Close"); }
if ( isOpen("Results") ) { selectWindow("Results"); run("Close"); }
if ( isOpen("ROI Manager") ) { selectWindow("ROI Manager"); run("Close"); }

imgPath = File.openDialog("Choose a File");
outputPrefix = getPathFilenamePrefix(imgPath);
parentFolder = File.getParent(imgPath) +  File.separator;// Returns the folder name without the trailing file separator

outputFolder = parentFolder + outputPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }
timeStamp = getTime()%4;
ROIfolder = outputFolder + "ROIs-" + zeroPadding4(timeStamp) + File.separator;
if ( !(File.exists(ROIfolder)) ) { File.makeDirectory(ROIfolder); }

processImageStack(imgPath, ROIfolder, z_interval, t_specified);

function processImageStack(inputFile, outputFolder, z_interval, t) {
	setBatchMode(false);
	open(inputFile);
	outputPrefix = getPathFilenamePrefix(inputFile);
	// pre-processing of the image for easy display and visualization
	if (Stack.isHyperstack) {
		Stack.getDimensions(width, height, nChannel, nSlice, nFrame);
	}
	else nFrame = nSlices/nChannel/nSlice;
	run("Properties...", "channels="+nChannel+" slices="+nSlice+" frames="+
		nFrame+" unit=micron pixel_width=0.62 pixel_height=0.62 voxel_depth="+z_interval+" frame=[300 sec]");
	Stack.getDimensions(width, height, nChannel, nSlice, nFrame);
	print("Image width is: " + width + " pixels.");
	print("Image height is: " + height + " pixels.");
	run("In [+]");
	run("In [+]");
	// clear roi manager
	roiManager("reset");
	// first, loop from middle z upwards
	zMid = floor(nSlice/2) + 1;
	//print(zMid);
	for (z=zMid; z<zStop+1; z+=zStep){
		Stack.setSlice(z);
		setTool("polyline");
		waitForUser("Draw along the epithelial bud surface");
		roiManager("Add");
		roiName = "mesh-t-" + zeroPadding3(t) + "-z-" + zeroPadding2(z) + ".txt";
		roiN = roiManager("count");
		roiManager("select", roiN-1);
		roiManager("Rename", roiName);
		//run("Select None");
	}
	// second, loop from middle z - zStep downwards
	for (z=zMid-zStep; z>zStart-1; z-=zStep){
		Stack.setSlice(z);
		setTool("polyline");
		waitForUser("Draw along the epithelial bud surface");
		roiManager("Add");
		roiName = "mesh-t-" + zeroPadding3(t) + "-z-" + zeroPadding3(z) + ".txt";
		roiN = roiManager("count");
		roiManager("select", roiN-1);
		roiManager("Rename", roiName);
		//run("Select None");
	}
	roiManager("Sort");
	// save ROIs before adjusting them
	roiFilename = outputFolder + outputPrefix + "-meshROIs-beforeAdjusting.zip";
	roiManager("Deselect");// this ensures the whole collection of ROIs to be saved
	roiManager("Save", roiFilename);
	// save ROIs after adjusting them
	waitForUser("Modify the ROIs if necessary. Confirm when you are happy!");
	roiFilename = outputFolder + outputPrefix + "-meshROIs.zip";
	roiManager("Deselect");// this ensures the whole collection of ROIs to be saved
	roiManager("Save", roiFilename);
	run("Close All");
	// Use a separate macro for the saving process
	saveRoiAsCoordinates(roiFilename, outputFolder, z_interval);
}

function saveRoiAsCoordinates(roiFilename, outputFolder, z_interval) {
	setBatchMode(true);
	
	// clears roi manager and loads the roi set
	roiManager("reset"); roiManager("Open",roiFilename);
	// get some basic numbers for parsing
	roiN = roiManager("count");
	// create an empty image as a holder
	newImage("temp.tif", "8-bit black", 1500, 1500, 1);
	run("Properties...", "channels=1 slices=1 frames=1 unit=micron"+
		"pixel_width=0.62 pixel_height=0.62 voxel_depth="+z_interval+" frame=[300 sec]");
	
	for (i=0; i<roiN; i+=1){
		roiManager("select", i);
		roiName = call("ij.plugin.frame.RoiManager.getName", i);
		outFilename = outputFolder + roiName;
		saveAs("XY Coordinates", outFilename);
	}
}

function getFilenamePrefix(filename) {
	// this one takes just the file name without folder path
	temp = split(filename, ".");
	return temp[0];
}

function getPathFilenamePrefix(pathFileOrFolder) {
	// this one takes full path of the file of folder
	temp = split(pathFileOrFolder, File.separator);
	temp = temp[temp.length-1];
	temp = split(temp, ".");
	return temp[0];
}

function zeroPadding(N, N_max) {
	if ( N_max < 10 ) {
		temp = toString(N); return temp;
	}
	if ( N_max < 100 ) {
		temp = zeroPadding2(N); return temp;
	}
	if ( N_max < 1000 ) {
		temp = zeroPadding3(N); return temp;
	}
	if ( N_max < 10000 ) {
		temp = zeroPadding4(N); return temp;
	}
	else {
		print( "Warning! Maximum >= 10000! Change zeroPadding to account for that.");
		temp = toString(N);
		return temp;
	}
}

function zeroPadding4(t) {
	// pad t to 4 digits when t <10000
	if ( t < 10 ) {
		tPadded = "000" + t; return tPadded;
	}
	if ( t < 100 ) {
		tPadded = "00" + t; return tPadded;
	}
	if ( t < 1000 ) {
		tPadded = "0" + t; return tPadded;
	}
	if ( t < 10000 ) {
		temp = toString(t); return temp;
	}
	else {
		print( "Warning! Maximum >= 10000! Change zeroPadding to account for that.");
		temp = toString(t); return temp;
	}
}

function zeroPadding3(t) {
	// pad t to 3 digits when t <1000
	if ( t < 10 ) {
		tPadded = "00" + t; return tPadded;
	}
	if ( t < 100 ) {
		tPadded = "0" + t; return tPadded;
	}
	if ( t < 1000 ) {
		temp = toString(t); return temp;
	}
	else {
		print( "Warning! Maximum >= 1000! Change zeroPadding to account for that.");
		temp = toString(t); return temp;
	}
}

function zeroPadding2(t) {
	// pad t to 2 digits when t <100
	if ( t < 10 ) {
		tPadded = "0" + t; return tPadded;
	}
	if ( t < 100 ) {
		temp = toString(t); return temp;
	}
	else {
		print( "Warning! Maximum >= 100! Change zeroPadding to account for that.");
		temp = toString(t); return temp;
	}
}
