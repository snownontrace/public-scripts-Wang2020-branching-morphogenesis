## Instructions of Code Usage
This is a collection of customized scripts (Jupyter notebook, R, ImageJ macro and Jython) used for image analysis, plotting and movie making in Wang et al., 2020 (PubMed ID will be updated after publication). Please kindly cite our paper if you used them in your work.

---
### Image analysis and plotting

Refer to the table below for a guide of which scripts were used to generate the plot(s) of interest.

| Figures | Scripts used |
|---|---|
| Fig. 1E | Imaris-tracking-surface-data-plotting.ipynb |
| Fig. 1G-J | get-peripheral-line-profile-step1.ijm <br> Dynamic-peripheral-line-scan.ipynb <br> get-peripheral-line-profile-step3.ijm |
| Fig. 2A-B | TrackMate-tracking-cell-division-data-plotting.ipynb |
| Fig. 2D | get-E-cadherin-surface-to-center-line-scan.ijm <br> E-cad-line-scan-plotting.ipynb |
| Fig. 2F-G | get-E-cadherin-edge-AUC-peakHeight-by-line-scan.ijm <br> Ecad-K14RFP-correlation.ipynb |
| Fig. 3B-C | count-buds.ijm <br> Bud-count-decoding-plotting.ipynb |
| Fig. 4A-E | E13epi-scRNA-seq-analysis.ipynb |
| Fig. 5C, F | count-buds.ijm <br> Bud-count-decoding-plotting.ipynb |
| Fig. 6D-F <br> Fig. 7B-C, E, G | count-buds.ijm <br> Bud-count-decoding-plotting.ipynb <br> Spheroid-curvature-analysis.ipynb |
| Fig. S1C | Imaris-tracking-surface-data-plotting.ipynb |
| Fig. S1D-K | get-peripheral-line-profile-step1.ijm <br> Dynamic-peripheral-line-scan.ipynb <br> get-peripheral-line-profile-step3.ijm |
| Fig. S2C-E | draw-3d-ROIs-single-time-frame.ijm <br> Compute-3D-mesh.ipynb <br> TrackMate-tracking-cell-division-data-plotting.ipynb |
| Fig. S3C, F | get-pHH3-surface-interior-mean-intensity.ijm <br> Numerical-modeling-pHH3-Ki67-quantification-plotting.ipynb |
| Fig. S3G-H | count-buds.ijm <br> Bud-count-decoding-plotting.ipynb |
| Fig. S4B-D | E13epi-scRNA-seq-analysis.ipynb |
| Fig. S5D, F | get-mean-intensity-Ecad-D193-D266-D267.ijm <br> get-background-intensity-Ecad-D193-D266-D267.ijm <br> Western-blot-and-immunofluorescence-quantification.ipynb |
| Fig. S6B, D-F | Spheroid-curvature-analysis.ipynb |
| Fig. S7D | get-mean-intensity-b1integrin-and-Ecad-D193-D301-D304.ijm <br> get-background-intensity-b1integrin-and-Ecad-D193-D301-D304.ijm <br> Western-blot-and-immunofluorescence-quantification.ipynb |
| Fig. S7I-J | count-cells-attachment-assay.ijm <br> Cell-attachment-assay-analysis.ipynb |

---
### Making and annotating videos

- Image sequences of automated surface rendering and cell tracking were generated in Imaris 9.5.0 (Bitplane). All other image sequences were generated in Fiji.

  - Tracking of daughter cells from surface-derived cell divisions (Movie S7) was performed using TrackMate, a Fiji plugin. Images of tracked cells were exported using the Jython script "TrackMate-tracking-export-spot-tif-series.py" running in Fiji. Exported image sequences of individual cell tracks were assembled formatted using ImageJ macro scripts "TrackMate-tracking-save-exported-series-as-stack.ijm" and "TrackMate-tracking-equalize-frames-of-merged-spot-stacks.ijm".


- Image stacks were annotated using "movie-annotation-add-time-stamp.ijm", "movie-annotation-add-scale-bar.ijm" and "movie-annotation-add-arrows-time-lapse-frames.ijm" before or after being combined or concatenated into a single image stack for a single video.

  - Note, make sure the image width and height pixel sizes are even numbers, otherwise ffmpeg may complain.


- Annotated image stacks were exported to tif image sequences and made into H.264 encoded mp4 videos using "make-movie.py", which is a Python wrapper of [ffmpeg](https://www.ffmpeg.org/).

  ```
  usage: python make-movie.py [-h] folder fps target_size [n_digit_ImgID] [quality]

  positional arguments:
    folder         folder containing the image sequence for movie making
    fps            playback speed in frames per second
    target_size    the desired file size in MB
    n_digit_ImgID  optional; the digit number of image IDs of the image
                   sequence; default 4
    quality        optional; quality, 0 highest, 63 lowest; default 0

  optional arguments:
    -h, --help     show this help message and exit
  ```

  For example, the following command makes the image sequence stored in '\~/branching-paper/movie-1' into a '.mp4' movie at 12 fps and with a file size under 15 MB. The movie is saved in the parental folder of the image sequence folder ('\~/branching-paper/'):
  ```bash
  python make-movie.py ~/branching-paper/movie-1 12 15
  ```
