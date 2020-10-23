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

inputFolderList = newArray('/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/190331-4_K14Rhet-HisG-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180218-mTmGHisG-ROI1-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/190227-mTmGHisG-ROI1-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/190227-mTmGHisG-ROI2-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/200125-K14R-HisG-ROI1-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/190331-1_K14Rhomo-HisG-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/190331-6_K14Rhet-HisG-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180624-mTmGHisG-SMG1-ROI1-dataset-low-quality/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180325-mTmGHisG-ROI1-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180325-mTmGHisG-ROI2-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180624-mTmGHisG-SMG1-ROI2-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180624-mTmGHisG-SMG2-ROI1-dataset/',
							'/Users/wangs20/2-Branching-morphogenesis-paper/Dynamic-line-scan-analysis/180624-mTmGHisG-SMG2-ROI2-dataset/');

datasetPrefixList = newArray('190331-4_K14Rhet-HisG-1-1-denoised-BCratio-img-seq-stacked-z-26',
							'180218-mTmGHisG-ROI1-denoised-BCratio-img-seq-BC-all-z-24',
							'190227-mTmGHisG-2photon-E13-ROI1-denoised-BC-all-mid-plane',
							'190227-mTmGHisG-2photon-E13-ROI2-denoised-BC-all-mid-plane',
							'2020-01-25-K14R-HisG-2photon-25x-2-denoised-ROI1-z-25',
							'190331-1_K14Rhomo-HisG-1-1-denoised-z-27',
							'190331-6_K14Rhet-HisG-2-2-denoised-z-23',
							'180624-2photon-mTmGHisG-SMG1-combined-BC-all-ROI1-z-24-denoised',
							'180325-mTmGHisG-2photon-mosaic-ROI1-denoised-BC-all-z-24',
							'180325-mTmGHisG-2photon-mosaic-ROI2-denoised-BC-all-z-30',
							'180624-2photon-mTmGHisG-SMG1-combined-BC-all-ROI2-z-40-denoised',
							'180624-2photon-mTmGHisG-SMG2-combined-BC-all-ROI1-z-31-denoised',
							'180624-2photon-mTmGHisG-SMG2-combined-BC-all-ROI2-z-36-denoised');

for (i = 0; i < inputFolderList.length; i++) {
//for (i = 0; i < 1; i++) {// To test one file
	inputFolder = inputFolderList[i];
	datasetPrefix = datasetPrefixList[i];
	processDataset(inputFolder, datasetPrefix);
}

function processDataset(inputFolder, datasetPrefix) {
	//inputFile = inputFolder + datasetPrefix + ".tif";
	inputFile = inputFolder + datasetPrefix + "-8bit.tif";
	xyCoorFolder = inputFolder + datasetPrefix + "-linescan-output-t-interpolated" + File.separator;
	outputFolder = inputFolder + datasetPrefix + "-dynamic-line-scan-profile" + File.separator;
	
	if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }
	
	run("Close All");
	run("Clear Results");
	setBatchMode(true);
	c1name = "GFP";// modify accordingly if the channel setting is different
	c2name = "RFP";
	processImageStack(inputFile, outputFolder);
}

function processImageStack(inputFile, outputFolder) {
	open(inputFile); Stack.getDimensions(width, height, channels, slices, frames);
	run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel global");
	
	run("Make Composite");
	Stack.setChannel(1); run("Green");
	//c1Satu = 1; run("Enhance Contrast", "saturated="+c1Satu);
	Stack.setChannel(2); run("Magenta");
	//c2Satu = 1; run("Enhance Contrast", "saturated="+c2Satu);
	
	for (t=1; t<frames+1; t+=1){
	//for (t=frames; t>0; t-=1){
		Stack.setFrame(t);
		xyCoorFile = xyCoorFolder + "t-" + zeroPadding(t) + ".txt";
		if ( !(File.exists(xyCoorFile)) ) {
			// Sometimes the interpolated (x,y) coordinates does not cover the entire time series
			continue;
		}
		run("XY Coordinates... ", "open=["+xyCoorFile+"]");
		run("Enlarge...", "enlarge=-10 pixel");// Note that for most images of time series, 1 pixel = 0.62 um
		run("Interpolate", "interval=1");
		run("Area to Line");
		
		newXYcoorFile = outputFolder + "newXY-t-" + zeroPadding(t) + ".txt";
		saveAs("XY Coordinates", newXYcoorFile);

		// Get profile and display values in "Results" window, save as txt
		outputProfile1 = outputFolder + c1name + "-t-" + zeroPadding(t) + ".txt";
		Stack.setChannel(1);// channel 1, usually GFP
		run("Clear Results");
		profile = getProfile();
		for (j=0; j<profile.length; j++)
			setResult("Value", j, profile[j]);
		updateResults();
		saveAs("Measurements", outputProfile1);

		outputProfile2 = outputFolder + c2name + "-t-" + zeroPadding(t) + ".txt";
		Stack.setChannel(2);// channel 1, usually GFP
		run("Clear Results");
		profile = getProfile();
		for (j=0; j<profile.length; j++)
			setResult("Value", j, profile[j]);
		updateResults();
		saveAs("Measurements", outputProfile2);

	}
	run("Clear Results");
}

function zeroPadding(t) {
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
		return t;
	}
	else {
		print( "Warning! Maximum of t > 1000! Change zeroPadding to account for that.");
		return t;
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

