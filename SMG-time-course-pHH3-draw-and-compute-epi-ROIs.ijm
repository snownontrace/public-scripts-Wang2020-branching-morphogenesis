inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All"); roiManager("Reset");
setBatchMode(false);

fileList = getFileList(inputFolder);

for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	if (endsWith(filename, "tif")) {
		open(filename); id0 = getImageID();
		cEpi = 4; // Channel 4 is E-cadherin staining for this dataset
		
		drawEpiROI(id0, cEpi, outputFolder, outputPrefix);
		getEpiROIs(id0, cEpi, outputFolder, outputPrefix);

		run("Close All"); roiManager("Reset");
	}
}

function drawEpiROI(id, cEpi, outputFolder, outputPrefix) {
// For a given image id, ask user to draw a polygon ROI, which is later used to
// intersect with the epithelial mask (or the shrinked interior mask) to get
// two fan-shaped epithelial ROIs (epiTotal and epiInterior).
//
// If an ROI file is already there, skip and go to the next image.
	
	roi_file = outputFolder + outputPrefix + "-user-ROI.roi";
	
	if ( File.exists(roi_file) ) {
		return roi_file;
	}
	else {
		// Ask user to draw a polygon ROI to intersect with the 
		// epithelial mask to get a fan-shaped epithelial ROI.
		selectImage(id0); Stack.setChannel(cEpi);
		setTool("polygon");
		waitForUser("Draw a polygon ROI to intersect with the epithelial mask.\nNote the purpose is to get a fan-shaped slice of the epithelial bud.\nTry to get as large a selection as possible!");
		
		roiManager("Reset"); roiManager("Add"); // roi 0 in manager
		
		// save selected roi
		roiManager("Select", 0); roiManager("save", roi_file);
		
		// Reset tool
		setTool("rectangle");

		return roi_file;
	}
}

function getEpiROIs(id, cEpi, outputFolder, outputPrefix) {
// For a given image id, use the cEpi channel to segment a 
// binary mask of the epithelial area.
//
// Then ask user to draw a polygon ROI to intersect with the
// epithelial mask (or the shrinked interior mask) to get
// two fan-shaped epithelial ROIs (epiTotal and epiInterior.
//
// If an ROI file is already there, open and used it directly.
// Otherwise, do segmentation and save the ROIs for future use.
	
	roi_file = outputFolder + outputPrefix + "-ROIs.zip";
	user_roi_file = outputFolder + outputPrefix + "-user-ROI.roi";

	roiManager("Reset"); // clears ROI manager
	
	if ( File.exists(roi_file) ) {
		roiManager("open", roi_file);
	}
	else {
		idEpiMask = getEpiMask(id, cEpi, outputFolder, outputPrefix);
		selectImage(idEpiMask); roiManager("Add"); // roi 0 in manager

		if ( File.exists(user_roi_file) ) {
			roiManager("open", user_roi_file); // roi 1 in manager
		}
		else {
			// Ask user to draw a polygon ROI to intersect with the 
			// epithelial mask to get a fan-shaped epithelial ROI.
			selectImage(id); Stack.setChannel(cEpi);
			setTool("polygon");
			waitForUser("Draw a polygon ROI to intersect with the epithelial mask\nNote the purpose is to get a fan-shaped slice of the epithelial bud");
			roiManager("Add"); // roi 1 in manager
		}
		
		surfaceHeight = 15; // in microns
		selectImage(idEpiMask); run("Enlarge...", "enlarge=-"+surfaceHeight); // when not specified pixel, enlarge is in scaled units (microns)
		roiManager("Add"); // roi 2 in manager
		
		// ROI intersection to create epiTotal or epiInterior ROIs
		roiManager("Select", newArray(0,1)); roiManager("AND"); roiManager("Add"); // roi 3 in manager; epiTotal
		roiManager("Select", newArray(1,2)); roiManager("AND"); roiManager("Add"); // roi 4 in manager; epiInterior
		
		// save ROI set for segmentation
		roiManager("deselect");
		roiManager("save", roi_file);
		
		// Reset tool
		setTool("rectangle");
	}
	
	return roi_file;
}

function getEpiMask(id, cEpi, outputFolder, outputPrefix) {
// For a given image id, use the cEpi channel to segment a 
// binary mask of the epithelial area.
//
// If a mask file is already there, open and used it directly.
// Otherwise, do segmentation and save the mask for future use.

	epi_mask_file = outputFolder + outputPrefix + "-epi-mask.tif";
	
	if ( File.exists(epi_mask_file) ) {
		// Facilitates re-run when modifying processing parameters
		open(epi_mask_file); idMask = getImageID();
	}
	else {
		// Duplicate the E-cadherin channel for segmentation of the epithelial area
		selectImage(id); run("Select None"); run("Duplicate...", "duplicate channels="+cEpi); idEpi = getImageID();
		selectImage(idEpi); run("Gaussian Blur...", "sigma=20");
		selectImage(idEpi); setAutoThreshold("Huang dark"); setOption("BlackBackground", false); run("Convert to Mask");
		selectImage(idEpi); run("Keep Largest Region"); idMask = getImageID();
		selectImage(idEpi); run("Close");
		// Save the segmented binary image
		selectImage(idMask); saveAs("tiff", epi_mask_file);
	}

	// Make epithelial selection from the binary mask
	selectImage(idMask); run("Select None"); run("Create Selection");
	// Adjust segmented epithelial mask to match boundary defined by collagen IV staining
	// Due to the 10 µm thickness of z-projection, shrinking by 4 µm matches quite well
	run("Enlarge...", "enlarge=-4");
	
	return idMask;
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