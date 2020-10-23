inputFolder = getDirectory("Choose the folder containing images to process:");
// Create an output folder based on the inputFolder
parentFolder = getPath(inputFolder); inputFolderPrefix = getPathFilenamePrefix(inputFolder);
outputFolder = parentFolder + inputFolderPrefix + "-equalized-frames" + File.separator;
if ( !(File.exists(outputFolder)) ) { File.makeDirectory(outputFolder); }

// Determine whether a matching record file is there
// If yes, use the information to do the matching; no user input is needed.
// If not, create one and record the information for future re-run; user input is required
cell_division_matching_record_file = outputFolder + "180218-mTmGHisG-ROI1-cell-division-matching-record-file.txt";
if ( !(File.exists(cell_division_matching_record_file)) ) {
	record_exist = false;
	record_f = File.open(cell_division_matching_record_file);
	print(record_f, "title_long" + "\t" + "pre_division_frame"); // "\t" specifies the tab
}
else {
	record_exist = true;
	
	// Read in the record, store the information in 2 arrays
	filestring = File.openAsString(cell_division_matching_record_file);
	rows = split( filestring, "\n" ); // Use line breaks to get rows
	title_long_arr = newArray( rows.length-1 ); // "-1" because there is header
	pre_division_frame_arr = newArray( rows.length-1 ); // "-1" because there is header
	
	for(i=1; i<rows.length; i++){ // i starts from 1 to skip the header row
		columns = split(rows[i],"\t");
		title_long_arr[i-1] = columns[0]; //this is the 1st column
		pre_division_frame_arr[i-1] = parseInt(columns[1]); //this is the 2nd column
	}
}



run("Close All");

// frame_max = 157; // from Track_ID = 95 -- just FYI
N_beginning_repeat = 12; // add this many frames to the beginning to simulate freezing of 1st frame
frame_max= 200; // make all movies to be this many frames so that the first and final frames will freeze for a while
N_cell_division = 42; // This is the total number of tracked cell divisions

fList = getFileList(inputFolder);

//for (i=0; i<1; i++) {//for testing
for (i=0; i<N_cell_division; i++) {
	
	// Implement user inspection if record file does not exist,
	// at the same time create the record file
	if ( !record_exist ) {
		// Open the pair of files from the same cell division
		setBatchMode(true);
		
		f1 = inputFolder + fList[2*i];
		open(f1);
		id1 = getImageID();
		title1 = getTitle();
		temp = split(title1, "-");
		title1 = toLowerCase(temp[1]);
		rename(title1);// use the simplified title: only the cell division ID, e.g. 1A, 1B...
		t_start_1 = get_t_from_slice_label(id1);
		
		
		f2 = inputFolder + fList[2*i+1];
		open(f2);
		id2 = getImageID();
		title2 = getTitle();
		temp = split(title2, "-");
		title2 = toLowerCase(temp[1]);
		rename(title2);// use the simplified title: only the cell division ID, e.g. 1A, 1B...
		t_start_2 = get_t_from_slice_label(id2);

		if ( t_start_1 < t_start_2 ) {
			title_long = title1;
			pre_division_frame = t_start_2 - t_start_1;
		}
		else {
			title_long = title2;
			pre_division_frame = t_start_1 - t_start_2;
		}
		
		print(record_f, title_long + "\t" + pre_division_frame); // "\t" specifies the tab

		// The code block below provides a manual curation interface, in case slice label was not included or problematic
		
//		// User selection of the series and frame prior to cell division
//		// Note that "long" and "short" here only denotes whether the series contains the pre-division frames,
//		// but they do not necessarily correspond to longer or shorter time of returning to the surface
//		setBatchMode(false);
//		
//		selectImage(id1);
//		run("In [+]");
//		run("In [+]");
//		
//		selectImage(id2);
//		run("In [+]");
//		run("In [+]");
//		
//		run("Tile");
//		waitForUser("Identify the time series containing the pre-division part.\n Stop at the frame right before the anaphase onset.");
//		title_long = getTitle();
//		Stack.getPosition(current_channel, current_slice, pre_division_frame);
//		print(record_f, title_long + "\t" + pre_division_frame); // "\t" specifies the tab
	}
	
	else {
		setBatchMode(true);
		
		f1 = inputFolder + fList[2*i];
		open(f1);
		id1 = getImageID();
		title1 = getTitle();
		temp = split(title1, "-");
		title1 = toLowerCase(temp[1]);
		rename(title1);// use the simplified title: only the cell division ID, e.g. 1A, 1B...
				
		f2 = inputFolder + fList[2*i+1];
		open(f2);
		id2 = getImageID();
		title2 = getTitle();
		temp = split(title2, "-");
		title2 = toLowerCase(temp[1]);
		rename(title2);// use the simplified title: only the cell division ID, e.g. 1A, 1B...

		title_long = title_long_arr[i];
		temp = split(title_long, "-");
		if ( temp.length > 1 ) {
			// In case the record file was created befroe the script changes to use short titles,
			// this statement transforms the format of recorded title_long to match the short format
			title_long = toLowerCase(temp[1]);
		}
		pre_division_frame = pre_division_frame_arr[i];
	}

	// No user interaction is required any more in any case
	setBatchMode(true);
	
	if ( title_long == title1 ) {
		id_long = id1; title_long = title1;
		id_short = id2; title_short = title2;
	}
	else {
		id_long = id2; title_long = title2;
		id_short = id1; title_short = title1;
	}

	// Add the pre-division frames to the id_short images
	id_short = matching_first_n_frames(id_short, id_long, pre_division_frame);

	// Label the two image series with the cell division id as title, add time stamps to the lower left corner
	label_spot_series(id_long, pre_division_frame);
	label_spot_series(id_short, pre_division_frame);
	
	// Before adding the repeating frames at the beginning and the end, record the duration of this tracked cell divisions
	selectImage(id_long); duration_long = nSlices;
	selectImage(id_short); duration_short = nSlices;
	duration = maxOf(duration_long, duration_short);

	// Append specified number of repeating frames to the beginning and the end of each series
	id_long = repeat_N_first_frames(id_long, N_beginning_repeat);
	selectImage(id_long); N_ending_repeat = frame_max - nSlices;
	id_long = repeat_N_last_frames(id_long, N_ending_repeat);

	id_short = repeat_N_first_frames(id_short, N_beginning_repeat);
	selectImage(id_short); N_ending_repeat = frame_max - nSlices;
	id_short = repeat_N_last_frames(id_short, N_ending_repeat);

	// Expand the canvase of both images by 2 pixels, so that combining them will naturally generate a 2 pixel line between images
	selectImage(id_long);
	new_width = getWidth() + 2;
	new_height = getHeight() + 2;
	run("Canvas Size...", "width="+new_width+" height="+new_height+" position=Center zero");

	selectImage(id_short);
	new_width = getWidth() + 2;
	new_height = getHeight() + 2;
	run("Canvas Size...", "width="+new_width+" height="+new_height+" position=Center zero");

	// Combine the two stacks so that the shorter duration stack is on the left
	// In addition, concatenate the two image titles to use as an output prefix
	if ( duration_short <= duration_long ) {
		run("Combine...", "stack1=["+title_short+"] stack2=["+title_long+"]");
		id_combined = getImageID();
		outputPrefix = title_short + "-" + title_long;
	}
	else {
		run("Combine...", "stack1=["+title_long+"] stack2=["+title_short+"]");
		id_combined = getImageID();
		outputPrefix = title_long + "-" + title_short;
	}

	selectImage(id_combined);
	duration_padded = zeroPadding(duration, frame_max);
	output_file_name = outputFolder + "Duration-" + duration_padded + "-" + outputPrefix + ".tif";
	saveAs("Tiff", output_file_name);

	run("Close All");
}

function get_t_from_slice_label(id) {
	selectImage(id);
	Stack.setFrame(1);
	label = getInfo("slice.label");
	
	label_parts = split(label, "_");
	temp = split(label_parts[0], "t");
	t = parseInt(temp[0]);
	
	return t;	
}

function label_spot_series(id, pre_division_frame) {
	selectImage(id); title = getTitle();
	
	setForegroundColor(255, 255, 255);
	setFont("Arial", 18, "antiliased");

//	top_label = "cell division " + title;
//	if ( lengthOf(title) == 2 ) {
//		// 1-digit cell division id (1-9) to center
//		run("Time Stamper", "starting=0 interval=0 x=35 y=23 font=18 decimal=0 anti-aliased or=["+top_label+"]");
//	}
//	if ( lengthOf(title) == 3 ) {
//		// 2-digit cell division id (10-99) to center
//		run("Time Stamper", "starting=0 interval=0 x=30 y=23 font=18 decimal=0 anti-aliased or=["+top_label+"]");
//	}
//	if ( ( lengthOf(title) > 3 ) || ( lengthOf(title) < 2 ) ){
//		run("Time Stamper", "starting=0 interval=0 x=3 y=23 font=18 decimal=0 anti-aliased or=["+top_label+"]");
//		print("WARNING: unexpected title length.");
//	}

	// Note: when font size is 24 and y position <= 28 points, the anti-aliased is automatically turned off
	// Probably some bug about anti-aliased on handling the distance to edge
	t_start = -1 * 5 * pre_division_frame;
	run("Time Stamper", "starting="+t_start+" interval=5 x=28 y=198 font=18 decimal=0 anti-aliased or=min");
	return id;
}

function repeat_N_last_frames(id, N) {
	// Append N frames of the image in the last frame to simulate a freezing effect at the beginning of series
	
	selectImage(id); Stack.setFrame(nSlices); run("Select All"); run("Copy"); run("Select None");

	for (i = 0; i < N; i++) {
		selectImage(id); Stack.setFrame(nSlices); run("Add Slice");
		selectImage(id); Stack.setFrame(nSlices); run("Select All"); run("Paste"); run("Select None");
	}

	return id;
}

function repeat_N_first_frames(id, N) {
	// Append N frames of the image in the first frame to simulate a freezing effect at the beginning of series

	// Record the title of id_short to use for concatenated image
	selectImage(id); title_original = getTitle();

	// Make the size of image id1 to be N frames
	selectImage(id); Stack.setFrame(1); run("Duplicate...", "use"); id1 = getImageID();
	for (i = 0; i < N-1; i++) {
		selectImage(id1); run("Add Slice");
	}
	selectImage(id1); Stack.setDimensions(1, 1, N);

	// Paste the first frame into all other frames
	selectImage(id1); Stack.setFrame(1); run("Select All"); run("Copy"); run("Select None");
	for (i = 2; i < N+1; i++) {
		selectImage(id1); Stack.setFrame(i); run("Select All"); run("Paste"); run("Select None");
	}
	selectImage(id1); rename("N_frame1");

	// Concatenate the repeated N first frames to the original
	run("Concatenate...", "  title=["+title_original+"] open image1=N_frame1 image2=["+title_original+"] image3=[-- None --]"); id_new = getImageID();

	return id_new;
}

function matching_first_n_frames(id_short, id_long, N) {
	// Append the first N frames of the long series (id_long) to the beginning of the short series (id_short)

	// Record the title of id_short to use for concatenated image
	selectImage(id_short); title_short = getTitle();
	
	// Duplicate the first N frames
	selectImage(id_long); run("Duplicate...", "duplicate range=1-"+N+" use"); rename("first_N_frames");
	
	// Concatenate the first N frames of id_long and the entire id_short
	run("Concatenate...", "  title=["+title_short+"] open image1=first_N_frames image2="+title_short+" image3=[-- None --]"); id_short_new = getImageID();

	return id_short_new;
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

function zeroPadding(N, N_max) {
	if ( N_max < 10 ) {
		temp = toString(N); return temp;
	}
	if ( N_max < 100 ) {
		temp = zeroPadding2(N); return temp;
	}
	if ( N_max < 1000 ) {
		temp = zeroPadding3(N); return temp;
	}
	if ( N_max < 10000 ) {
		temp = zeroPadding4(N); return temp;
	}
	else {
		print( "Warning! Maximum >= 10000! Change zeroPadding to account for that.");
		temp = toString(N);
		return temp;
	}
}

function zeroPadding4(t) {
	// pad t to 4 digits when t <1000
	if ( t < 10 ) {
		tPadded = "000" + t; return tPadded;
	}
	if ( t < 100 ) {
		tPadded = "00" + t; return tPadded;
	}
	if ( t < 1000 ) {
		tPadded = "0" + t; return tPadded;
	}
	if ( t < 10000 ) {
		temp = toString(t); return temp;
	}
	else {
		print( "Warning! Maximum >= 10000! Change zeroPadding to account for that.");
		temp = toString(t); return temp;
	}
}

function zeroPadding3(t) {
	// pad t to 4 digits when t <1000
	if ( t < 10 ) {
		tPadded = "00" + t; return tPadded;
	}
	if ( t < 100 ) {
		tPadded = "0" + t; return tPadded;
	}
	if ( t < 1000 ) {
		temp = toString(t); return temp;
	}
	else {
		print( "Warning! Maximum >= 1000! Change zeroPadding to account for that.");
		temp = toString(t); return temp;
	}
}

function zeroPadding2(t) {
	// pad t to 4 digits when t <1000
	if ( t < 10 ) {
		tPadded = "0" + t; return tPadded;
	}
	if ( t < 100 ) {
		temp = toString(t); return temp;
	}
	else {
		print( "Warning! Maximum >= 100! Change zeroPadding to account for that.");
		temp = toString(t); return temp;
	}
}