import glob
import numpy as np
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
# from statsmodels.stats.multicomp import MultiComparison
from statsmodels.stats.libqsturng import psturng
from scipy.interpolate import UnivariateSpline, interp1d

def get_segments_mean(a, n):
    '''
    Calculate mean values of every n items in a list (not walking average)
    
    Input Parameters:
    -----------------
        a: a list or array of values
        n: length of segments; has to be divisible by len(a)
    
    Returns:
    --------
        res: a list of mean values of every n items in the given list
        
    '''
    assert len(a)%n == 0

    res = []
    for i in range(int(len(a)/n)):
        a_temp = a[i*n : (i+1)*n]
        temp = np.mean(a_temp)
        res.append(temp)
        
    return res

def header(f, N=10):
    '''Print out the first N lines of a file
    '''
    with open(f) as myfile:
        head = [next(myfile).strip() for x in range(N)]
    return '\n'.join(head)

def tukeyTest(data, groups, alpha=0.05):
    '''Perform pairwise Tukey test for data by groups
    '''
    # pairwise comparisons using Tukey's test, calculating p-values
    res = pairwise_tukeyhsd(data, groups, alpha)
    print('Summary of test:\n', res)
    # print(dir(results))# prints out all attributes of an object
    pVal = psturng(np.abs(res.meandiffs / res.std_pairs), len(res.groupsunique), res.df_total)
    print('p values of all pair-wise tests:\n', pVal)

    return res

def getInteriorAreaDF(codingFile, interiorAreaFile):
    '''Read in data from corresponding filename coding and
    ineterior area files, merge the data by scrambled filenames,
    and returns the merged data frame.
    '''
    dfCode = pd.read_csv(codingFile, header=0, sep='\t')
    dfCode.columns = ['file_name', 'scrambled_file_name']
    dfInteriorArea0 = pd.read_csv(interiorAreaFile, header=0, sep='\t')
    dfInteriorArea0.columns = ['scrambled_file_name', 'interior_area']
    dfInteriorArea = dfCode.merge(dfInteriorArea0, on = 'scrambled_file_name')
    return dfInteriorArea

def getTotalAreaDF(codingFile, totalAreaFile):
    '''Read in data from corresponding filename coding and
    total area files, merge the data by scrambled filenames,
    and returns the merged data frame.
    '''
    dfCode = pd.read_csv(codingFile, header=0, sep='\t')
    dfCode.columns = ['file_name', 'scrambled_file_name']
    dfTotalArea0 = pd.read_csv(totalAreaFile, header=0, sep='\t')
    dfTotalArea0.columns = ['scrambled_file_name', 'interior_area']
    dfTotalArea = dfCode.merge(dfTotalArea0, on = 'scrambled_file_name')
    if len(dfTotalArea)==0:
        # In case the total area was extracted from files with regular file names
        dfTotalArea0.columns = ['file_name', 'interior_area']
        dfTotalArea = dfCode.merge(dfTotalArea0, on = 'file_name')
    return dfTotalArea

def getAreaDF(codingFile, interiorAreaFile, totalAreaFile, totalAreaColName=None):
    '''Read in data from corresponding filename coding, interior and
    total area text files, merge the data by scrambled filenames,
    and returns the merged data frame.
    '''
    if totalAreaColName is None:
        # Specify whether the total area was obtained on files with
        # original file names or scrambled file names
        totalAreaColName = 'scrambled_file_name'
    
    dfCode = pd.read_csv(codingFile, header=0, sep='\t')
    dfCode.columns = ['file_name', 'scrambled_file_name']
    
    dfInteriorArea0 = pd.read_csv(interiorAreaFile, header=0, sep='\t')
    dfInteriorArea0.columns = ['scrambled_file_name', 'interior_area']
    dfInteriorArea = dfCode.merge(dfInteriorArea0, on = 'scrambled_file_name')
    
    dfTotalArea0 = pd.read_csv(totalAreaFile, header=0, sep='\t')
    dfTotalArea0.columns = [totalAreaColName, 'total_area']
    dfArea = dfInteriorArea.merge(dfTotalArea0, on = totalAreaColName)
    
    dfArea['protruded_area'] = dfArea['total_area'] - dfArea['interior_area']
    dfArea['ratio_protruded_area'] = dfArea['protruded_area'] / dfArea['total_area']
    
    return dfArea

def getAreaDFbyPrefix(datasetPrefix, datasetFolder=None, totalAreaColName=None):
    '''A convenience function of getAreaDF.
    
        Use pattern match to identify the corresponding pair
    of filename coding and counting files, then call getAreaDF
    to obtain the merged data frame.
    '''
    if datasetFolder is None:
        # This is the default folder storing most bud count files
        datasetFolder = '../data/DLD-1-spheroids-protruded-area-KM/'
    if totalAreaColName is None:
        # Specify whether the total area was obtained on files with
        # original file names or scrambled file names
        totalAreaColName = 'scrambled_file_name'
        
    # Identify the corresponding pair of filename coding and counting files
    codingFiles = glob.glob( datasetFolder + datasetPrefix + '*fileNameRecord.txt')
    interiorAreaFiles = glob.glob( datasetFolder + datasetPrefix + '*interior-area.txt')
    totalAreaFiles = glob.glob( datasetFolder + datasetPrefix + '*total-area.txt')

    # There should be only one coding file for each data set
    codingFile = codingFiles[0]
    
    # There should be only one total area file for each data set
    totalAreaFile = totalAreaFiles[0]

    # There could be multiple interior files for each data set,
    # which is because sometimes Kaz counts for several times
    # to check for consistenty. Take the last one.
    interiorAreaFiles.sort()
    interiorAreaFile = interiorAreaFiles[-1]

    df = getAreaDF(codingFile, interiorAreaFile, totalAreaFile, totalAreaColName)
    
    return df

def getCountDF(codingFile, countFile):
    '''Read in data from corresponding filename coding and
    counting files, merge the data by scrambled filenames,
    and returns the merged data frame.
    '''
    dfCode = pd.read_csv(codingFile, header=0, sep='\t')
    dfCode.columns = ['file_name', 'scrambled_file_name']
    dfCount0 = pd.read_csv(countFile, header=0, sep='\t')
    dfCount0.columns = ['scrambled_file_name', 'counts']
    dfCount = dfCode.merge(dfCount0, on = 'scrambled_file_name')
    return dfCount

def getCountDFbyPrefix(datasetPrefix, datasetFolder=None):
    '''A convenience function of getCountDF.
        Use pattern match to identify the corresponding pair
    of filename coding and counting files, then call getCountDF
    to obtain the merged data frame.
    '''
    if datasetFolder is None:
        # This is the default folder storing most bud count files
        datasetFolder = '../data/DLD-1-spheroids-bud-count-KM/'
    # Identify the corresponding pair of filename coding and counting files
    codingFiles = glob.glob( datasetFolder + datasetPrefix + '*fileNameRecord.txt')
    countFiles = glob.glob( datasetFolder + datasetPrefix + '*budCount.txt')

    # There should be only one coding file for each data set
    codingFile = codingFiles[0]

    # There could be multiple count files for each data set,
    # which is because sometimes Kaz counts for several times
    # to check for counting consistenty. Take the last one.
    countFiles.sort()
    countFile = countFiles[-1]

    # print(header(codingFile))
    # print(header(countFile))

    df = getCountDF(codingFile, countFile)
    
    return df

# ***Curvature calculation functions***

def curvature_splines(x, y):
    """Calculate the signed curvature of a 2D curve at each point
    using interpolating splines.
    
    Parameters
    ----------
        x,y: numpy.array(dtype=float) shape (n_points, )
    
    Returns
    -------
        curvature: numpy.array shape (n_points, )
    """
    t = np.arange(x.shape[0])
#     std = error * np.ones_like(x)

    fx = UnivariateSpline(t, x, k=3)
    fy = UnivariateSpline(t, y, k=3)

    dx = fx.derivative(1)(t)
    d2x = fx.derivative(2)(t)
    dy = fy.derivative(1)(t)
    d2y = fy.derivative(2)(t)
    curvature = (dy*d2x - dx*d2y) / np.power(dx**2 + dy**2, 1.5)
    return curvature

def centerVector(x):
    """Center a vector by the middle point of two extreme value
    Parameter: 1-d numpy array, or list, or pandas Series
    Returns: the same data type and shape as input
    """
    midX = np.mean([np.min(x), np.max(x)])
    return x-midX

def isClockwise(x, y):
    """Determines whether the direction following the first quarter
    of (x,y) points turns clockwise or not using cross product
    Parameter: two 1-d vectors representing x and y coordinates of points
    Returns: Boolean value of whether it turns clockwise or not
    """
    x = centerVector(x)
    y = centerVector(y)
    quarterIndex = int(len(x)/4)
    v1 = [x[0], y[0]]
    v2 = [x[quarterIndex], y[quarterIndex]]
    if np.cross(v1, v2)<0:
        return True;
    else:
        return False;

def getCurvatureDF(xyFilename, N=500):
    '''Read a text file storing a series of (x,y) coordinates of a closed curve,
    calculate the local curvature at N points and return the data frame containing
    3 columns: x, y and the curvature at (x,y)
    '''
    df0 = pd.read_csv(xyFilename, header=None, sep="\t")
    # Add column names
    df0.columns = ["x", "y"]
    # reverse the y coordinates because plotting is in reverse order as images
    df0.y = -1 * df0.y
    # center the coordinates of x and y to align plots
    df0.x = centerVector(df0.x)
    df0.y = centerVector(df0.y)
    # interpolate the x, y coordinates with defined number of values
    xOld = np.arange(0, len(df0.x))
    xNew = np.linspace(0, len(df0.x)-1, N)
    f1 = interp1d(xOld, df0.x)
    dfXnew = f1(xNew)
    f2 = interp1d(xOld, df0.y)
    dfYnew = f2(xNew)
    # store interepolated data in a new data frame
    df = pd.DataFrame(np.transpose(np.array([dfXnew, dfYnew])), columns = ["x", "y"])
    # reverse the order of x an y if the curve is not turning clockwise
    if not isClockwise(df.x, df.y):
        temp = df.x.tolist()
        temp.reverse()
        df.x = temp
        temp = df.y.tolist()
        temp.reverse()
        df.y = temp
    # calculate the curvature and store in a new column
    df["curvature"] = curvature_splines(df.x, df.y)
    return df

def getCurvatureDfList(inputFolder, N=500):
    '''Read all ".txt" files in a folder, and return a data frame list in which each
    data frame contains the data frame generated from the getCurvatureDF function of
    each text file.
        Briefly, for each text file, getCurvatureDF reads in a series of (x,y) coordinates
    along a closed curve, calculate the local curvature at N points and return the data
    frame containing 3 columns: x, y and the curvature at (x,y).
    '''
    xyCoorFileList = glob.glob(inputFolder + "*.txt")
    xyCoorFileList.sort()
    curvatureDfList = []
    for f in xyCoorFileList:
        dfTemp = getCurvatureDF(f, N)
        curvatureDfList.append(dfTemp)
    
    return curvatureDfList

def getHighCurvatureCounts(curvatureArray, curvatureThreshold=0.02, normalize=True):
    '''Count the number of data points whose absolute value is larger than a threshold
    
    Parameters:
        curvatureArray: a list of 1-dimensional numpy array
        curvatureThreshold: the threshold value beyond which a number is counted
        normalize: if True, return the counts in percentage of total points in each array
    
    Returns:
        a list of counts, each marks the total number of values exceeding the specified threshold
    '''
    counts=[]
    for i in np.arange(len(curvatureArray)):
        beyondThreshold = [np.abs(curvatureArray[i][ii])>curvatureThreshold for ii in np.arange(len(curvatureArray[i]))]
        counts.append(beyondThreshold.count(True))
    
    if normalize == True:
        counts = np.array(counts)*100.0/len(curvatureArray[i])
    
    return counts


def is_on_edge(cnt, width=1024, height=1024, tolerance=1, im=None):
    '''
    Determine whether a contour (cnt) is on the edge of image (im)
    
    Input Parameters:
    -----------------
    cnt:
        contour of an object (outline)
        
    width, height:
        image width and height in pixels
        
    tolerance:
        distance from the edge to be called on_edge; in pixels
        default: 1
        
    im: 
        numpy array of image read by opencv; if provided, calculate the width and height
    
    
    Returns:
    --------
    res:
        boolean value of whether cnt is on the edge of im
    
    '''
    if im is not None:
        height, width = im.shape
    
    # Get bounding rectangle of the coutour
    x,y,w,h = cv.boundingRect(cnt)
    if (x<=tolerance) or (y<=tolerance) or (x+w>=width-tolerance) or (y+h>=height-tolerance):
        res = True
    else:
        res = False
    
    return res


def get_shape_metrics(outlines_file, width=1024, height=1024, tolerance=1):
    '''
    Compute shape metrics from a txt file storing object outlines
    
    Input Parameters:
    -----------------
    outlines_file:
        A txt file, each line of which has a series of numbers representing
        the (x, y) coordinates
        
    width, height:
        Original image width and height in pixels; used to determine whether
        the object is on_edge
        
    tolerance:
        distance from the edge to be called on_edge; in pixels
        default: 1
    
    
    Returns:
    --------
    df:
        A pandas dataframe with the following columns:
        'cell_id', 'centroid_x', 'centroid_y',
        'area', 'perimeter', 'on_edge',
        'circularity', 'aspect_ratio', 'solidity', 'file_name'
        
    '''
    # Read in coordinates from the outlines text file
    with open(outlines_file, 'r') as f:
        lines = f.readlines()

    shape_metrics = []
    for i, line in enumerate(lines):
        # parse numbers representing (x, y) coordinates
        coordinates = [int(num) for num in line.strip().split(',')]

        # Reshape 1D to 2D
        cnt = np.reshape(coordinates, (-1, 2))

        # compute image moments
        M = cv.moments(cnt)

        # compute centroids from moments
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        # compute area
        area = cv.contourArea(cnt)

        # compute perimeter
        # second parameter is to specify whether contour is closed
        perimeter = cv.arcLength(cnt,True)

        # compute circularity defined as: 4pi*area/sqr(perimeter)
        circularity = 4*np.pi*area/perimeter/perimeter

        # fit ellipse to obtain major and min axis to 
        # compute apsect ratio and angle
        (x,y),(ma,MA),angle = cv.fitEllipse(cnt)
        aspect_ratio = MA/ma

        # compute the convex hull to compute solidity
        hull = cv.convexHull(cnt)
        hull_area = cv.contourArea(hull)
        solidity = float(area)/hull_area

        # determine whether the object is on the image edge
        on_edge = is_on_edge(cnt)

        temp_metrics = [i+1, cx, cy, area, perimeter, on_edge,
                        circularity, aspect_ratio, solidity]
        shape_metrics.append(temp_metrics)

    df = pd.DataFrame(shape_metrics, columns=['cell_id', 'centroid_x', 'centroid_y',
                                              'area', 'perimeter', 'on_edge',
                                              'circularity', 'aspect_ratio', 'solidity'])
 
    base_file_name = os.path.basename(outlines_file)
    df['file_name'] = [base_file_name]*len(df)
    
    return df