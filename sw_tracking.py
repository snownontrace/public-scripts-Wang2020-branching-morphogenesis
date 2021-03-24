import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from scipy.spatial.distance import euclidean
import scipy.linalg

def isInPolygon(testX, testY, vertX, vertY, addedStart=None, addedEnd=None):
    """Determines whether point(testX, testY) is within the polygon defined by
    ordered vertices (vertX[i], vertY[i]).  An additional starting or ending
    point can be supplemented if needed.
        Note: testing points on the edges may be considered inside or outside
    depending on the edges.
    """
    # insert the added starting or ending points if provided
    if addedStart is not None:
        vertX = np.insert(vertX, 0, addedStart[0])
        vertY = np.insert(vertY, 0, addedStart[1])
    if addedEnd is not None:
        vertX = np.append(vertX, addedEnd[0])
        vertY = np.append(vertY, addedEnd[1])

    # Initialize a condition variable "c" as outside of the polygon, then
    # flip its value at each time when a horizontal semi-infinate ray from
    # the testing point (increasing x, fixed y) crosses an edge. Odd and even
    # number of crossings mean "inside" and "outside", respectively.
    # The first judging condition determines whether the test point falls
    # within the y range of the evaluating edge. Importantly, it also ensures
    # that vertY[j]-vertY[i] is not 0. If testy is within the y range of edge,
    # it then determines whether the on-edge point at y-level "testY" is to
    # the right of testX, e.g. whether testX < xOnEdge.
    c = False
    nVert = len(vertX)
    for i in range(nVert):
        j = i + 1
        if j == nVert: j = 0 # last point connects back to first point
        if ( (vertY[i]>testY) != (vertY[j]>testY) ):
            slopeEdge = (vertX[j]-vertX[i]) / (vertY[j]-vertY[i])
            xOnEdge = slopeEdge * (testY-vertY[i]) + vertX[i]
            if testX < xOnEdge:
                c = not c
        # print(c)
    return c

def getDistance(spotCoor, meshDF, THRESHOLD_DIS=None):
    """
    Calculate the minimum distance between a spot and a mesh grid

    Inputs
    ------
    spotCoor:
        A list or 1-D numpy array of the spot coordinate [x, y, z]
            x, y, z coordinates are calibrated (usually in microns)

    meshDF:
        A pandas data frame specifying the mesh grid
    
    Returns
    -------
    A tuple of 3 items:
        1. The minimum distance between the spot and the mesh grid
        2. The path position of the grid point with the minimal distance
        3. The z position of the grid point with the minimal distance

    """
    
    # when a threshold is given, only search the +- threshold cube within spot
    if THRESHOLD_DIS is not None:
        meshDF = meshDF.loc[meshDF.x >= spotCoor[0] - THRESHOLD_DIS]
        meshDF = meshDF.loc[meshDF.x <= spotCoor[0] + THRESHOLD_DIS]
        meshDF = meshDF.loc[meshDF.y >= spotCoor[1] - THRESHOLD_DIS]
        meshDF = meshDF.loc[meshDF.y <= spotCoor[1] + THRESHOLD_DIS]
    if len(meshDF.x.values) == 0:
        return np.inf, np.inf, np.inf
    meshGrids = np.c_[meshDF.x.values, meshDF.y.values, meshDF.z.values]
    dis = [euclidean(spotCoor, grid) for grid in meshGrids]
    # dis = [np.linalg.norm(spotCoor - grid) for grid in meshGrids]
    index_min = np.argmin(dis)
    distance = dis[index_min]
    pathPosMin = meshDF.pathPos.iloc[index_min]
    zPosMin = meshDF.zPos.iloc[index_min]
    return distance, pathPosMin, zPosMin

def getDistance2meshes(spotCoor, meshDF1, meshDF2):
    """
    Calculate the minimum distance between a spot and a mesh grid

    Inputs
    ------
    spotCoor:
        A list or 1-D numpy array of the spot coordinate [x, y, z]
            x, y, z coordinates are calibrated (usually in microns)

    meshDF1 and meshDF2:
        Pandas data frames specifying two mesh grids
    
    Returns
    -------
    The minimum distance between the spot and the two mesh grids.

    """
    dist1 = getDistance(spotCoor, meshDF1)
    dist2 = getDistance(spotCoor, meshDF2)
    
    return np.min([dist1, dist2])

def f_getDistance2meshes(x):
    '''
    A wrapper function to accept a list of parameters for parallel processing
    
    Input
    -----
    x[0]: a spot coordinate (list or numpy array of x, y, z positions)
    x[1]: first mesh dataframe
    x[2]: second mesh dataframe
    
    Returns
    -------
    A number representing the shortest distance of a spot to the 2 meshes

    '''
    return getDistance2meshes(x[0], x[1], x[2])

def refineDistance(spotCoor, p0, p1, p2):
    """Takes the spot coordinate and 3 corners of a triangle, first
    fit a plane of the triganle, then find the distance of the spot to
    the plane defined by a formular. Return the distance and foot point.
    """
    if np.all(p0 == np.inf) or np.all(p1 == np.inf) or np.all(p2 == np.inf):
        refinedDis = np.inf
        footCoor = np.array([np.inf, np.inf, np.inf])
        return refinedDis, footCoor
    spotCoor, p0, p1, p2 = np.array(spotCoor), np.array(p0), np.array(p1), np.array(p2)
    v0, v1, v2 = spotCoor - p0, p1 - p0, p2 - p0
    # print(v0, v1, v2)
    # If spotCoor falls on p0, then distance is 0, spotCoor is the foot point
    if np.all(v0 == 0):
        refinedDis = 0
        footCoor = spotCoor.flatten()
        return refinedDis, footCoor
    # If v0 is perpendicular to the plane, then lenth of v0 is the distance,
    # and p0 is the foot point
    if np.all(v0*v1 == 0) and np.all(v0*v2 == 0):
        refinedDis = euclidean(v0, np.zeros_like(v0))
        footCoor = p0.flatten()
        return refinedDis, footCoor
    # If the trivial cases are not true, we will first compute the norm
    # vector that is perpendicular to the plane.
    # print("checkpoint")
    A0 = np.c_[v1, v2].T
    A = A0[:, 0:2] # note that index here is left included, right excluded
    b = A0[:, 2] * -1
    x = scipy.linalg.solve(A, b)    # solve Ax=b
    # print(np.allclose(np.dot(A, x), b))   # check wehther solution is good
    vNorm = np.array([x[0], x[1], 1.0])
    A = np.c_[vNorm, v1, v2].T
    b = np.array([np.dot(vNorm, p0), np.dot(v1, spotCoor), np.dot(v2, spotCoor)]).T
    x = scipy.linalg.solve(A, b)    # solve Ax=b
    # print(np.allclose(np.dot(A, x), b))   # check wehther solution is good
    footCoor = x.flatten()
    vFoot = footCoor - p0
    A = A0[:, 0:2] # note that index here is left included, right excluded
    b = vFoot[0:2]
    x = scipy.linalg.solve(A, b)    # solve x1*v1 + x2*v2 = vFoot
    # print(np.allclose(np.dot(A, x), b))   # check wehther solution is good
    # determine whether foot point is inside the triangle
    if x[0] >= 0 and x[1] >= 0 and (x[0] + x[1]) <= 1:
        # print("Foot is inside the triangle!")
        refinedDis = euclidean(spotCoor,footCoor)
        return refinedDis, footCoor
    else:
        # print("Foot is outside the triangle!")
        vertices = np.array([p0, p1, p2])
        # dis = [np.linalg.norm(spotCoor - p) for p in vertices]
        dis = [euclidean(spotCoor, p) for p in vertices]
        tempIndex = np.argmin(dis)
        footCoor = vertices[tempIndex].flatten()
        refinedDis = dis[tempIndex]
        return refinedDis, footCoor

def getGridCoor(meshDF, zPos, pathPos):
    """ Return the grid coordinates at zPos and pathPos assuming meshDF is a
    mesh data frame at a single time point.
    """
    temp = meshDF
    temp = temp.loc[temp.zPos == zPos]
    temp = temp.loc[temp.pathPos == pathPos]
    if len(temp.x.values) > 1:
        exit('Mesh contains multiple (zPos, pathPos)!')
    if len(temp.x.values) == 0:
        WARNING: ('Requested (zPos, pathPos) is outside of the mesh!')
        gridCoor = np.array([np.inf, np.inf, np.inf])
        # gridCoor = [np.inf, np.inf, np.inf]
    else:
        gridCoor = np.c_[temp.x.values, temp.y.values, temp.z.values].flatten()
        # gridCoor = [temp.x.values, temp.y.values, temp.z.values]
    return gridCoor

def getDisFoot(spotCoor, meshDF, pathPos0=None, zPos0=None):
    """ Takes the spot coordinate and the mesh data, calculate the minimum
    distance of existing grids, then refine the distance by considering 4
    adjacent triangle planes sharing the initial foot point. Select the minimum
    of the 4 refined distances. Return the foot point coordinate.

    Note: spotCoor is ideally 1-D numpy array.
    """
    if pathPos0 is None or zPos0 is None:
        _, pathPos0, zPos0 = getDistance(spotCoor, meshDF)
    p0 = getGridCoor(meshDF, zPos0, pathPos0)
    p1 = getGridCoor(meshDF, zPos0 + 1, pathPos0)
    p2 = getGridCoor(meshDF, zPos0, pathPos0 + 1)
    p3 = getGridCoor(meshDF, zPos0 - 1, pathPos0)
    p4 = getGridCoor(meshDF, zPos0, pathPos0 - 1)
    # print(spotCoor)
    # print(p0, p1, p2, p3, p4)
    dis1, foot1 = refineDistance(spotCoor, p0, p1, p2)
    dis2, foot2 = refineDistance(spotCoor, p0, p2, p3)
    dis3, foot3 = refineDistance(spotCoor, p0, p3, p4)
    dis4, foot4 = refineDistance(spotCoor, p0, p4, p1)
    disList = [dis1, dis2, dis3, dis4]
    footList = [foot1, foot2, foot3, foot4]
    dis = min(disList)
    foot = footList[np.argmin(disList)]
    return dis, foot

def decomposeVector(v1, v2):
    """Project vector v2 onto the direction of vector v1.
    Return vPara (same direction as v1) and vPerpend (perpendicular
    to the direction of v1)
    """
    v1, v2 = np.array(v1).flatten(), np.array(v2).flatten()
    if len(v1) == 1 or len(v2) == 1:
        exit('Both vectors have to be at least 2-D!')
    if len(v1) != len(v2):
        exit('The two vectors need to have the same length!')
    v1_norm = v1 / euclidean(v1, [0, 0, 0])
    vPara = v1_norm * np.dot(v1_norm, v2)
    vPerpend = v2 - vPara
    # print(np.dot(vPara, vPerpend))
    return vPara, vPerpend

def splinePath(x, y, N, z=None):
    """Takes a set of (x,y) coordinates, spline along z if provided,
    otherwise along its path. Finally, interpolate at N equal
    distance points.  Return 2 or 3 size N numpy arrays representing
    interpolated N (x,y) or (x,y,z) coordinates.
    """
    if z is None:
        dr = (np.diff(x)**2 + np.diff(y)**2)**.5 # segment lengths
        r = np.zeros_like(x)
        r[1:] = np.cumsum(dr) # integrate path
        r_int = np.linspace(0, r.max(), N) # regular spaced path
        z, z_int = r, r_int
        splx = UnivariateSpline(z, x, s=0, ext='const') # interpolate
        # splx.set_smoothing_factor(0.5)
        x_int = splx(z_int)
        sply = UnivariateSpline(z, y, s=0, ext='const')
        # sply.set_smoothing_factor(0.5)
        y_int = sply(z_int)
        return x_int, y_int
    if z is not None:
        # check whether z is increasing -- requied for spline interpolate
        dz = np.diff(z)
        if not np.all(dz >= 0):
            exit('z for splinePath is not increasing!')
        z_int = np.linspace(z.min(), z.max(), N)
        splx = UnivariateSpline(z, x, s=0, ext='const') # interpolate
        # splx.set_smoothing_factor(0.5)
        x_int = splx(z_int)
        sply = UnivariateSpline(z, y, s=0, ext='const')
        # sply.set_smoothing_factor(0.5)
        y_int = sply(z_int)
        return x_int, y_int, z_int

def discretizePath(x, y, N, z=None):
    """Similar to splinePath, but do linear interpolation instead of spline.
    Takes a set of (x,y) coordinates, interpolate N points along z if provided,
    otherwise along its path. Return 2 or 3 size N numpy arrays representing
    interpolated N (x,y) or (x,y,z) coordinates.
    """
    if z is None:
        dr = (np.diff(x)**2 + np.diff(y)**2)**.5 # segment lengths
        r = np.zeros_like(x)
        r[1:] = np.cumsum(dr) # integrate path
        r_int = np.linspace(0, r.max(), N) # regular spaced path
        x_int = np.interp(r_int, r, x) # interpolate
        y_int = np.interp(r_int, r, y)
        return x_int, y_int
    if z is not None:
        z_int = np.linspace(z.min(), z.max(), N)
        x_int = np.interp(z_int, z, x) # interpolate
        y_int = np.interp(z_int, z, y)
        return x_int, y_int, z_int

def meshFromPolylines(inputFolder, N=100, N_CROSS=30, VOXEL_DEPTH=2.0):
    """Takes a list of .txt files storing ordered coordinates of polylines
    at relatively sparse z slices and time intervals, interpolate to generate
    a time series of mesh grids (N points along the polyline at N_CROSS
    differnt z planes).

    The input files are a series of txt files that each contains a list
    of ordered x,y coordinates.  The file name of each txt file indicates
    the z slice and time frame.

    First, it reads in the series of x,y coordinates, interpolate equal
    distance points along the spline fitted line for plotting on the
    corresponding z plane and time point.

    Second, it takes the ordered set of x,y,z points along the polyline path,
    spline and interpolate again to get a dense enough mesh grid points
    at each time point.

    Third, it interpolate along the time line to make sure every time point
    has a mesh grid representing the bud surface.

    Finally, all data will be saved into a pandas DataFrame, which is returned.
    """
    fileList = glob.glob(inputFolder+'*.txt')
    fileList.sort()

    xyData, tzData = [], []
    for f in fileList:
        xyData.append(pd.read_table(f, header = None))
        f = f.split('/')[-1]
        f = f.split('.')[0]
        tzData.append([int(s) for s in f.split('-') if s.isdigit()])
    tzData = np.array(tzData)
    # print(xyData)
    # print(tzData)

    # interpolate along each path to position crosslines
    pathData = []
    for i in range(len(xyData)):
        temp = xyData[i].values
        x, y = temp[:,0], temp[:,1]
        try:
            x_int, y_int = splinePath(x, y, N)
        except: # exception will rise when there are only 2 or 3 points
            x_int, y_int = discretizePath(x, y, N)
        # The following is time series in frame number
        tempT = np.ones_like(x_int) * tzData[i,0]
        # The following is z slice in microns
        tempZ = np.ones_like(x_int) * tzData[i,1] * VOXEL_DEPTH
        # Record the point position along path
        pathPos = np.arange(N)
        tempDF = pd.DataFrame([x_int, y_int, tempZ, tempT, pathPos])
        tempDF = tempDF.transpose()
        pathData.append(tempDF)
    # concat all data into one big pandas data frame
    pathDF = pd.concat(pathData, ignore_index=True)
    pathDF.columns = ['x', 'y', 'z', 't', 'pathPos']

    # # select a subset of the data
    # pathDF = pathDF.loc[pathDF.z >= 9*VOXEL_DEPTH]
    # pathDF = pathDF.loc[pathDF.z <= 38*VOXEL_DEPTH]
    # pathDF = pathDF.loc[pathDF.t >= 131]

    # interpolate along crosslines to get meshes for existing time points
    meshData = []
    for t in pathDF.t.unique():
        pathDF_t = pathDF.loc[pathDF.t == t]
        for i in pathDF_t.pathPos.unique():
            pathDF_ti = pathDF_t.loc[pathDF_t.pathPos == i]
            temp = pathDF_ti.sort_values('z', ascending=True)
            x, y, z = temp.x, temp.y, temp.z
            # no exception handling since z length should always be more than 3
            x_int, y_int, z_int = splinePath(x, y, N_CROSS, z)
            # x_int, y_int, z_int = discretizePath(x, y, N_CROSS, z) # linear
            tempT = np.ones_like(x_int) * t
            tempPos = np.ones_like(x_int) * i
            tempPosZ = np.arange(len(z_int))
            tempDF = pd.DataFrame([x_int, y_int, z_int, tempT, tempPos, tempPosZ])
            tempDF = tempDF.transpose()
            meshData.append(tempDF)
    meshDF = pd.concat(meshData, ignore_index=True)
    meshDF.columns = ['x', 'y', 'z', 't', 'pathPos', 'zPos']

    # interpolate the mesh data for every time frame
    tMeshData = []
    for zPos in meshDF.zPos.unique():
        meshDF_zPos = meshDF.loc[meshDF.zPos == zPos]
        for i in meshDF_zPos.pathPos.unique():
            temp = meshDF_zPos.loc[meshDF_zPos.pathPos == i]
            temp = temp.sort_values('t', ascending=True)
            x, y, t = temp.x, temp.y, temp.t
            tN = t.max() - t.min() + 1
            # x_int, y_int, t_int = discretizePath(x, y, tN, t)
            try:
                x_int, y_int, t_int = splinePath(x, y, tN, t)
            except:
                x_int, y_int, t_int = discretizePath(x, y, tN, t)
            tempPosZ = np.ones_like(x_int) * zPos
            z = temp.z.unique()[0]
            tempZ = np.ones_like(x_int) * z
            tempPos = np.ones_like(x_int) * i
            tempDF = pd.DataFrame([x_int, y_int, tempZ, t_int, tempPos, tempPosZ])
            tempDF = tempDF.transpose()
            tMeshData.append(tempDF)
    tMeshDF = pd.concat(tMeshData, ignore_index=True)
    tMeshDF.columns = ['x', 'y', 'z', 't', 'pathPos', 'zPos']
    return tMeshDF

def get_polyline_len(spotCoors):
    '''
    Calculate the polyline length along an ordered set of spot coordinates


    Inputs
    ------
    spotCoors:
        A list of spot coodinates.
        Each item is a 3-item list or array [x, y, z]
    
    
    Returns
    -------
        Cumulative distance of all segments
        
    '''
    # When only 1 splot is given
    if len(spotCoors) == 1:
        return 0
    
    dist = 0
    for i in range(len(spotCoors)-1):
        dist += euclidean(spotCoors[i], spotCoors[i+1])
    
    return dist
    
def get_mean_speed(spotCoors, time_interval=5):
    '''
    Calculate mean speed of an ordered sequence of spot coordinates.
    The time intervals between adjacent spots are constant.
    
    
    Inputs
    ------
    spotCoors:
        A list of spot coodinates.
        Each item is a 3-item list or array [x, y, z]
        
    time_interval:
        Duration between adjacent spots. In minutes. Default is 5
    
    
    Returns
    -------
        Mean speed along the poly line specified by spotCoors
        
    '''
    # When only 1 splot is given
    if len(spotCoors) == 1:
        return 0
    
    polyline_len = get_polyline_len(spotCoors)
    # total time in hours
    total_time = time_interval * ( len(spotCoors)-1 ) / 60
    mean_speed = polyline_len / total_time
    
    return mean_speed

def get_mean_speed_track(df, n_rolling=12, time_interval=5):
    '''
    Calculate the mean track speed from a data frame of the entire spot series
    
    Inputs
    ------
    df:
        A Pandas data frame of all spot series in a track
        
    n_rolling:
        The number of track segments to average for a more smooth speed calculation
        
    time_interval:
        Duration between adjacent spots. In minutes. Default is 5
    
    
    Returns
    -------
        Mean speed at each point (spot) along the track
    
    '''
#     # sort values by t in case it was not sorted
#     df.sort_values('t', ascending=True, inplace=True)
    
    # construct a list of all spot coordinates in time order
    spotCoors = []
    n_spots = len(df)
    for i in range(n_spots):
        spotCoor = [df.x[i], df.y[i], df.z[i]]
        spotCoors.append(spotCoor)
    
    n_before = int( np.floor(n_rolling/2) )
    n_after = n_rolling - n_before
    
    # For special cases when a track is even shorter than specified n_rolling
    if n_rolling + 1 >= n_spots:
        speed_temp = get_mean_speed(spotCoors, time_interval)
        speed_lst = [speed_temp] * n_spots
        return speed_lst
    
    # For general cases when a track is longer than n_rolling
    speed_lst=[]
    
    # For the beginning spots
    for i in range(n_before+1):
        spotCoors_local = spotCoors[:(i+n_after+1)]
        speed_temp = get_mean_speed(spotCoors_local, time_interval)
        speed_lst.append(speed_temp)
        
    # For the middle spots
    for i in range(n_before+1, n_spots-n_after):
        spotCoors_local = spotCoors[(i-n_before):(i+n_after+1)]
        speed_temp = get_mean_speed(spotCoors_local, time_interval)
        speed_lst.append(speed_temp)
        
    # For the ending spots
    for i in range(n_spots-n_after, n_spots):
        spotCoors_local = spotCoors[(i-n_before):]
        speed_temp = get_mean_speed(spotCoors_local, time_interval)
        speed_lst.append(speed_temp)
    
    return speed_lst

def normalize_time(df,
                   ref='pre_anaphase_onset_n_frames',
                   time_interval=5):
    '''
    Normalize the time so that it starts from the anaphase onset
    
    Inputs
    ------
    df:
        A Pandas data frame of all spot series in a track
        
    ref:
        The column storing the number of frames before anaphase onset,
        or some other meaningful number to serve as the reference point
        
    time_interval:
        Duration between adjacent spots. In minutes. Default is 5
    
    
    Returns
    -------
        A Pandas data frame with added column 't_normed'
    
    '''
    # Return the df as is if 't_normed' is already there
    if 't_normed' in df.columns:
        print('There is already a \'t_normed\' column!')
        return df
    
    track_list = df.track_id.unique()
    df_list = []
    for track in track_list:
        df_temp = df[df.track_id==track]
        df_temp.sort_values('t', ascending=True, inplace=True)
        df_temp.reset_index(inplace=True, drop=True)
        
        # Note: the frame when two daughter cell chromatin separated
        # is considered at time 0
        #
        # Frame number prior to anaphase onset
        n_pre = df_temp[ref].values[0]
        frames = df_temp.t.values
        start_frame = df_temp.t.min()
        t_normed = [5*(i-n_pre-start_frame) for i in frames]
        df_temp['t_normed'] = t_normed
        df_list.append(df_temp)
    
    df_all = pd.concat(df_list, ignore_index=True)
    
    return df_all


def get_cell_division_tracking_df(f_tracking=None, f_return_time=None, f_combined=None):
    '''
    Data wrangling to combine the tracking and return time data into a single data frame
    
    Inputs
    ------
    f_tracking:
        Path to the csv file storing TrackMate exported long-term manual tracking data
    f_return_time:
        Path to the csv file storing manually annoated daughter cell returning time from
        the anaphase onset to surface. Numbers are in minutes.
    f_combined:
        Path to the csv file storing combined tracking data.
            If exists, read directly from it.
            Otherwise, construct from f_tracking and f_return_time and save to csv.
    
    Returns
    -------
    df_cell_division_tracking:
        Pandas DataFrame of the combined tracking data
    
    '''
    data_folder = '../data/cell-division-tracking-data/'
    if f_combined is None:
        f_combined = data_folder + '180218-mTmGHisG-2photon-cell-division-tracking.csv'
    
    if os.path.isfile(f_combined):
        print('A combined csv file exists! Data frame will be directly read from this csv file.')
        df_cell_division_tracking = pd.read_csv(f_combined)
        return df_cell_division_tracking
    
    if f_tracking is None:
        f_tracking = data_folder + '180218-mTmGHisG-ROI1-track-info-with-cell-division-id.csv'
    if f_return_time is None:
        f_return_time = data_folder + '180218-mTmGHisG-2photon-cell-division-returning-time.csv'
    
    # Read in the TrackMate exported long-term manual tracking data of cell divisions for plotting
    df = pd.read_csv(f_tracking)

    df.sort_values(by=['cell_division_id', 'track_id', 't'], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # Drop the daughter cells whose tracks were incomplete (goes beyond the FOV or time series)
    cell_division_id_to_drop = ['incomplete1A', 'incomplete1B']
    df = df[~df.cell_division_id.isin(cell_division_id_to_drop)]

    # Remove the A, B postfix to consolidate cell_division id
    df.cell_division_id = [i[:-1] for i in df.cell_division_id]

    # Make the cell_division_id to be integer type
    df.cell_division_id = df.cell_division_id.astype('int64')

#     print('The row and column numbers of tracking data:', df.shape)
    
    
    # In manual tracking using Trackmate, one of the daughter cells begin from the separation of 
    # the two daughter cells (anaphase onset).
    #
    # To plot the tracks that reflect the overlapping origin of both daughter cells, append
    # the surface to anaphase onset part of tracks from the matching daughter cell
    # 
    # In addition, record the duration of surface cell from leaving the surface to ananphase onset

    pre_anaphase_onset_n_frames = []
    track1_post_anaphase_n_frames = []
    track2_post_anaphase_n_frames = []

    for cell_division in df.cell_division_id.unique():
    # for cell_division in [20]:# for testing
        df_temp = df[df.cell_division_id==cell_division]
    #     print(df_temp.shape)
        assert df_temp.track_id.nunique() == 2
        track1_id = df_temp.track_id.unique()[0]
        track2_id = df_temp.track_id.unique()[1]
        track1 = df_temp[df_temp.track_id==track1_id]
        track2 = df_temp[df_temp.track_id==track2_id]
        if track1.t.min() < track2.t.min():
            to_add = track1[track1.t < track2.t.min()]
            assert to_add.shape[0] > 0
            to_add.loc[:,'track_id'] = [ df_temp.track_id.unique()[1] ] * to_add.shape[0]
            if len(track1)-len(to_add) < len(track2):
                track1_post_anaphase_n_frames.append([track1_id,
                                                      len(track1)-len(to_add),
                                                      str(cell_division)+'_faster'])
                track2_post_anaphase_n_frames.append([track2_id,
                                                      len(track2),
                                                      str(cell_division)+'_slower'])
            else:
                track1_post_anaphase_n_frames.append([track1_id,
                                                      len(track1)-len(to_add),
                                                      str(cell_division)+'_slower'])
                track2_post_anaphase_n_frames.append([track2_id,
                                                      len(track2),
                                                      str(cell_division)+'_faster'])
        else:
            to_add = track2[track2.t < track1.t.min()]
            assert to_add.shape[0] > 0
            to_add.loc[:,'track_id'] = [ df_temp.track_id.unique()[0] ] * to_add.shape[0]
            if len(track1) < len(track2)-len(to_add):
                track1_post_anaphase_n_frames.append([track1_id,
                                                      len(track1),
                                                      str(cell_division)+'_faster'])
                track2_post_anaphase_n_frames.append([track2_id,
                                                      len(track2)-len(to_add),
                                                      str(cell_division)+'_slower'])
            else:
                track1_post_anaphase_n_frames.append([track1_id,
                                                      len(track1),
                                                      str(cell_division)+'_slower'])
                track2_post_anaphase_n_frames.append([track2_id,
                                                      len(track2)-len(to_add),
                                                      str(cell_division)+'_faster'])
        df = pd.concat([df, to_add])
        df.reset_index(inplace=True, drop=True)
        pre_anaphase_onset_n_frames.append([cell_division, len(to_add)])

    df.sort_values(by=['cell_division_id', 'track_id', 't'], inplace=True)
    df.reset_index(inplace=True, drop=True)
#     print(df.shape)

    # Annotate the pre_anaphase_onset_n_frames data
    df_pre_anaphase_onset_n_frames = pd.DataFrame(pre_anaphase_onset_n_frames,
                                                  columns=['cell_division_id',
                                                           'pre_anaphase_onset_n_frames'])

    # Annotate the post_anaphase_n_frames data
    df_track1 = pd.DataFrame(track1_post_anaphase_n_frames,
                             columns=['track_id',
                                      'post_anaphase_n_frames',
                                      'track_id_slower_or_faster'])
    df_track2 = pd.DataFrame(track2_post_anaphase_n_frames,
                             columns=['track_id',
                                      'post_anaphase_n_frames',
                                      'track_id_slower_or_faster'])
    df_track_post_anaphase_n_frames = pd.concat([df_track1, df_track2])
    df_track_post_anaphase_n_frames.reset_index(inplace=True, drop=True)
#     df_track_post_anaphase_n_frames.head()

    df_cell_division = df.merge(df_pre_anaphase_onset_n_frames, on='cell_division_id')
    df_cell_division = df_cell_division.merge(df_track_post_anaphase_n_frames, on='track_id')
    df_cell_division.head()
    
    # Read in manually annotated return time data
    df = pd.read_csv(f_return_time, header = 0, sep=',')
    # Construct a new track_id to match the merged data frame
    df['track_id_slower_or_faster'] = [str(df.cell_division_id[i])+'_'+df.faster_or_slower_daughter[i]
                                       for i in range(len(df))]
    df_anaphase_to_surface_return = df.loc[:, ['track_id_slower_or_faster', 'anaphase_to_surface_return']]
    df_anaphase_to_surface_return.head()

    df_cell_division = df_cell_division.merge(df_anaphase_to_surface_return, on='track_id_slower_or_faster')
    df_cell_division.head()
    
    df_cell_division.to_csv(f_combined, index=False)
    return df_cell_division


def get_track_to_surf_dist(track_spot_surf_dist_file):
    '''
    Compute the mean track-to-surface distance for each track
    
    Inputs
    ------
    track_spot_surf_dist_file:
        Path to csv file of spot-do-surface distance data
    
    Returns
    -------
    df_cell_division_tracking:
        Pandas DataFrame of the mean track-to-surface distance (averaged over all spots)
        
    '''
    
    # Read in data of all spot to surface distance
    df = pd.read_csv(track_spot_surf_dist_file, skiprows=3)
    df.rename(columns={'Shortest Distance to Surfaces':'Distance'}, inplace=True)

    # get mean distance for each track
    track_mean_dist_surf = []
    for track_id in df.TrackID.unique():
        df_temp = df[df.TrackID == track_id]
        track_mean_dist_surf.append([track_id, df_temp.Distance.mean(), df_temp.Distance.min(), df_temp.Distance.max()])
        
    df_epi_track_mean_dist_surf = pd.DataFrame(track_mean_dist_surf,
                                               columns=['ID', 'mean_dist_surf', 'min_dist_surf', 'max_dist_surf'])
    
    return df_epi_track_mean_dist_surf

def combine_speed_and_surf_dist(track_mean_speed_file, track_spot_surf_dist_file):
    '''
    combine the mean track speed and mean track-to-surface distance data frames;
    
    Inputs
    ------
    track_mean_speed_file:
        Path to csv file of mean track speed data
        
    track_spot_surf_dist_file:
        Path to csv file of spot-do-surface distance data
    
    
    Returns
    -------
    df_merged:
        Pandas DataFrame of the mean track-to-surface distance (averaged over all spots)
        
    '''
    
    # Read in data of mean track speed for all epithelial tracks
    df_epi_mean_speed = pd.read_csv(track_mean_speed_file, skiprows=3)
    df_epi_mean_speed.rename(columns={'Track Speed Mean':'Mean_Track_Speed'}, inplace=True)
    
    # Get mean track-to-surface distance
    df_epi_track_dist_surf = get_track_to_surf_dist(track_spot_surf_dist_file)
    
    # Combine data
    df_merged = df_epi_mean_speed.merge(df_epi_track_dist_surf, on='ID')
    
    return df_merged