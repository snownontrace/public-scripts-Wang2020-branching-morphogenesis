inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-ROIs" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All"); roiManager("reset");
setBatchMode(false);

fileList = getFileList(inputFolder);

for (i=0; i<fileList.length; i++) {
	filename = inputFolder+fileList[i];
	outputPrefix = getFilenamePrefix(fileList[i]);
	
	if (endsWith(filename, "nd2")) {
		open(filename); id0 = getImageID();
//		run("Set Scale...", "distance=0 global");// Remove embedded scale information -- this will affect enlarge commands
		roi_file = outputFolder + outputPrefix + ".roi";
		if ( File.exists(roi_file) ) {
			print("Corresponding ROI already exisits! Delete it to re-draw.")
			continue;
		}
		else {
			selectImage(id0);
			Stack.setChannel(4); // E-cadherin channel
			saturation=1.0; run("Enhance Contrast", "saturated="+saturation);
			setTool("polygon");
			waitForUser("Draw a polygon around the epithelium:");
			roiManager("reset");
			roiManager("add");
			roiManager("select", 0);
			roiManager("save", roi_file);
		}
		run("Close All");
	}
}

// reset tool to default
setTool("rectangle");

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