setBatchMode(true);
roiFilename = getArgument();

// create 2 folders for the two sets of mesh polylines
temp = split(roiFilename, ".");
outputFolder1 = temp[0] + "-1" + File.separator;
outputFolder2 = temp[0] + "-2" + File.separator;
if (!(File.exists(outputFolder1))) { File.makeDirectory(outputFolder1); }
if (!(File.exists(outputFolder2))) { File.makeDirectory(outputFolder2); }

// clears roi manager and loads the roi set
roiManager("reset");
roiManager("Open",roiFilename);
// get some basic numbers for parsing
roiN = roiManager("count");
// create an empty image as a holder
newImage("temp.tif", "8-bit black", 1500, 1500, 1);
run("Properties...", "channels=1 slices=1 frames=1 unit=micron"+
	"pixel_width=0.62 pixel_height=0.62 voxel_depth=2 frame=[300 sec]");

for (i=0; i<roiN/2; i+=1){
	roiManager("select", i);
	roiName = call("ij.plugin.frame.RoiManager.getName", i);
	outFilename = outputFolder1 + roiName;
	saveAs("XY Coordinates", outFilename);
}

for (i=roiN/2; i<roiN; i+=1){
	roiManager("select", i);
	roiName = call("ij.plugin.frame.RoiManager.getName", i);
	outFilename = outputFolder2 + roiName;
	saveAs("XY Coordinates", outFilename);	
}

//run("Close All");