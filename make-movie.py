import os, glob, argparse

def make_movie(tempPath, fps, target_size, n_digit_ImgID=4, quality=0):
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
    tempPattern = '*'
    for i in range(n_digit_ImgID):
        tempPattern = tempPattern + '[0-9]'
    tempPattern = tempPattern + '.tif'
    tif_list = glob.glob(os.path.join(tempPath, tempPattern))

    assert len(tif_list) > 0

    # Infer datasetPrefix from the first file name of the tif file list
    filename_tif0 = os.path.basename(tif_list[0])
    n_trailing_chars = -1*(n_digit_ImgID+4)
    datasetPrefix = filename_tif0[:n_trailing_chars]
    # print(datasetPrefix)

    # Use bit rates to precisely control the output file size to be x MB (Mega Bytes)
    # For example, if you want a 30 MB output file for a >9.3 second movie:
    # bitrate = 30 MiB * 8192 [converts MiB to kBit]) / 10 seconds = 24576 kBit/s
    duration = int( len(tif_list)/fps ) + 1
    bit_rate = str( int(target_size * 8192 / duration) ) + 'k'

    # create output file name in a sytematic way
    outMovie = tempPath[:-1] + '-q' + str(quality) + '-' + str(fps) + '_fps-' + str(target_size) + 'MB.mp4'

    # Call 'ffmpeg' to make mp4 movies
    tifPattern = os.path.join(tempPath, datasetPrefix+'%0'+str(n_digit_ImgID)+'d.tif')
    os.system('ffmpeg -r '+str(fps)+' -i '+tifPattern+' -b:v '+bit_rate+' -pass 1 \
                -c:v libx264 -pix_fmt yuv420p -q:v '+str(quality)+' -f mp4 -y /dev/null && \
                ffmpeg -r '+str(fps)+' -i '+tifPattern+' -b:v '+bit_rate+' -pass 2 \
                -c:v libx264 -pix_fmt yuv420p -q:v '+str(quality)+' -f mp4 -y '+outMovie)

    return os.path.isfile(outMovie)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="folder containing the image sequence for movie making")
    parser.add_argument("fps", help="playback speed in frames per second",
                        type=int, default=12)
    parser.add_argument("target_size", help="the desired file size in MB",
                        type=int, default=30)
    parser.add_argument("n_digit_ImgID", nargs='?', help="optional; the digit number of image IDs of the image sequence; default 4",
                        type=int, default=4)
    parser.add_argument("quality", nargs='?', help="optional; quality, 0 highest, 63 lowest; default 0",
                        type=int, default=0)

    args = parser.parse_args()
    make_movie(args.folder, args.fps, args.target_size, args.n_digit_ImgID, args.quality)

    # fps_list = [6, 12, 24]
    # target_size_list = [10, 20] # in MB (Mega Bytes)
    #
    # parentFolder = '/Users/wangs20/2-Branching-morphogenesis-paper/supplemental-movies/'
    # movieFolders = glob.glob(parentFolder + 'Movie1-*/')
    # movieFolders.sort()
    #
    # for folder in movieFolders:
    #     print(folder)
    #     for fps in fps_list:
    #         for target_size in target_size_list:
    #             make_movie(folder, fps, target_size)
