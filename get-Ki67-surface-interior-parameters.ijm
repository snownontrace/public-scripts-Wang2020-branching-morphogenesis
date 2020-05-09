inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All");
run("Clear Results");
setBatchMode(true);

fileList = getFileList(inputFolder);
// Create a text file to store measurement results; use time stamp to keep different versions
timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
f = File.open(parentFolder + inputFolderPrefix + "-pHH3-" + timeStamp + ".txt");
print(f, "filename" + "\t" + "area_in" + "\t" + "area_surf" + "\t" + "Ki67_thres_area_in" + "\t" + "Ki67_thres_area_surf");

for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	if (endsWith(filename, "tif")) {
		open(filename); id = getImageID();
		type = "20x-slice";
		set_YGMC(id, type);

		idMaskTotal = getMaskTotal(id);
		idMaskInterior = getMaskInterior(id);
		idMaskKi67 = getMaskKi67(id);
//		selectImage(id); run("Duplicate...", "duplicate channels=4"); idC4 = getImageID();

		run("Clear Results");
		// Make epithelial selection from the mask, and measure the segmented idMaskKi67
		selectImage(idMaskTotal); run("Select None"); run("Create Selection");
		selectImage(idMaskKi67); run("Restore Selection"); run("Measure"); // epi total

		// Make epithelial selection from the mask, and measure the segmented idMaskKi67
		selectImage(idMaskInterior); run("Select None"); run("Create Selection");
		selectImage(idMaskKi67); run("Restore Selection"); run("Measure"); // interior total
		
		// Get the raw measurements
		area_epi = getResult("Area", 0); // unit: square microns
		Ki67_mean_epi = getResult("Mean", 0);
		area_in = getResult("Area", 1);
		Ki67_mean_in = getResult("Mean", 1);
		// Calculate the threshold area using mean intensity measurements on thresholded images
		Ki67_thres_area_epi = area_epi * Ki67_mean_epi / 255.0;
		Ki67_thres_area_in = area_in * Ki67_mean_in / 255.0;
		// Calculate the surface layer values
		area_surf = area_epi - area_in;
		Ki67_thres_area_surf = Ki67_thres_area_epi - Ki67_thres_area_in;
		
		// Record the results
		print(f, outputPrefix + "\t" + area_in + "\t" + area_surf + "\t" + Ki67_thres_area_in + "\t" + Ki67_thres_area_surf);

		// Save mask files
		selectImage(idMaskTotal); saveAs("tiff", outputFolder + outputPrefix + "-total-epithelial-mask.tif");
		selectImage(idMaskInterior); saveAs("tiff", outputFolder + outputPrefix + "-interior-epithelial-mask.tif");
		selectImage(idMaskKi67); saveAs("tiff", outputFolder + outputPrefix + "-Ki67-mask.tif");
		
		run("Close All");
		run("Clear Results");
	}
}

File.close(f);

function set_YGMC(id, type){
	// This function sets the color scheme and composite of a 4-channel image
	
	selectImage(id);
	Stack.setChannel(1);
	run("Yellow");
	Stack.setChannel(2);
	run("Green");
	Stack.setChannel(3);
	run("Magenta");
	Stack.setChannel(4);
	run("Cyan");
	run("Make Composite");

	if (type == "MIP") {
		Stack.setChannel(1); run("Enhance Contrast", "saturated=0.35");
		Stack.setChannel(2); setMinAndMax(60, 5000);
		Stack.setChannel(3); setMinAndMax(30, 800);
		Stack.setChannel(4); setMinAndMax(120, 1200);
	}

	if (type == "20x-slice") {
		Stack.setChannel(1); setMinAndMax(20, 1000);
		Stack.setChannel(2); setMinAndMax(20, 3000);
		Stack.setChannel(3); setMinAndMax(20, 4095);
		Stack.setChannel(4); setMinAndMax(100, 2000);
	}

	if (type == "60x-slice") {
		Stack.setChannel(1); setMinAndMax(15, 1200);
		Stack.setChannel(2); setMinAndMax(20, 1700);
		Stack.setChannel(3); setMinAndMax(40, 1000);
		Stack.setChannel(4); setMinAndMax(190, 2000);
	}
	
	return id;
}

function getMaskTotal(id) {
	// This function uses the MIP of fluorescence of DLD-1 spheroid images to segment out the region of the entire cross-section
	selectImage(id); run("Duplicate...", "duplicate channels=2-3"); idC23 = getImageID();
	selectImage(idC23); run("Z Project...", "projection=[Max Intensity]"); idMIP = getImageID();
	selectImage(idMIP); run("Gaussian Blur...", "sigma=10");
	setAutoThreshold("Huang dark");
	setOption("BlackBackground", false);
	call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
	run("Convert to Mask");
	selectImage(idMIP); run("Keep Largest Region"); run("Fill Holes"); idMaskTotal = getImageID();
	// Close intermediate images
	selectImage(idMIP); run("Close");
	selectImage(idC23); run("Close");
	return idMaskTotal;
}

function getMaskInterior(id) {
	// This function uses the second channel (green) of DLD-1 spheroid images to segment out the region of interior
	selectImage(id); run("Duplicate...", "duplicate channels=2"); idC2 = getImageID();
	selectImage(idC2); run("Gaussian Blur...", "sigma=10");
	setAutoThreshold("Huang dark");
	setOption("BlackBackground", false);
	call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
	run("Convert to Mask");
	run("Fill Holes"); return idC2;
//	selectImage(idC2); run("Keep Largest Region"); run("Fill Holes"); idMaskInterior = getImageID();
//	// Close intermediate images
//	selectImage(idC2); run("Close");
//	return idMaskInterior;
}

function getMaskKi67(id) {
	// This function uses the second channel (green) of DLD-1 spheroid images to segment out the region of interior
	selectImage(id); run("Duplicate...", "duplicate channels=4"); idC4 = getImageID();
	selectImage(idC4); run("Gaussian Blur...", "sigma=2"); 
	setAutoThreshold("Default dark");
	setOption("BlackBackground", false);
	call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
	run("Convert to Mask");
	
	return idC4;
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