inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
roiFolder = parentFolder + inputFolderPrefix + "-ROIs" + File.separator;
outputFolder = parentFolder + inputFolderPrefix + "-mesenchyme-images" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All"); roiManager("reset");
setBackgroundColor(0, 0, 0); // set background to be black
setBatchMode(true);

fileList = getFileList(inputFolder);

for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	
	if (endsWith(filename, "nd2")) {
		roi_file = roiFolder + outputPrefix + ".roi";
		merged_file = outputFolder + outputPrefix + "-mesenchyme.tif";
//		merged_file = outputFolder + outputPrefix + "-mesenchyme.jpg";
		
		open(filename); id0 = getImageID();
		selectImage(id0); run("Duplicate...", "duplicate channels=1"); rename("DAPI");
		selectWindow("DAPI");
		saturation=0.35; run("Enhance Contrast", "saturated="+saturation); run("8-bit");
		
		selectImage(id0); run("Duplicate...", "duplicate channels=3"); rename("actin");
		selectWindow("actin");
		saturation=0.35; run("Enhance Contrast", "saturated="+saturation); run("8-bit");
		
		run("Merge Channels...", "c1=actin c2=DAPI c3=actin");	rename("merged");
		selectWindow("merged");
		roiManager("reset"); roiManager("Open", roi_file); roiManager("Select", 0);
		run("Clear", "slice");

		selectWindow("merged");
		saveAs("Tiff", merged_file);
		
		run("Close All");
	}
}

run("Close All"); roiManager("reset");


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