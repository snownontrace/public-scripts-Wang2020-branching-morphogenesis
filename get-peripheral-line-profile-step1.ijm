// This macro generates a set of periphery bud line profile of both image channels through a 2-step process.
//
// In the first step, user drawing are required:
// 1. User draw a segmented line along the bud surface
// 2. The drawn line x,y coordinates were saved into a text file
// 
// To reduce amount of drawing, the script asks to draw every 12 frames.
// Customized Python scripts are needed to interpolate the time points in between (2nd step).
// This step is implemented by the "interpPolylineT" and "savePathSeries" functions
// in the jupyter-notebook script "Dynamic-line-scan-modularized."
//
// In the macro of the third step:
// 3. Interpolated x,y coordinates at each time point are loaded onto the image,
//    forming a closed area by joining the end points
// 4. Spline fit and interpolate the area ROI, transform it into a line ROI
// 5. Get the profile of both channels and save them into text files
//
// Note: when changing the area to be a line selection, the polygon is split at the bottom-most point,
// which is usually not the neck of the bud. To clip the line profile, a Python script needs to be run
// to correspond the beginning and end point of the new line coordinates

run("Close All");
tStep = 12; // in frame number; interval is mostly 5 min


inputFolder = "/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/190227-mTmGHisG-ROI1-dataset/";
inputFile = inputFolder + "190227-mTmGHisG-2photon-E13-ROI1-denoised-BC-all-mid-plane.tif";

// Use time stamp to avoid over-writing previously saved files
timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
//timeStamp = 9961;
t_start = 112;
t_end = 134;
t_step = 12;
processImageStackSpecifiyTrange(inputFile, t_start, t_end, t_step);

//inputFolder = getDirectory("Choose the folder containing images to process:");
//processFolder(inputFolder);

function processFolder(inputFolder) {
	flist = getFileList(inputFolder);
	//for (i=0; i<1; i++) {//for testing
	for (i=0; i<flist.length; i++) {
	
		filename = inputFolder + flist[i];	
		
		if ( endsWith(filename, ".nd2") || endsWith(filename, ".czi") || endsWith(filename, ".tif") ) {
			processImageStack(filename);
			
	//		t_start = 150;
	//		t_end = 160;
	//		t_step = 1;
	//		processImageStackSpecifiyTrange(inputFile, t_start, t_end, t_step);
		}
	}
}

function processImageStackSpecifiyTrange(inputFile, t_start, t_end, t_step) {
	
	outputPrefix = getPathFilenamePrefix(inputFile);
	if (timeStamp != 0) {
		outputFolder = inputFolder + outputPrefix + "-linescan-output-" + timeStamp + File.separator;
		roiFolder = inputFolder + outputPrefix + "-ROI-output-" + timeStamp + File.separator;
	}
	else {
		outputFolder = inputFolder + outputPrefix + "-linescan-output" + File.separator;
		roiFolder = inputFolder + outputPrefix + "-ROI-output" + File.separator;
	}
	if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }
	if ( !(File.exists(roiFolder)) ) { File.makeDirectory(roiFolder); }
			
	open(inputFile);
	id = getImageID();
	Stack.getDimensions(width, height, channels, slices, frames);
	// Use pixel units
	run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel global");
	run("In [+]");
	//run("In [+]");
	run("Make Composite");
	Stack.setChannel(1); run("Green");
	c1Satu = 1; run("Enhance Contrast", "saturated="+c1Satu);
	Stack.setChannel(2); run("Magenta");
	c2Satu = 1; run("Enhance Contrast", "saturated="+c2Satu);
	
	for (t=t_end; t>t_start-1; t-=t_step){
		tPadded = zeroPadding(t, frames);
		roiFile = roiFolder +  "t-" + tPadded + ".roi";
		outFilename = outputFolder + "t-" + tPadded + ".txt";

//		if ( (t==t_end) && (File.exists(roiFile)) ) {
		if ( File.exists(roiFile) ) {
		// If it is there, open to serve as a guide!
			roiManager("Reset");// Clear off existing ROIs in the manager
			roiManager("Open", roiFile);
			roiManager("Select", 0);
		}
		Stack.setFrame(t);
		setTool("polyline");
		waitForUser("Draw ***clockwise*** along the bud surface");

		roiManager("Reset");// Clear off existing ROIs in the manager
		Stack.setFrame(t-tStep);
		roiManager("Add"); roiManager("Select", 0);

		// save the ROI in case in the future you want to import it for adjustment
		roiManager("Save", roiFile);

		// save the polygon anchor point (x,y) list for interpolation and analysis
		selectImage(id);
		saveAs("XY Coordinates", outFilename);
		//run("Select None");
	}
	roiManager("Reset");
	setTool("rectangle");
	run("Close All");

}

function processImageStack(inputFile, outputFolder, roiFolder) {
	open(inputFile);
	id = getImageID();
	Stack.getDimensions(width, height, channels, slices, frames);
	// Use pixel units
	run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel global");
	run("In [+]");
	//run("In [+]");
	run("Make Composite");
	Stack.setChannel(1); run("Green");
	c1Satu = 1; run("Enhance Contrast", "saturated="+c1Satu);
	Stack.setChannel(2); run("Magenta");
	c2Satu = 1; run("Enhance Contrast", "saturated="+c2Satu);
	
	//for (t=1; t<frames+1; t+=tStep){
	for (t=frames; t>0; t-=tStep){
		Stack.setFrame(t);
		setTool("polyline");
		waitForUser("Draw ***clockwise*** along the bud surface");

		roiManager("Reset");// Clear off existing ROIs in the manager
		Stack.setFrame(t-tStep);
		roiManager("Add"); roiManager("Select", 0);

		// save the ROI in case in the future you want to import it for adjustment
		tPadded = zeroPadding(t, frames);
		roiFile = roiFolder +  "t-" + tPadded + ".roi";
		roiManager("Save", roiFile);

		// save the polygon anchor point (x,y) list for interpolation and analysis
		selectImage(id);
		outFilename = outputFolder + "t-" + tPadded + ".txt";
		saveAs("XY Coordinates", outFilename);
		//run("Select None");
	}
	roiManager("Reset");
	setTool("rectangle");
	run("Close All");
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
	// pad t to 4 digits when t <1000
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
	// pad t to 4 digits when t <1000
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
	// pad t to 4 digits when t <1000
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

