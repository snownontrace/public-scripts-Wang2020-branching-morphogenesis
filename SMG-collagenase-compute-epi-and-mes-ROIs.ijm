inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All"); roiManager("Reset");
setBatchMode(true);

fileList = getFileList(inputFolder);

for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	if (endsWith(filename, "tif")) {
		
		open(filename); id = getImageID();
		
		cDAPI = 1; // Channel 1 is DAPI for this dataset
		cEpi = 4; // Channel 4 is E-cadherin staining for this dataset
		computeROIs(id, cDAPI, cEpi, outputFolder, outputPrefix);

		run("Close All"); roiManager("Reset");
	}
}


//// Testing 1 image
//i = 0;
//filename = inputFolder+fileList[i];
//outputPrefix = getFilenamePrefix(fileList[i]);
//open(filename); id = getImageID();
//cDAPI = 1; // Channel 1 is DAPI for this dataset
//cEpi = 4; // Channel 4 is E-cadherin staining for this dataset
//computeROIs(id, cDAPI, cEpi, outputFolder, outputPrefix);


function computeROIs(id, cDAPI, cEpi, outputFolder, outputPrefix) {
// For a given image id, use the cDAPI cEpi channel to segment a 
// binary mask of the epithelial and mesenchyme area.
//
// If an ROI file is already there, open and used it directly.
// Otherwise, do segmentation and save the ROIs for future use.
	
	roi_file = outputFolder + outputPrefix + "-ROIs.zip";

	roiManager("Reset"); // clears ROI manager
	
	if ( File.exists(roi_file) ) {
		roiManager("open", roi_file);
	}
	else {
		idEpiMask = getEpiMask(id, cEpi, outputFolder, outputPrefix);
		selectImage(idEpiMask); roiManager("Add"); // roi 0 in manager; epiROI

		idDapiMask = getDapiMask(id, cDAPI, outputFolder, outputPrefix);
		selectImage(idDapiMask); roiManager("Add"); // roi 1 in manager; DAPI ROI

		// ROI intersection to create epiTotal or epiInterior ROIs
		roiManager("Select", newArray(0,1)); roiManager("AND"); roiManager("Add"); // roi 2 in manager; epiROI within DPAI ROI
		roiManager("Select", newArray(1,2)); roiManager("XOR"); roiManager("Add"); // roi 3 in manager; mesROI
		
		// save ROI set for segmentation
		roiManager("deselect");
		roiManager("save", roi_file);
	}
	
	return roi_file;
}

function getDapiMask(id, cDAPI, outputFolder, outputPrefix) {
// For a given image id, use the DAPI channel to segment a 
// binary mask of the cell area.
//
// This procedure automatically ignores the dim DAPI area that
// is frequently observed in tissue interior presumably due to
// compromised light scattering, which is more severe in 40x water
// objective images than in 60x oil immersion obejective images
// where samples have been mounted in ProLong Gold mountant and
// cured for > 24 hours.
// 
// If a mask file is already there, open and used it directly.
// Otherwise, do segmentation and save the mask for future use.

	dapi_mask_file = outputFolder + outputPrefix + "-dapi-mask.tif";
	
	if ( File.exists(dapi_mask_file) ) {
		// Facilitates re-run when modifying processing parameters
		open(dapi_mask_file); idDAPI = getImageID();
	}
	else {
		// Duplicate the E-cadherin channel for segmentation of the epithelial area
		selectImage(id); run("Select None"); run("Duplicate...", "duplicate channels="+cDAPI); idDAPI = getImageID();
		selectImage(idDAPI); run("Gaussian Blur...", "sigma=50");
		selectImage(idDAPI); setAutoThreshold("Huang dark");
//		setOption("BlackBackground", false);
		call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
		run("Convert to Mask");
//		// Save the segmented binary image
		selectImage(idDAPI); saveAs("tiff", dapi_mask_file);
	}

	// Make epithelial selection from the binary mask
	selectImage(idDAPI); run("Select None"); run("Create Selection");
	
	return idDAPI;
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
		open(epi_mask_file); idEpi = getImageID();
	}
	else {
		// Duplicate the E-cadherin channel for segmentation of the epithelial area
		selectImage(id); run("Select None"); run("Duplicate...", "duplicate channels="+cEpi); idEpi = getImageID();
		selectImage(idEpi); run("Gaussian Blur...", "sigma=20");
		selectImage(idEpi); setAutoThreshold("Huang dark");
//		setOption("BlackBackground", false);
		call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
		run("Convert to Mask");
		
		// Adjust segmented epithelial mask to match boundary defined by collagen IV staining
		// Due to the 20 µm thickness of z-projection, shrinking by 5 µm matches quite well
		// The Morphological Filters erosion retains the edge on the imaging border, a nice feature useful here.
		getPixelSize(unit, pixelWidth, pixelHeight);
		adjust_shrinkage = floor(5/pixelWidth);
//		print(pixelWidth);
//		print(adjust_shrinkage);
		selectImage(idEpi); run("Morphological Filters", "operation=Erosion element=Disk radius="+adjust_shrinkage);
		// Save the segmented binary image
		selectImage(idEpi); saveAs("tiff", epi_mask_file);
	}

	// Make epithelial selection from the binary mask
	selectImage(idEpi); run("Select None"); run("Create Selection");
	
	return idEpi;
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