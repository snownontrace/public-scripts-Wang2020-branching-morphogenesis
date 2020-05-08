import os, glob

def make_movie(tempPath, fps=24, target_size=30, quality=0):
    '''Make a '.mp4' movie from an image sequence using ffmpeg

    Parameters
    ----------
        tempPath: the folder storing the image sequence for making movie; has to end with '/'
        fps: play back speed, frames per second
        target_size: the upper limit of movie file size in MB
        quality: compression quality, use 0 for highest quality and 51 (when using 8-bit )
                    or 63 for worst quality (10-bit)
    Returns
    -------
        Boolean value of whether the movie file exists or not
    '''
    # Use the file list length (total frames) to calculate movie duration in seconds
    datasetPrefix = os.path.basename(tempPath[:-1])
    tif_list = glob.glob(tempPath + datasetPrefix + '-[0-9][0-9][0-9][0-9].tif')
    assert len(tif_list) > 0

    # Use bit rates to precisely control the output file size to be x MB (Mega Bytes)
    # For example, if you want a 30 MB output file for a >9.3 second movie:
    # bitrate = 30 MiB * 8192 [converts MiB to kBit]) / 10 seconds = 24576 kBit/s
    duration = int( len(tif_list)/fps ) + 1
    bit_rate = str( int(target_size * 8192 / duration) ) + 'k'

    # create output file name in a sytematic way
    outMovie = tempPath[:-1] + '-q' + str(quality) + '-' + str(fps) + '-fps-' + str(target_size) + 'MB.mp4'

    # # For making mp4 movies
    # os.system('ffmpeg-422 -r '+str(fps)+' -i '+tempPath+datasetPrefix+'%04d.tif -b:v 24576k\
    #             -vcodec mpeg4 -q:v '+str(quality)+' -y '+outMovie)

    # os.system('ffmpeg-422 -r '+str(fps)+' -i '+tempPath+datasetPrefix+'%04d.tif -b:v 24576k\
    #             -c:v libx264 -pix_fmt yuv420p -q:v '+str(quality)+' -y '+outMovie)
    #
    os.system('ffmpeg-422 -r '+str(fps)+' -i '+tempPath+datasetPrefix+'-%04d.tif -b:v '+bit_rate+' -pass 1 \
                -c:v libx264 -pix_fmt yuv420p -q:v '+str(quality)+' -f mp4 -y /dev/null && \
                ffmpeg-422 -r '+str(fps)+' -i '+tempPath+datasetPrefix+'-%04d.tif -b:v '+bit_rate+' -pass 2 \
                -c:v libx264 -pix_fmt yuv420p -q:v '+str(quality)+' -f mp4 -y '+outMovie)

    return os.path.isfile(outMovie)

if __name__ == "__main__":
    fps_list = [12, 24]
    target_size_list = [10, 30] # in MB (Mega Bytes)

    parentFolder = '/Users/wangs20/2-Branching-morphogenesis-paper/supplemental-movies/'
    movieFolders = glob.glob(parentFolder + 'Movie*/')
    movieFolders.sort()

    for folder in movieFolders:
        print(folder)
        for fps in fps_list:
            for target_size in target_size_list:
                make_movie(folder, fps, target_size)
