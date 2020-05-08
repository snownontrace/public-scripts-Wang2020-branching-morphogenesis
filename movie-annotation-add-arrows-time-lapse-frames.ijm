id=getImageID();
arrow_ROI_folder = "/Volumes/ShaoheGtech2/2019-spheroids-live-time-lapse/Movie10-arrow-ROIs/";
ROI_output_file = arrow_ROI_folder +  "cleft-initiation-arrow3-RoiSet.zip"
draw_arrow(id, ROI_output_file);

function draw_arrow(id, ROI_output_file) {
	selectImage(id); Stack.getDimensions(width, height, channels, slices, frames);
	if ( !(File.exists(ROI_output_file)) ) {
		roiManager("reset");
//		for (i = 1; i < frames+1; i++) {
		for (i = frames; i > 0; i--) {
//		for (i = frames; i > 139; i--) {
			Stack.setFrame(i);
			setTool("arrow");
			waitForUser("Draw or move the arrow:");
			//makeArrow(783, 116, 706, 236, "notched");
			//Roi.setStrokeWidth(4);
			//Roi.setStrokeColor("white");
			roiManager("add");
			setForegroundColor(255, 255, 255);
			run("Draw", "slice");
		}
		roiManager("save", ROI_output_file);
	}
	else {
		roiManager("reset");
		roiManager("open", ROI_output_file);
		nROIs = roiManager("count");
		for (i = 0; i < nROIs; i++) {
			roiManager("select", i);
			setForegroundColor(255, 255, 255);
			run("Draw", "slice");
		}
		roiManager("reset");
	}
}