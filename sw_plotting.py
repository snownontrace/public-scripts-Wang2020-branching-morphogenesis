import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import seaborn as sns
import numpy as np
from sw_tracking import get_mean_speed_track

font = {'family' : 'Arial',
        'size'   : 7}
matplotlib.rc('font', **font)
plt.rcParams['svg.fonttype'] = 'none'


def plot_2D_mid_outline(polyline_df_xy, t, ax, shift_x, shift_y,
                        line_color, line_alpha, line_width):
#     temp = polyline_df_xy.loc[(polyline_df_xy.t == t) & (polyline_df_xy.z == z)]
    temp = polyline_df_xy.loc[polyline_df_xy.t == t]
    z_values = temp.z.unique()
    midZ = z_values[ int( len(z_values)/2 ) ]
    temp = temp.loc[temp.z==midZ]
    x, y = temp.x.values, temp.y.values
    ax.plot(x-shift_x, y-shift_y, '-', color=line_color, alpha=line_alpha, lw=line_width)

def plot_2D_outlines_xy(polyline_df_xy, t, z_range, ax, shift_x, shift_y,
                        line_color, line_alpha, line_width):
    temp_t = polyline_df_xy.loc[polyline_df_xy.t == t]
    temp_tz = temp_t.loc[( temp_t.z > 50-z_range ) & ( temp_t.z < 50+z_range )]
    for z in temp_tz.z.unique():
        temp = temp_t.loc[temp_t.z==z]
        x, y = temp.x.values, temp.y.values
        ax.plot(x-shift_x, y-shift_y, '-', color=line_color, alpha=line_alpha, lw=line_width)

# def plot_2D_polylines_xy(polyline_df_xy, t, ax,
#                          line_color, line_alpha, line_width):
#     polyline_df_xy_t = polyline_df_xy.loc[polyline_df_xy.t == t]
#     # plot the horizontal lines pf mesh
#     for i in polyline_df_xy_t.z.unique():
#         temp = polyline_df_xy_t.loc[polyline_df_xy_t.z == i]
#         x, y = temp.x.values, temp.y.values
#         ax.plot(x, y, '-', color=line_color, alpha=line_alpha, lw=line_width)
    
def plot_tracks_2D(trackDF,
                   output_fig_path=None,
                   line_color=None, track_list=None,
                   tracks_highlight=None, uniform_line_width=False,
                   plot_xy_outlines=False, polyline_df_xy=None, z_range=15,
                   x_ticks=None, y_ticks=None,
                   draw_spot_start=False, draw_spot_end=False):

    from matplotlib import cm
    # Create a colors dictionary to set same color for the daughter cells of the same cell division
    colors = cm.Dark2(np.linspace(0, 1, trackDF.cell_division_id.nunique()))
    colors = [val for pair in zip(colors, colors) for val in pair]

    fig = plt.figure(figsize=(2, 2), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    x_min, y_min = trackDF.x.min(), trackDF.y.min()
    if track_list is None:
        track_list = trackDF.track_id.unique()
    for i, track in enumerate(track_list):
        df_temp = trackDF[trackDF.track_id==track]
        x, y = df_temp.x.values-x_min, df_temp.y.values-y_min
        
        if (tracks_highlight is not None) and (track in tracks_highlight):
            if uniform_line_width:
                ax.plot(x, y, '-', color='#FF00FF', alpha=.6, lw=.6)
            else:
                ax.plot(x, y, '-', color='#FF00FF', alpha=.8, lw=.8)
            
        else:
#             ax.plot(x, y, '-', color=line_color, alpha=.6, lw=.6)
            if line_color is None:
                ax.plot(x, y, '-', color=colors[i], alpha=.6, lw=.6)
            else:
                ax.plot(x, y, '-', color=line_color, alpha=.6, lw=.6)

        if draw_spot_start == True:
            ax.plot(x[0], y[0], 'ob', alpha=.4, markersize=2, markeredgewidth=0)
        if draw_spot_end == True:
            ax.plot(x[-1], y[-1], 'or', alpha=.4, markersize=2, markeredgewidth=0)
    
    if plot_xy_outlines:
        plot_2D_outlines_xy(polyline_df_xy, t=1,
                            z_range=z_range,
                            shift_x=x_min, shift_y=y_min,
                            ax=ax,
                            line_color='#1A6A82',
                            line_alpha=.02,
                            line_width=.6)
        plot_2D_outlines_xy(polyline_df_xy, t=192,
                            z_range=z_range,
                            shift_x=x_min, shift_y=y_min,
                            ax=ax,
                            line_color='#A05B22',
                            line_alpha=.02,
                            line_width=.6)
        
    # *** add axis labels ***
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # *** set axis ticks if provided ***
    if x_ticks is not None:
        ax.set_xticks(x_ticks)
    if y_ticks is not None:
        ax.set_yticks(y_ticks)
    
    # *** Make the x and y axes equal in dimension to mimic image display ***
    ax.axis('equal')
    
    # *** Flip the y-axis to match the image coordinates ***
    plt.gca().invert_yaxis()
    
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    
    return ax

def plot_3D_polylines_xy(polyline_df_xy, t, ax, line_color, line_alpha, shift_x, shift_y, shift_z):
    polyline_df_xy_t = polyline_df_xy.loc[polyline_df_xy.t == t]
    # plot the horizontal lines pf mesh
    for i in polyline_df_xy_t.z.unique():
        temp = polyline_df_xy_t.loc[polyline_df_xy_t.z == i]
        x, y, z = temp.x.values, temp.y.values, temp.z.values
        ax.plot(x-shift_x, y-shift_y, z-shift_z, '-', color=line_color, alpha=line_alpha, lw=0.2)

def plot_3D_polylines_yz(polyline_df_yz, t, ax, line_color, line_alpha, shift_x, shift_y, shift_z):
    polyline_df_yz_t = polyline_df_yz.loc[polyline_df_yz.t == t]
    # plot the vertical lines pf mesh
    for i in polyline_df_yz_t.z.unique():
        temp = polyline_df_yz_t.loc[polyline_df_yz_t.z == i]
        x, y, z = temp.x.values, temp.y.values, temp.z.values
        ax.plot(z-shift_x, y-shift_y, x-shift_z, '-', color=line_color, alpha=line_alpha, lw=0.2)


def plot_tracks_3D(trackDF, polyline_df_xy, polyline_df_yz,
                   output_fig_path=None, plot_style='white', line_color=None,
                   fig_width=3, fig_height=3, fig_dpi=300,
                   plot_xy_polylines=False, plot_yz_polylines=False,
                   track_list=None, tracks_highlight=None, uniform_line_width=False,
                   elevation=45, azimuth=60, axis_off=False,
                   centering=True, draw_spot_start=False, draw_spot_end=False):
    """This script takes the spot position data of all tracks in 3D
    """
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    # Create a colors dictionary to set same color for the daughter cells of the same cell division
#     colors = cm.jet(np.linspace(0, 1, df.cell_division_id.nunique()))
#     colors = cm.Set1(np.linspace(0, 1, df.cell_division_id.nunique()))
    colors = cm.Dark2(np.linspace(0, 1, trackDF.cell_division_id.nunique()))
    colors = [val for pair in zip(colors, colors) for val in pair]
    
    if plot_style=='white':
        AXES_COLOR = '#000000'#black
        mpl.rc('figure', facecolor='w', edgecolor=AXES_COLOR)
        mpl.rc('axes', facecolor='w', edgecolor=AXES_COLOR, labelcolor=AXES_COLOR)
        mpl.rc('xtick', color=AXES_COLOR)
        mpl.rc('ytick', color=AXES_COLOR)
        mpl.rc('grid', color='#EEEEEE')
    
    if plot_style=='dark':
        AXES_COLOR = '#FFFFFF'#white
        mpl.rc('figure', facecolor='k', edgecolor=AXES_COLOR)
        mpl.rc('axes', facecolor='k', edgecolor=AXES_COLOR, labelcolor=AXES_COLOR)
        mpl.rc('xtick', color=AXES_COLOR)
        mpl.rc('ytick', color=AXES_COLOR)
        mpl.rc('grid', color='gray')
    
    # plotting set up
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=fig_dpi)
    ax = fig.add_axes([0, 0, 1.0, 1.0], projection='3d')
    
    if plot_style=='white':
        # *** Set the background color of the panes ***
        PANECOLOR = (1, 1, 1, 1.0) # white
        ax.w_xaxis.set_pane_color(PANECOLOR)
        ax.w_yaxis.set_pane_color(PANECOLOR)
        ax.w_zaxis.set_pane_color(PANECOLOR)
        # *** Set the line colors of x,y,z axes ***
        AXISCOLOR = (0, 0, 0, 1.0) # black
        ax.w_xaxis.line.set_color(AXISCOLOR)
        ax.w_yaxis.line.set_color(AXISCOLOR)
        ax.w_zaxis.line.set_color(AXISCOLOR)

    if plot_style=='dark':
        # *** Set the background color of the panes ***
        # PANECOLOR = (0.1, 0.1, 0.1, 1.0) # dark grey
        PANECOLOR = (0, 0, 0, 1.0) # black
        ax.w_xaxis.set_pane_color(PANECOLOR)
        ax.w_yaxis.set_pane_color(PANECOLOR)
        ax.w_zaxis.set_pane_color(PANECOLOR)
        # *** Set the line colors of x,y,z axes ***
        AXISCOLOR = (1.0, 1.0, 1.0, 1.0) # white
        ax.w_xaxis.line.set_color(AXISCOLOR)
        ax.w_yaxis.line.set_color(AXISCOLOR)
        ax.w_zaxis.line.set_color(AXISCOLOR)
    
    # calculate the range values and scales in each dimension
    tMin, tMax = trackDF.t.min(), trackDF.t.max()
    xMin, xMax = trackDF.x.min(), trackDF.x.max()
    yMin, yMax = trackDF.y.min(), trackDF.y.max()
    zMin, zMax = trackDF.z.min(), trackDF.z.max()
    print('x, y, z min: ', xMin, yMin, zMin)
    print('x, y, z max: ', xMax, yMax, zMax)
    if centering == False:
        shift_x, shift_y, shift_z = 0, 0, 0
    else:
        shift_x, shift_y, shift_z = np.mean([xMax, xMin]), np.mean([yMax, yMin]), np.mean([zMax, zMin])

    if track_list is None:
        track_list = trackDF.track_id.unique()
    for i, track in enumerate(track_list):
        temp = trackDF.loc[trackDF.track_id == track]
        temp = temp.sort_values('t', ascending=True)
        x, y, z = temp.x, temp.y, temp.z
        x, y, z = np.array(x), np.array(y), np.array(z)
        if (tracks_highlight is not None) and (track in tracks_highlight):
            if uniform_line_width:
                ax.plot(x-shift_x, y-shift_y, z-shift_z, '-', color='#FF00FF', alpha=.6, lw=.6)
            else:
                ax.plot(x-shift_x, y-shift_y, z-shift_z, '-', color='#FF00FF', alpha=.8, lw=.8)
        else:
            if line_color is None:
                ax.plot(x-shift_x, y-shift_y, z-shift_z, '-', color=colors[i], alpha=.6, lw=.6)
            else:
                ax.plot(x-shift_x, y-shift_y, z-shift_z, '-', color=line_color, alpha=.6, lw=.6)

        if draw_spot_start == True:
            ax.plot([x[0]-shift_x], [y[0]-shift_y], [z[0]-shift_z], 'ob', alpha=.4, markersize=2, markeredgewidth=0)
        if draw_spot_end == True:
            ax.plot([x[-1]-shift_x], [y[-1]-shift_y], [z[-1]-shift_z], 'or', alpha=.6, markersize=2, markeredgewidth=0)

    if plot_xy_polylines:
        plot_3D_polylines_xy(polyline_df_xy, 1, ax,
                             line_color='#1A6A82', line_alpha=0.08,
                             shift_x=shift_x, shift_y=shift_y, shift_z=shift_z)
        plot_3D_polylines_xy(polyline_df_xy, 192, ax,
                             line_color='#A05B22', line_alpha=0.08,
                             shift_x=shift_x, shift_y=shift_y, shift_z=shift_z)

    if plot_yz_polylines:
        plot_3D_polylines_yz(polyline_df_yz, 1, ax,
                             line_color='#1A6A82', line_alpha=0.08,
                             shift_x=shift_x, shift_y=shift_y, shift_z=shift_z)
        plot_3D_polylines_yz(polyline_df_yz, 192, ax,
                             line_color='#A05B22', line_alpha=0.08,
                             shift_x=shift_x, shift_y=shift_y, shift_z=shift_z)

    # *** adjust axis limits and turn on/off grids -- has to be after plotting ***
    x0, y0, z0 = xMin-shift_x, yMin-shift_y, zMin-shift_z
    if abs(x0) > abs(y0):
        y0 = x0
    else:
        x0 = y0
#     x0, y0, z0 = -100, -100, -40
#     x0, y0, z0 = -95, -95, -40
#     x0, y0, z0 = -120, -120, -40
    axisLength = abs(x0) * 2
    ax.set_xlim( x0, x0 + axisLength )
    ax.set_ylim( y0, y0 + axisLength )
    ax.set_zlim( z0, z0 + axisLength )
    
    # *** customize grid size ***
    grid_size = 40
    ax.set_xticks(np.arange( x0, x0 + axisLength + 1, grid_size))
    ax.set_yticks(np.arange( y0, y0 + axisLength + 1, grid_size))
    ax.set_zticks(np.arange( z0, z0 + axisLength + 1, grid_size))

    # *** add axis labels ***
#     ax.set_xlabel('x')
#     ax.set_ylabel('y')
#     ax.set_zlabel('z')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    
    # *** add axis tick labels ***
#     ax.set_xticklabels([0, 40, 80, 120, 160])
#     ax.set_yticklabels([0, 40, 80, 120, 160])
#     ax.set_zticklabels([92, 52, 12, -28, -68])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])


#     ax.grid(False)
    ax.view_init(elevation, azimuth) # elevation and azimuth angles for viewpoint settting

    # Flip the y-axis to match the image coordinates
    plt.gca().invert_yaxis()
    
    if axis_off:
        plt.axis('off')
    
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    
    return ax

def plot_cum_dist_deprecated(data, n_bins=None, output_fig_path=None,
                  x_ticks=None, y_ticks=None, y_log_scale=False,
                  fig_width=1.0, fig_height=1.0):
    '''Plot a black curve and a blue histogram representing cumulative distribution of data
    '''
    
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    ax = sns.kdeplot(data, cumulative=True, linewidth=0.8, legend=False, color='k')
    
    plt.hist(data, bins=n_bins, cumulative=True, density=True, color='Blue', rwidth=.9, alpha=.6)
#     ax = sns.distplot(data, kde=False, hist_kws={'cumulative': True, 'rwidth': .9, 'alpha': .5}, norm_hist=True, color='Blue')

    plt.ylabel("Cumulative\nfraction of data")
    
    if x_ticks is not None:
        plt.xticks(x_ticks)

    if y_ticks is not None:
        plt.yticks(y_ticks)
        
    if y_log_scale == True:
    # seems to have issues, may address in the future
        ax.set(yscale="log")
    
    # The following removes excessive clipping to facilitate detailing of line widths and colors etc in illustrator
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    
    return ax

def plot_cum_dist(data, n_bins=None, output_fig_path=None,
                  x_ticks=None, y_ticks=None, y_log_scale=False,
                  x_max=None, y_max=None,
                  fig_width=1.0, fig_height=1.0,
                  clipping_removal=True, axis_off=False):
    '''Plot a black curve and a blue histogram representing cumulative distribution of data
    '''
    
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    ax = sns.kdeplot(data, cumulative=True, linewidth=0.8, legend=False, color='k')
    
    plt.hist(data, bins=n_bins, cumulative=True, density=True, color='Blue', rwidth=.9, alpha=.6)
#     ax = sns.distplot(data, kde=False, hist_kws={'cumulative': True, 'rwidth': .9, 'alpha': .5}, norm_hist=True, color='Blue')

    plt.ylabel("Cumulative\nfraction of data")
    
    if x_ticks is not None:
        plt.xticks(x_ticks)
        
    if x_max is not None:
        plt.xlim( [min(data), x_max] )
        
    if y_log_scale == True:
    # seems to have issues, may address in the future
        ax.set(yscale="log")
    else:
        if y_ticks is not None:
            plt.yticks(y_ticks)

        if y_max is not None:
            plt.ylim( [0, y_max] )

    if clipping_removal == True:
        # The following removes excessive clipping to facilitate detailing
        # of line widths and colors etc. in illustrator
        # *** Note that removing clipping causes issues for log scale ***
        for o in fig.findobj():
            o.set_clip_on(False)
        for o in ax.findobj():
            o.set_clip_on(False)

    if axis_off == True:
        plt.axis("off")
        
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    
    return ax

def plot_dist(data,
              n_bins=None, output_fig_path=None,
              x_ticks=None, y_ticks=None, y_log_scale=False,
              fig_width=1.0, fig_height=1.0):
    '''Plot a black curve and a blue histogram representing cumulative distribution of data
    '''
    
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    ax = sns.kdeplot(data, cumulative=False, linewidth=0.8, legend=False, color='k')
    
    plt.hist(data, bins=n_bins, cumulative=False, density=True, color='Blue', rwidth=.9, alpha=.6)
#     ax = sns.distplot(data)

    plt.ylabel("Probablity density")
    
    if x_ticks is not None:
        plt.xticks(x_ticks)

    if y_ticks is not None:
        plt.yticks(y_ticks)
        
    if y_log_scale == True:
    # seems to have issues, may address in the future
        ax.set(yscale="log")
    
    # The following removes excessive clipping to facilitate detailing of line widths and colors etc in illustrator
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    
    return ax


def plot_tracks_2D_colorcode(trackDF, output_fig_path=None,
                             colorcode='z', color_map='jet', color_bar=True,
                             norm_min=None, norm_max=None,
                             track_list=None, tracks_highlight=None,
                             plot_xy_outlines=False, polyline_df_xy=None, z_range=15,
                             x_ticks=None, y_ticks=None,
                             draw_spot_start=False, draw_spot_end=False):
    
    assert colorcode in ['z', 'speed', 'time']
    
    fig = plt.figure(figsize=(2, 2), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    x_min, y_min = trackDF.x.min(), trackDF.y.min()
#     df = trackDF # alias
    if track_list is None:
        track_list = trackDF.track_id.unique()
    for i, track in enumerate(track_list):
        df_temp = trackDF[trackDF.track_id==track]
        df_temp.sort_values('t', ascending=True, inplace=True)
        df_temp.reset_index(inplace=True, drop=True)
        
        # Extract the x, y coordinates of the points
        x, y = df_temp.x.values-x_min, df_temp.y.values-y_min
        
        # Create a set of line segments so that we can color them individually
        # This creates the points as a N x 1 x 2 array so that we can stack points
        # together easily to get the segments. The segments array for line collection
        # needs to be (numlines) x (points per line) x 2 (for x and y)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        if colorcode == 'z':
            color_code_values = df_temp.z.values[:-1]
            if norm_min is None:
                norm_min = 0
            if norm_max is None:
                norm_max = 100
                
        elif colorcode == 'speed':
            # Calculate the mean track speed (drop last point to match segment number)
            color_code_values = get_mean_speed_track(df_temp, n_rolling=12)[:-1]
            if norm_min is None:
                norm_min = 10
            if norm_max is None:
                norm_max = 40
        
        elif colorcode == 'time':
            # Calculte time from anaphase onset
            # Convert frames to minutes (5 min per frame)
            if 't_normed' in df_temp.columns:
                color_code_values = df_temp.t_normed.values[1:]
            else:
                n_pre = df_temp.pre_anaphase_onset_n_frames.values[0]
                frames = df_temp.t.values[1:]
                start_frame = df_temp.t.min()
                color_code_values = [5*(i-n_pre-start_frame) for i in frames]
            if norm_min is None:
                norm_min = 0
            if norm_max is None:
                norm_max = 240
                
        # make color code values into a numpy array
        color_code_values = np.array(color_code_values)
        
        # Create a continuous norm to map from data points to colors
        norm = plt.Normalize(norm_min, norm_max) # empirically determined speed normalization
        lc = LineCollection(segments, cmap=color_map, norm=norm)
        # Set the values used for colormapping
        lc.set_array(color_code_values)
        lc.set_linewidth(.6)
        line = ax.add_collection(lc)

        if draw_spot_start == True:
            ax.plot(x[0], y[0], 'ob', alpha=.4, markersize=2, markeredgewidth=0)
        if draw_spot_end == True:
            ax.plot(x[-1], y[-1], 'or', alpha=.4, markersize=2, markeredgewidth=0)
    
    if plot_xy_outlines:
        plot_2D_outlines_xy(polyline_df_xy, t=1,
                            z_range=z_range,
                            shift_x=x_min, shift_y=y_min,
                            ax=ax,
                            line_color='#1A6A82',
                            line_alpha=.02,
                            line_width=.6)
        plot_2D_outlines_xy(polyline_df_xy, t=192,
                            z_range=z_range,
                            shift_x=x_min, shift_y=y_min,
                            ax=ax,
                            line_color='#A05B22',
                            line_alpha=.02,
                            line_width=.6)
    
    # *** add color bar ***
    if color_bar:
        fig.colorbar(line, ax=ax)
    
    # *** add axis labels ***
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # *** set axis ticks if provided ***
    if x_ticks is not None:
        ax.set_xticks(x_ticks)
    if y_ticks is not None:
        ax.set_yticks(y_ticks)
    
    # *** Make the x and y axes equal in dimension to mimic image display ***
    ax.axis('equal')
    
    # *** Flip the y-axis to match the image coordinates ***
    plt.gca().invert_yaxis()
    
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    
    return ax

def change_bar_width(ax, new_value):
    '''modify the bar width in bar plots
    
    Input Parameters:
    -----------------
        ax: a matplotlib axis object
        new_value: the desired bar width
    
    Returns:
    --------
        ax: modified axis object
    
    '''
    for patch in ax.patches :
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)
        
    return ax

def plotCountBar(groups, counts, outputFigPath,
                 plotting_order=None,
                 yMax=None, yTicks=None,
                 yLabel=None,
                 xLabel_off=False,
                 xticklabels_angle=None,
                 xTickLabels=None,
                 bar_width=0.7,
                 fig_width=0.7, fig_height=0.9):
    '''plot bar plot of bud counting data, save .svg as outputFigPath
    
    Note: error bar here is 95% confidence interval by bootstrapping
    '''
    
    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    sns.barplot(groups, counts,
                order=plotting_order,
                color=".7", # This a nicer looking lighter gray to my own taste
                errwidth=.7, errcolor="k", capsize=.2, ci=95)

    if yMax is None:
        yMax = int(max(counts)/5 + 1) * 5
        
    if yTicks is None:
        yTicks = [10*i for i in range(int(max(counts)/10 + 1))]
        
    if yLabel is None:
        yLabel = 'Bud count'
    
    plt.ylim(0, yMax)
    plt.yticks(yTicks)
    plt.ylabel(yLabel)
    
    if xLabel_off:
        plt.xlabel("")
    else:
        plt.xlabel("Groups")

    if xticklabels_angle is not None:
        if xTickLabels is None:
            xTickLabels = ax.get_xticklabels()
        ax.set_xticklabels(xTickLabels,
                           rotation=xticklabels_angle,
                           horizontalalignment='right')
    
    # Narrow the bar width
    change_bar_width(ax, bar_width)
    
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)

    plt.savefig(outputFigPath)
    
    return ax

def plot_track_distance_to_surface(df, output_fig_path=None,
                                   N_tracks=200, fig_width=1.5, fig_height=1.0, rand_seed=7):
    assert 'TrackID' in df.columns
    assert 'Distance' in df.columns
    
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    tracks = df.TrackID.unique()
    # Plot N randomly chosen tracks to show most movement of surface-proximal tracks move within the surface
    np.random.seed(rand_seed)
    track_count = 0
    for i in np.random.randint(0, len(tracks), N_tracks*100):
        # Get the data frame subset of current track
        df_temp = df[ df.TrackID==tracks[i] ]
        # Filter out short tracks
        if len(df_temp)<36:
            continue
        # Filter out very long tracks that tends to contain errors
        if len(df_temp)>120:
            continue

        # Filter out tracks with positive distance,
        # which are likely outside of the epithelial surface
        if pd.Series(df_temp.Distance>-3).any():
            continue

        # Normalize the x-axis to make the plot cleaner
        x = np.arange(len(df_temp))/(len(df_temp)-1)
#         plt.plot(x, df_temp.Distance, alpha=0.2, lw=0.4)
        plt.plot(x, df_temp.Distance, alpha=0.1, lw=0.4, color='k')

        track_count += 1
        if track_count > N_tracks:
            break

    # Check whether desired number of plot were obtained
    assert track_count == N_tracks + 1
    
    plt.xlabel('Relative track time')
    plt.ylabel("Distance to\nepithelial surface")
    plt.ylim( [-50, 0] )
    plt.yticks( [-45, -30, -15, 0])

    # The following removes excessive clipping to facilitate detailing of line widths and colors etc in illustrator
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if output_fig_path is not None:
        plt.savefig(output_fig_path)

    return ax

def plotCurvatureHeatmap(curvatureArray, outputFigPath, colorMax=0.02, fig_width=1.0, fig_height=0.8):
    '''plot heatmap of curvature, save .svg as outputFigPath'''

    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    sns.heatmap(np.stack(curvatureArray), cmap="coolwarm", vmin=-1*colorMax, vmax=colorMax)

    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)

    plt.axis("off")
    
    plt.savefig(outputFigPath)

    return ax

# Plotting functions

def plotCurvatureHeatmap(curvatureArray, outputFigPath, colorMax=0.02, fig_width=1.0, fig_height=0.8):
    '''plot heatmap of curvature, save .svg as outputFigPath'''

    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    sns.heatmap(np.stack(curvatureArray), cmap="coolwarm", vmin=-1*colorMax, vmax=colorMax)

    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)

    plt.axis("off")
    
    plt.savefig(outputFigPath)

    return ax

def plotCurvatureSwarm(groups, counts, outputFigPath, fig_width=0.7, fig_height=0.9):
    '''plot swarm and error bar of curvature counting data, save .svg as outputFigPath
    
    Note: error bar here is 95% confidence interval by bootstrapping
    '''
    
    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    sns.swarmplot(groups, counts, size=2)    
    sns.pointplot(groups, counts,
                  ci=95, capsize=.2, errwidth=.7,
                  markers='_', scale=.5, join=False, color="Gray")

    yMax = int(max(counts)/5 + 1) * 5
    plt.ylim(-2, yMax)
    yTicks = [10*i for i in range(int(max(counts)/10 + 1))]
    plt.yticks(yTicks)
    
    plt.xlabel("Groups")
    plt.ylabel("% Perimeter with\nhigh curvature")

    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    plt.savefig(outputFigPath)
    
    return ax

def plotCurvatureBar(groups, counts, outputFigPath,
                     bar_width=.7,
                     plotting_order=None,
                     yMax=None, yTicks=None,
                     fig_width=.7, fig_height=.9):
    '''plot swarm and error bar of curvature counting data, save .svg as outputFigPath
    
    Note: error bar here is 95% confidence interval by bootstrapping
    '''
    
    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    sns.barplot(groups, counts, color=".7",
                order=plotting_order,
                errwidth=.7, errcolor="k",
                capsize=.2, ci=95)

    if yMax == None:
        yMax = int(max(counts)/5 + 1) * 5
    if yTicks == None:
        yTicks = [10*i for i in range(int(max(counts)/10 + 1))]
    
    plt.ylim(0, yMax)
    plt.yticks(yTicks)
    
    plt.xlabel("Groups")
    plt.ylabel("% Perimeter with\nhigh curvature")
    
    # Narrow the bar width
    change_bar_width(ax, bar_width)

    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)

    plt.savefig(outputFigPath)
    
    return ax


def plot_curvature(df, outputFigPath=None, size=3, colorNormMax=0.02,
                   fig_width=0.7, fig_height=0.9, flip_y=False,
                   x_max=None, y_max=None):
    
    assert 'x' in df.columns
    assert 'y' in df.columns
    assert 'curvature' in df.columns
    
    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    ax.scatter(df.x, df.y, s=size, c=df.curvature, vmin=-1*colorNormMax, vmax=colorNormMax, cmap="coolwarm")

    # When supplied, specify the range of x, y axes
    if x_max is not None:
        ax.set_xlim([0, x_max])
    if y_max is not None:
        ax.set_ylim([0, y_max])
    
    if flip_y == True:
        # Flip the y-axis to match the image coordinates,
        # if this has not been handled in the DF creation step
        plt.gca().invert_yaxis()
    
    # Make the x and y axes equal in dimension to mimic image display
    plt.axis('equal')
    plt.axis("off")
    
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if outputFigPath is not None:
        plt.savefig(outputFigPath)
    
    return ax

def plot_curvature_one_line(df, outputFigPath=None, size=3, colorNormMax=0.02,
                   fig_width=0.7, fig_height=0.9, flip_y=False,
                   x_max=None, y_max=None):
    
    assert 'x' in df.columns
    assert 'y' in df.columns
    assert 'curvature' in df.columns
    
    fig = plt.figure(figsize=(fig_width,fig_height), dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    # Note: marker 's' is square
    ax.scatter(np.zeros(len(df.x)), range(len(df.y)), marker='s', s=size, c=df.curvature, vmin=-1*colorNormMax, vmax=colorNormMax, cmap="coolwarm")

    # When supplied, specify the range of x, y axes
    if x_max is not None:
        ax.set_xlim([0, x_max])
    if y_max is not None:
        ax.set_ylim([0, y_max])
    
    if flip_y == True:
        # Flip the y-axis to match the image coordinates,
        # if this has not been handled in the DF creation step
        plt.gca().invert_yaxis()
    
    # Make the x and y axes equal in dimension to mimic image display
    plt.axis('equal')
    plt.axis("off")
    
    for o in fig.findobj():
        o.set_clip_on(False)
    for o in ax.findobj():
        o.set_clip_on(False)
    
    if outputFigPath is not None:
        plt.savefig(outputFigPath)
    
    return ax
