inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-stacks" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

run("Close All");
setBatchMode(true);


nChannel = 1;
nSlice = 3;
c1Saturation = 2;
c2Saturation = 2;

flist = getFileList(inputFolder);

//for (i=0; i<1; i++) {//for testing
for (i=0; i<flist.length; i++) {
	
	folder = inputFolder + flist[i];
	outputPrefix = getPathFilenamePrefix(flist[i]);
	
	if ( endsWith(folder, File.separator) ) {
		
		run("Image Sequence...", "open=["+folder+"] sort");
		
		nFrame = nSlices/nChannel/nSlice;
		run("Stack to Hyperstack...", "order=xyczt(default) channels="+nChannel+" slices="+nSlice+" frames="+nFrame+" display=Composite");
		id0 = getImageID();
		run("Properties...", "channels="+nChannel+" slices="+nSlice+" frames="+nFrame+" unit=micron pixel_width=0.62 pixel_height=0.62 voxel_depth=2 frame=[300 sec]");
		
		zMid = floor(nSlice/2) + 1;
		
//		Stack.setChannel(1);
//		run("Green");
//		Stack.setSlice(zMid);
//		run("Enhance Contrast", "saturated="+c1Saturation);
//		
//		Stack.setChannel(2);
//		run("Magenta");
//		Stack.setSlice(zMid);
//		run("Enhance Contrast", "saturated="+c2Saturation);

//		selectImage(id0);
//		run("Z Project...", "projection=[Max Intensity] all");
//		idMIP = getImageID();
//		saveAs("Tiff", outputFolder + outputPrefix + "-MIP.tif");

		selectImage(id0);
		run("Duplicate...", "duplicate slices="+zMid);
		idMidZ = getImageID();
		
		saveAs("Tiff", outputFolder + outputPrefix + "-midZ.tif");

		run("Close All");
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