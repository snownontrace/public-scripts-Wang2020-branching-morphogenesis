inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-output" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All");
setBatchMode(true);

fileList = getFileList(inputFolder);
//cEpi = 4; // Channel 4 is E-cadherin staining for this dataset

// Create a text file to store measurement results; use time stamp to keep different versions
timeStamp = getTime() % 10000;//last four digits of current time in milliseconds
f = File.open(parentFolder + inputFolderPrefix + "-pHH3-" + timeStamp + ".txt");
print(f, "filename" + "\t" + "area_in" + "\t" + "area_surf" + "\t" + 
		"pHH3_mean_in" + "\t" + "DAPI_mean_in" + "\t" + "Ecad_mean_in" + "\t" + "pHH3_thres_area_in" + "\t" + "DAPI_thres_area_in" + "\t" + 
		"pHH3_mean_surf" + "\t" + "DAPI_mean_surf" + "\t" + "Ecad_mean_surf" + "\t" + "pHH3_thres_area_surf" + "\t" + "DAPI_thres_area_surf");


for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	if (endsWith(filename, "tif")) {
		open(filename); id0 = getImageID();
//		run("Set Scale...", "distance=0 global");// Remove embedded scale information -- this will affect enlarge commands
		
		roi_file = outputFolder + outputPrefix + "-ROIs.zip"; // output from draw-and-compute-epi-ROIs.ijm
		roiManager("Reset"); // clears ROI manager
		roiManager("open", roi_file);
		
		// Duplicate the DAPI channel for thresholding
		selectImage(id0); run("Duplicate...", "duplicate channels=1"); idC1 = getImageID();
		selectImage(idC1); run("Gaussian Blur...", "sigma=2");
		selectImage(idC1); setAutoThreshold("Huang dark"); setOption("BlackBackground", false); run("Convert to Mask"); idC1Mask = getImageID();
//      // Auto local threshold
//		run("Enhance Contrast", "saturated=0.35"); setOption("ScaleConversions", true); run("8-bit");
//		run("Auto Local Threshold", "method=Median radius=15 parameter_1=0 parameter_2=0 white"); idC1Mask = getImageID();

		// Duplicate the pHH3 channel for thresholding
		selectImage(id0); run("Duplicate...", "duplicate channels=3"); idC3 = getImageID();
		selectImage(idC3); run("Gaussian Blur...", "sigma=5");
		selectImage(idC3); setAutoThreshold("Huang dark"); setOption("BlackBackground", false); run("Convert to Mask"); idC3Mask = getImageID();

		
		run("Clear Results");
		
		// Measure mean intensities of channels pHH3 (c3), DAPI (c1) and Ecad (c2)
		selectImage(id0);
		roiManager("Select", 3); // epiTotal ROI
		Stack.setChannel(3); run("Measure"); // pHH3
		Stack.setChannel(1); run("Measure"); // DAPI
		Stack.setChannel(2); run("Measure"); // Ecad
		
		roiManager("Select", 4); // epiInterior ROI
		Stack.setChannel(3); run("Measure"); // pHH3
		Stack.setChannel(1); run("Measure"); // DAPI
		Stack.setChannel(2); run("Measure"); // Ecad

		// Measure on thresholded pHH3 and DAPI image
		
		selectImage(idC3Mask); // thresholded pHH3 mask
		roiManager("Select", 3); // epiTotal ROI
		run("Measure"); // thresholded pHH3; epi
		roiManager("Select", 4); // epiInterior ROI
		run("Measure"); // thresholded pHH3; interior

		selectImage(idC1Mask); // thresholded DAPI mask
		roiManager("Select", 3); // epiTotal ROI
		run("Measure"); // thresholded DAPI; epi
		roiManager("Select", 4); // epiInterior ROI
		run("Measure"); // thresholded DAPI; interior
		
		// Get the raw measurements
		area_epi = getResult("Area", 0); // unit: square microns
		pHH3_mean_epi = getResult("Mean", 0);
		DAPI_mean_epi = getResult("Mean", 1);
		Ecad_mean_epi = getResult("Mean", 2);
		area_in = getResult("Area", 3);
		pHH3_mean_in = getResult("Mean", 3);
		DAPI_mean_in = getResult("Mean", 4);
		Ecad_mean_in = getResult("Mean", 5);
		pHH3_thres_area_epi = area_epi * getResult("Mean", 6) / 255.0;
		pHH3_thres_area_in = area_in * getResult("Mean", 7) / 255.0;
		DAPI_thres_area_epi = area_epi * getResult("Mean", 8) / 255.0;
		DAPI_thres_area_in = area_in * getResult("Mean", 9) / 255.0;
		
		// Calculate the surface layer values
		area_surf = area_epi - area_in;
		pHH3_mean_surf = (area_epi * pHH3_mean_epi - area_in * pHH3_mean_in) / area_surf;
		DAPI_mean_surf = (area_epi * DAPI_mean_epi - area_in * DAPI_mean_in) / area_surf;
		Ecad_mean_surf = (area_epi * Ecad_mean_epi - area_in * Ecad_mean_in) / area_surf;
		pHH3_thres_area_surf = pHH3_thres_area_epi - pHH3_thres_area_in;
		DAPI_thres_area_surf = DAPI_thres_area_epi - DAPI_thres_area_in;
		run("Clear Results");
		
		// Record the results
		print(f, outputPrefix + "\t" + area_in + "\t" + area_surf + "\t" + 
				pHH3_mean_in + "\t" + DAPI_mean_in + "\t" + Ecad_mean_in + "\t" + pHH3_thres_area_in + "\t" + DAPI_thres_area_in + "\t" + 
				pHH3_mean_surf + "\t" + DAPI_mean_surf + "\t" + Ecad_mean_surf + "\t" + pHH3_thres_area_surf + "\t" + DAPI_thres_area_surf);
		
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