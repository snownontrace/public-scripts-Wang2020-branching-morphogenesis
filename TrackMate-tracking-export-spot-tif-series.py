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

def save_snap_shot_seq_simple(imp, xml_filename, input_folder, output_folder,
							  ZOOM_BY_Z_DEPTH=False, Z1_CLOSE_TO_COVERSLIP=False, DRAW_DOT=True, TEST_RUN=False,
							  trackIDs=None, z_number_to_project=3):

	# Read in the tracking information from the TrackMate xml file
	xmlFile = File(input_folder + xml_filename)
	reader = TmXmlReader(xmlFile)
	if not reader.isReadingOk():
	    sys.exit(reader.getErrorMessage())

	model = reader.getModel() # Get a full model # model is a fiji.plugin.trackmate.Model
	model.setLogger(Logger.IJ_LOGGER) # Set logger for the model
	fm = model.getFeatureModel() # The feature model, that stores edge and track features.


	# Get the pixel calibration data
	calibr = imp.getCalibration()
	w = calibr.pixelWidth
	d = calibr.pixelDepth
	print("pixel width and depth: ", w, d)

	# Get the dimensions of the images
	cN = imp.getNChannels()
	zN = imp.getNSlices()
	tN = imp.getNFrames()
	print("Channel number, z slice number, frame number:", cN, zN, tN)

	# Calculate the half z depth for looping fromt he desired z_number_to_project variable
	z_half = int( ( z_number_to_project - 1 ) / 2 )

	#--------------------------------------------------------------------
	# The following loop goes through all the tracks loaded from the XML
	#--------------------------------------------------------------------

	test_count = 0
	if trackIDs is None:
		trackIDs = model.getTrackModel().trackIDs(True)
	for track_id in trackIDs:

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

			# Create a tif folder to store spot snapshots
			tif_folder = output_folder + 'trackName-' + str(track_name) + '-trackID-' + '%04d'%(track_id) + '/'
			if not os.path.exists(tif_folder):
				os.makedirs(tif_folder)

			for spot in track:
				spotID = spot.ID()
				# Fetch spot features directly from spot.
				x0 = spot.getFeature('POSITION_X')
				x = int(x0/w) # convert to pixel
				y0 = spot.getFeature('POSITION_Y')
				y = int(y0/w) # convert to pixel
				z0 = spot.getFeature('POSITION_Z')
				z = int(z0/d+1) # convert to pixel
				f = int(spot.getFeature('FRAME')+1)

				for c in range(cN):
					current_c = c + 1

					for current_z in range( z - z_half , z + z_half + 1 ):

						# Convert specified position (c,z,f) to index assuming hyperstack order is czt (default)
						sliceIndex = int(cN * zN * (f-1) + cN * (current_z-1) + current_c)
						imp.setSlice(sliceIndex)
#						ipTemp = imp.getProcessor()
#						impTemp = ImagePlus('temp', ipTemp)
						impTemp = imp.crop('slice')


						if DRAW_DOT == True:
							# Draw a dot at the center of image
							ip = impTemp.getProcessor()
#							ip.setColor(Color.BLUE)
#							ip.setColor(Color.CYAN)
							ip.setColor(Color.WHITE)
							ip.setLineWidth(4)
							ip.drawDot(x, y)
							impTemp.setProcessor(ip)

						if ZOOM_BY_Z_DEPTH == True:
							minZoom = 0.5 # this parameter specified the minimal zoom when shrinking images
							# First, expand the snapshot by 2 times to make them less pixelated, also prepare for the zoom-by-z
							impTemp = slices.resizeImage(impTemp, 1/minZoom)
							# Second, zoom out the image depending on distance from coverslip, but keep the canvas size
							impTemp = slices.zoomImageByZ( impTemp, z, zN, minZoom, Z1_CLOSE_TO_COVERSLIP )

						if ANNOTATE_Z == True:
							# annotate the z position at the bottom center

							ip = impTemp.getProcessor()
#							ip.setJustification(1) # 0, 1, 2 represents left, center and right justification.
							ip.setJustification(2) # 0, 1, 2 represents left, center and right justification.
							arial_font = Font("Arial", 0, 18) # 0 = PLAIN, 18 is font size
							ip.setFont(arial_font)
							ip.setAntialiasedText(True) # It appears that only on RGB the anti-aliased text works
							ip.setColor(Color.WHITE)
#							annotation_x_pos = int(ip.getWidth()/2)
							annotation_x_pos = int(ip.getWidth() - 28)
							annotation_y_pos = int(ip.getHeight() - 2)
#							print(annotation_x_pos, annotation_y_pos)
							if Z1_CLOSE_TO_COVERSLIP == True:
								z_relative = 2 * current_z
							else:
								z_relative = 2 * (zN - current_z + 1)
							ip.drawString( str(z_relative)+" "+u"\u00B5"+"m", annotation_x_pos, annotation_y_pos )

							impTemp.setProcessor(ip)

						# Make a meaningful file name and save the file
						outFileName = tif_folder + 't' + str(f) + '_z' + str(current_z) + '_c' + str(current_c) + "_" + str(spotID) + ".tif"
						FileSaver(impTemp).saveAsTiff(outFileName)


def save_snap_shot_seq(imp, xml_filename, input_folder, output_folder, ZOOM_BY_Z_DEPTH=False, Z1_CLOSE_TO_COVERSLIP=False, DRAW_DOT=False, TEST_RUN=False, z_number_to_project=5, L=100):

	# Read in the tracking information from the TrackMate xml file
	xmlFile = File(input_folder + xml_filename)
	reader = TmXmlReader(xmlFile)
	if not reader.isReadingOk():
	    sys.exit(reader.getErrorMessage())

	model = reader.getModel() # Get a full model # model is a fiji.plugin.trackmate.Model
	model.setLogger(Logger.IJ_LOGGER) # Set logger for the model
	fm = model.getFeatureModel() # The feature model, that stores edge and track features.


	# Get the pixel calibration data
	calibr = imp.getCalibration()
	w = calibr.pixelWidth
	d = calibr.pixelDepth
	print("pixel width and depth: ", w, d)

	# Get the dimensions of the images
	cN = imp.getNChannels()
	zN = imp.getNSlices()
	tN = imp.getNFrames()
	print("Channel number, z slice number, frame number:", cN, zN, tN)

	# Calculate the half z depth for looping fromt he desired z_number_to_project variable
	z_half = int( ( z_number_to_project - 1 ) / 2 )

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

			# Create a tif folder to store spot snapshots
			tif_folder = output_folder + 'trackName-' + str(track_name) + '-trackID-' + '%04d'%(track_id) + '/'
			if not os.path.exists(tif_folder):
				os.makedirs(tif_folder)

			for spot in track:
				spotID = spot.ID()
				# Fetch spot features directly from spot.
				x0 = spot.getFeature('POSITION_X')
				x = int(x0/w) # convert to pixel
				y0 = spot.getFeature('POSITION_Y')
				y = int(y0/w) # convert to pixel
				z0 = spot.getFeature('POSITION_Z')
				z = int(z0/d+1) # convert to pixel
				f = int(spot.getFeature('FRAME')+1)

				for c in range(cN):
					current_c = c + 1

					for current_z in range( z - z_half , z + z_half + 1 ):

	#					model.getLogger().log("current c, z, f: " + str(current_c) + ", " + str(current_z) + ", " + str(f))
						# Take a L x L snapshot centered at (x,y) at channel c, slice z and frame f.
						impTemp = stacks.snapshot( imp, current_c, current_z, f, x, y, L )

						if DRAW_DOT == True:
							# Draw a dot at the center of image
							ip = impTemp.getProcessor()
							#ip.setColor(0)
#							ip.setColor(Color.BLUE)
#							ip.setColor(Color.CYAN)
							ip.setColor(Color.WHITE)
							ip.setLineWidth(4)
							ip.drawDot(int(L/2),int(L/2))
							impTemp.setProcessor(ip)

						if ZOOM_BY_Z_DEPTH == True:
							minZoom = 0.5 # this parameter specified the minimal zoom when shrinking images
							# First, expand the snapshot by 2 times to make them less pixelated, also prepare for the zoom-by-z
							impTemp = slices.resizeImage(impTemp, 1/minZoom)
							# Second, zoom out the image depending on distance from coverslip, but keep the canvas size
							impTemp = slices.zoomImageByZ( impTemp, z, zN, minZoom, Z1_CLOSE_TO_COVERSLIP )

						if ANNOTATE_Z == True:
							# annotate the z position at the bottom center

							ip = impTemp.getProcessor()
#							ip.setJustification(1) # 0, 1, 2 represents left, center and right justification.
							ip.setJustification(2) # 0, 1, 2 represents left, center and right justification.
							arial_font = Font("Arial", 0, 18) # 0 = PLAIN, 18 is font size
							ip.setFont(arial_font)
							ip.setAntialiasedText(True) # It appears that only on RGB the anti-aliased text works
							ip.setColor(Color.WHITE)
#							annotation_x_pos = int(ip.getWidth()/2)
							annotation_x_pos = int(ip.getWidth() - 28)
							annotation_y_pos = int(ip.getHeight() - 2)
#							print(annotation_x_pos, annotation_y_pos)
							if Z1_CLOSE_TO_COVERSLIP == True:
								z_relative = 2 * current_z
							else:
								z_relative = 2 * (zN - current_z + 1)
							ip.drawString( str(z_relative)+" "+u"\u00B5"+"m", annotation_x_pos, annotation_y_pos )

							impTemp.setProcessor(ip)

						# Make a meaningful file name and save the file
						outFileName = tif_folder + 't' + str(f) + '_z' + str(current_z) + '_c' + str(current_c) + "_" + str(spotID) + ".tif"
						FileSaver(impTemp).saveAsTiff(outFileName)

#----------------
# Setup variables
#----------------

# Put here the path to the tif and xml TrackMate file you want to load
#input_folder = '/Volumes/ShaoheGtech/SMG-live-imaging-2017-2020/190227-mTmGHisG-2photon-definedThickness/'
#input_folder = '/Users/wangs20/OneDrive/Data/K14R-het-HisG-showcase/'
input_folder = '/Users/wangs20/OneDrive/Data/mTmG-HisG-selected/'
#input_folder = '/Volumes/ShaoheGtech/SMG-live-imaging-2017-2020/180218-mTmGHisG-2photon-selected/'
outputPrefix = '180218-mTmGHisG-ROI1'

#filenamePrefix = '180218-mTmGHisG-ROI1'
# xml_filename = filenamePrefix + '.xml'
# tif_filename = filenamePrefix + '.tif'
xml_filename = '180218-mTmGHisG-ROI1-cell-division.xml'
tif_filename = '180218-mTmGHisG-ROI1-denoised-BCratio-all-merged.tif'

z_number_to_project = 3 # however many z slices to do a local max intensity projection
L = 300 # the side length of the snapshot in pixels

ZOOM_BY_Z_DEPTH = False
#ZOOM_BY_Z_DEPTH = True # use if zoom by z is not helpful

Z1_CLOSE_TO_COVERSLIP = False
#Z1_CLOSE_TO_COVERSLIP = True # use if z1 is closest to the coverslip

DRAW_DOT = False
DRAW_DOT = True # use if drawing a dot at the center of tracking

ANNOTATE_Z = False
#ANNOTATE_Z = True # use if drawing a string to annotate the z position

TEST_RUN = False
#TEST_RUN = True # use for testing run (2 tracks)

# Reading in the image file for taking snapshots
tifFile = input_folder + tif_filename
imp = ImagePlus(tifFile)

#----------------------------------------------------------
# For running all ZOOM_BY_Z_DEPTH and DRAW_DOT combinations
#----------------------------------------------------------

#boolList = [False, True]
#for ZOOM_BY_Z_DEPTH in boolList:
#	for DRAW_DOT in boolList:
#		# Running the heavy-lifting function to save all snapshot series
#		output_folder = input_folder + outputPrefix + '-zZoom_' + str(ZOOM_BY_Z_DEPTH) + '-drawDot_' + str(DRAW_DOT) + '-' + time_stamp + '/'
#		if not os.path.exists(output_folder):
#			os.makedirs(output_folder)
#		save_snap_shot_seq(imp, xml_filename, input_folder, output_folder, ZOOM_BY_Z_DEPTH, Z1_CLOSE_TO_COVERSLIP, DRAW_DOT, TEST_RUN, z_number_to_project, L)

#----------------------------------------------------------
# For running both ZOOM_BY_Z_DEPTH conditions
#----------------------------------------------------------

boolList = [False, True]
for ZOOM_BY_Z_DEPTH in boolList:
	output_folder = input_folder + outputPrefix + '-zZoom_' + str(ZOOM_BY_Z_DEPTH) + '-drawDot_' + str(DRAW_DOT) + '-' + time_stamp + '/'
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	save_snap_shot_seq(imp, xml_filename, input_folder, output_folder, ZOOM_BY_Z_DEPTH, Z1_CLOSE_TO_COVERSLIP, DRAW_DOT, TEST_RUN, z_number_to_project, L)
	# # Specify the track IDs to save
	# trackIDs = [68, 69, 110, 121]
	# save_snap_shot_seq_simple(imp, xml_filename, input_folder, output_folder,
	# 						  ZOOM_BY_Z_DEPTH, Z1_CLOSE_TO_COVERSLIP, DRAW_DOT, TEST_RUN,
	# 						  trackIDs, z_number_to_project)

#-----------------------------------
# For running just one configuration
#-----------------------------------
#
# Running the heavy-lifting function to save all snapshot series
#output_folder = input_folder + outputPrefix + '-zZoom_' + str(ZOOM_BY_Z_DEPTH) + '-drawDot_' + str(DRAW_DOT) + '-' + time_stamp + '/'
#if not os.path.exists(output_folder):
#	os.makedirs(output_folder)
#save_snap_shot_seq(imp, xml_filename, input_folder, output_folder, ZOOM_BY_Z_DEPTH, Z1_CLOSE_TO_COVERSLIP, DRAW_DOT, TEST_RUN, z_number_to_project, L)

# Clean up workspace after running
imp.close()
IJ.run("Close All");
IJ.run("Collect Garbage"); # Release occupied memory
print("Used memory at finish: " + IJ.freeMemory())

# Print out time cost
endTime = System.currentTimeMillis()
timeLapse = (endTime - startTime)/1000
print("Time used: " + str(timeLapse) + " s")
