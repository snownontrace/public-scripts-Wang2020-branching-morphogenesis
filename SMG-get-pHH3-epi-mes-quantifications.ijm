inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All");
setBatchMode(true);

fileList = getFileList(inputFolder);

// Create a text file to store measurement results; use time stamp to keep different versions
timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
f = File.open(parentFolder + inputFolderPrefix + "-pHH3-" + timeStamp + ".txt");
print(f, "filename" + "\t" + 
      "area_epi" + "\t" + "pHH3_thres_area_epi" + "\t" + "percent_pHH3_thres_area_epi" + "\t" + 
      "area_mes" + "\t" + "pHH3_thres_area_mes" + "\t" + "percent_pHH3_thres_area_mes");


for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	if (endsWith(filename, "tif")) {
		open(filename); id0 = getImageID();
//		run("Set Scale...", "distance=0 global");// Remove embedded scale information -- this will affect enlarge commands
		
		roi_file = outputFolder + outputPrefix + "-ROIs.zip"; // output from compute-epi-and-mes-ROIs.ijm
		roiManager("Reset"); // clears ROI manager
		roiManager("open", roi_file);
		
		// Duplicate the pHH3 channel for thresholding
		selectImage(id0); run("Duplicate...", "duplicate channels=3"); idC3 = getImageID();
		selectImage(idC3); run("Gaussian Blur...", "sigma=2");
		selectImage(idC3); setAutoThreshold("Huang dark");
//		setOption("BlackBackground", false);
		call("ij.plugin.frame.ThresholdAdjuster.setMode", "B&W");
		run("Convert to Mask"); idC3Mask = getImageID();

		// Save pHH3 mask
		pHH3_mask_file = outputFolder + outputPrefix + "-ROIs.zip";
		selectImage(idC3Mask); saveAs("Tiff", pHH3_mask_file);
		

		// Measure on thresholded pHH3 and DAPI image
		selectImage(idC3Mask); // thresholded pHH3 mask
		roiManager("Select", 0); // epiROI
		run("Measure"); // thresholded pHH3; epi
		roiManager("Select", 3); // mesROI
		run("Measure"); // thresholded pHH3; mes
		
		// Get the raw measurements
		area_epi = getResult("Area", 0); // unit: square microns
		pHH3_mean_epi = getResult("Mean", 0);
		
		area_mes = getResult("Area", 1);
		pHH3_mean_mes = getResult("Mean", 1);

		pHH3_thres_area_epi = area_epi * getResult("Mean", 0) / 255.0;
		pHH3_thres_area_mes = area_mes * getResult("Mean", 1) / 255.0;

		percent_pHH3_thres_area_epi = getResult("Mean", 0) / 255.0 * 100;
		percent_pHH3_thres_area_mes = getResult("Mean", 1) / 255.0 * 100;
		
		run("Clear Results");
		
		// Record the results
		print(f, outputPrefix + "\t" + 
              area_epi + "\t" + pHH3_thres_area_epi + "\t" + percent_pHH3_thres_area_epi + "\t" + 
              area_mes + "\t" + pHH3_thres_area_mes + "\t" + percent_pHH3_thres_area_mes);
		
		// Close images no longer needed
		run("Close All");
	}
}

File.close(f);

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