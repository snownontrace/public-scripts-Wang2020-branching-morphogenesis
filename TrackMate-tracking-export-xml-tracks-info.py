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
	f_out.write('track_name' + ',' + 'track_id' + ',' + 'spot_id' + ',' + 'x'  + ',' + 'y' + ',' + 'z' + ',' + 't' + '\n')

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

# Epxand the image canvas by L pixels in all directions
def expandImageCanvas(impTemp, L):
	ipOld = impTemp.getProcessor()
	wOld = ipOld.getWidth()
	hOld = ipOld.getHeight()
	wNew = wOld + 2*L
	hNew = hOld + 2*L
	ipNew = ipOld.createProcessor(wNew, hNew)
	ipNew.setColor(0) # 0 = black color
	ipNew.insert(ipOld, L, L)
	impTemp.setProcessor(ipNew)
	return impTemp

# Resize the image by r fold
def resizeImage(impTemp, r):
	ipOld = impTemp.getProcessor()
	wOld = ipOld.getWidth()
	ipOld.setInterpolationMethod(1) # 0=NONE 1=BILINEAR 2=BICUBIC
	ipNew = ipOld.resize(int(r*wOld))
	impTemp.setProcessor(ipNew)
	return impTemp

# Zoom out the image depending on distance from coverslip while keeping the canvas size
def zoomImageByZ(impTemp, z, zN, minZoom, Z1_CLOSE_TO_COVERSLIP):
	from java.awt import Color
	ipOld = impTemp.getProcessor()
	wOld = ipOld.getWidth()
	hOld = ipOld.getHeight()
	if Z1_CLOSE_TO_COVERSLIP == True:
		wNew = int(wOld * (minZoom * (zN - z ) / (zN - 1) + minZoom)) # use when z = 1 is closest to coverslip
	else:
		wNew = int(wOld * (minZoom * (z - 1 ) / (zN - 1) + minZoom)) # use when z = 1 is farthest to coverslip
	ipNew = ipOld.resize(wNew)
	hNew = ipNew.getHeight()
	xOffset = int((wOld - wNew)/2)
	yOffset = int((hOld - hNew)/2)
	ipTemp = ipOld.createProcessor(wOld, hOld)
	ipTemp.setColor(Color.GRAY)
	ipTemp.fill()
	ipTemp.setColor(Color.DARK_GRAY)
	ipTemp.setLineWidth(2)
	ipTemp.drawLine(0, 0, wOld, hOld)
	ipTemp.drawLine(0, hOld, wOld, 0)
	ipTemp.insert(ipNew, xOffset, yOffset)
	impTemp.setProcessor(ipTemp)
	return impTemp

def snapshot(imp, c, z, f, x, y, L):
	'''Take a L x L snapshot centered at (x,y) at channel c, slice z and frame f

	Parameters:
		imp: an ImagePlus object for processing
		c, z, f: specificed channel, slice (z-dimension) and frame coordinate
		x, y: targeted center position to take the snapshot
		L: desired edge lengths of the snapshot in pixels

	Returns:
		cropped: an ImagePlus object of the snapshot image
	'''
	# Import inside function to limit scope
	from ij import ImagePlus
	
	# Get the dimensions of the images
	cN = imp.getNChannels()
	zN = imp.getNSlices()
#	fN = imp.getNFrames()

	# Convert specified position (c,z,f) to index assuming hyperstack order is czt (default)
	sliceIndex = int(cN * zN * (f-1) + cN * (z-1) + c)
	imp.setSlice(sliceIndex)
	ipTemp = imp.getProcessor()
	impTemp = ImagePlus('temp', ipTemp)

	# Expand the image by half of L to make sure final duplicate is the same size
	# when requested (x,y) could be within L pixels of the edge
	wOld = ipTemp.getWidth()
	hOld = ipTemp.getHeight()
	wNew = wOld + int(L)
	hNew = hOld + int(L)
	ipNew = ipTemp.createProcessor(wNew, hNew)
	ipNew.setColor(0) # 0 = black color
	ipNew.insert(ipTemp, int(L/2), int(L/2))
	imgNew = ImagePlus('new', ipNew)
	
	# Use the specified center coordinate x, y and the target side length to create ROI
	imgNew.setRoi(int(x), int(y), int(L), int(L))
#	cropped = ImagePlus('cropped', ipNew.crop())
	cropped = imgNew.crop()
	
	impTemp.close()
	imgNew.close()
	
	return cropped


#----------------
# Setup variables
#----------------

# Put here the path to the tif and xml TrackMate file you want to load
input_folder = '/Volumes/ShaoheGtech/SMG-live-imaging-2019-2021/210124-K14RhisG-2p/20210124-K14RhisG-2p-collagenase-denoised-FIJI-tifs/'
output_folder = input_folder

#xml_filename = '20210124-K14RhisG-2p-collagenase-SMG1-1-8bit.xml'
#xml_filename = '20210124-K14RhisG-2p-collagenase-SMG2-combined-8bit-wrong-pixel-size-0p31.xml'
xml_filename = '20210124-K14RhisG-2p-collagenase-SMG3-combined-8bit.xml'

outputPrefix = '20210124-K14RhisG-2p-collagenase-SMG3'
output_filename = outputPrefix + '-track-info.csv'

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
