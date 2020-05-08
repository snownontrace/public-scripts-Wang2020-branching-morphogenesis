import sys, os
from java.lang import System
from java.awt import Color, Font
from java.io import File
#from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger
from ij.io import FileSaver
from ij.plugin import FolderOpener
from ij.plugin.filter import AVI_Writer
from ij.process import ImageConverter
from ij.gui import Arrow
from ij import ImagePlus, IJ
#from loci.plugins.util import BFVirtualStack
#from loci.formats import ChannelSeparator
from packageSW import slices, stacks

# Record the starting time to calculate total time cost
startTime = System.currentTimeMillis()
time_stamp = '%06d'%(startTime%1000000)

# Clean up workspace
IJ.run("Close All");
IJ.run("Collect Garbage"); # Release occupied memory
print("Used memory at start: " + IJ.freeMemory())

#-------------------
# Facility functions
#-------------------

def save_track_info(xml_filename, input_folder, output_folder, output_filename, TEST_RUN=False):
	
	# Read in the tracking information from the TrackMate xml file
	xmlFile = File(input_folder + xml_filename)
	reader = TmXmlReader(xmlFile)
	if not reader.isReadingOk():
	    sys.exit(reader.getErrorMessage())
	
	model = reader.getModel() # Get a full model # model is a fiji.plugin.trackmate.Model
	model.setLogger(Logger.IJ_LOGGER) # Set logger for the model
	fm = model.getFeatureModel() # The feature model, that stores edge and track features.

	# Open a file handle to save the information of the tracks
	f_out = open(output_folder + output_filename, 'w')
	f_out.write('cell_division_id' + ',' + 'track_id' + ',' + 'spot_id' + ',' + 'x'  + ',' + 'y' + ',' + 'z' + ',' + 't' + '\n')

	#--------------------------------------------------------------------
	# The following loop goes through all the tracks loaded from the XML
	#--------------------------------------------------------------------
	
	test_count = 0
	for track_id in model.getTrackModel().trackIDs(True):
	
	#	# This trick is useful if some track_id needs to be come back at later
	#	if not track_id == 152:
	#		continue
		
		if TEST_RUN == True and test_count > 1:
			break
		test_count = test_count + 1
	
	
		# Fetch the track feature from the feature model.
		nSplit = fm.getTrackFeature(track_id, 'NUMBER_SPLITS')
		model.getLogger().log('')
		model.getLogger().log('Track ' + str(track_id) + ': number of splitting events = ' + str(nSplit))
	
		if nSplit > 0:
			model.getLogger().log('Branched tracks are skipped for now. They will be dealt with in the future.')
		else:
			track = model.getTrackModel().trackSpots(track_id)
			track_name = model.getTrackModel().name(track_id)
	
			for spot in track:
				spotID = spot.ID()
				# Fetch spot features directly from spot.
				x = spot.getFeature('POSITION_X')
				y = spot.getFeature('POSITION_Y')
				z = spot.getFeature('POSITION_Z')
				f = int(spot.getFeature('FRAME')+1)

				f_out.write(str(track_name) + ',' + str(track_id) + ',' + str(spotID) + ',' + str(x)  + ',' + str(y) + ',' + str(z) + ',' + str(f) + '\n')
	f_out.close()
	return os.path.isfile(output_folder + output_filename)

#----------------
# Setup variables
#----------------

# Put here the path to the tif and xml TrackMate file you want to load
#input_folder = '/Volumes/ShaoheGtech/SMG-live-imaging-2017-2020/190227-mTmGHisG-2photon-definedThickness/'
#input_folder = '/Users/wangs20/OneDrive/Data/K14R-het-HisG-showcase/'
input_folder = '/Users/wangs20/OneDrive/Data/mTmG-HisG-selected/'
#input_folder = '/Volumes/ShaoheGtech/SMG-live-imaging-2017-2020/180218-mTmGHisG-2photon-selected/'
output_folder = input_folder

outputPrefix = '180218-mTmGHisG-ROI1'
output_filename = outputPrefix + '-track-info.csv'

xml_filename = '180218-mTmGHisG-ROI1-cell-division.xml'

TEST_RUN = False
#TEST_RUN = True # uncomment for testing run (2 tracks)

# Run the function to loop through all tracks and save the info in a tidy long form for downstream plotting
save_track_info(xml_filename, input_folder, output_folder, output_filename, TEST_RUN)


# Clean up workspace after running
IJ.run("Close All");
IJ.run("Collect Garbage"); # Release occupied memory
print("Used memory at finish: " + IJ.freeMemory())

# Print out time cost
endTime = System.currentTimeMillis()
timeLapse = (endTime - startTime)/1000
print("Time used: " + str(timeLapse) + " s")
