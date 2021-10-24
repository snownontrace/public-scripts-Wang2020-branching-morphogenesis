## Instructions of Code Usage
This is a collection of customized scripts (Jupyter notebook, R, ImageJ macro and Jython) used for image analysis, plotting and movie making in [Wang et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34133940/). Please kindly cite our paper if you used them in your work.

---
### Image analysis and plotting

Refer to the table below for a guide of which scripts were used to generate the plot(s) of interest.

| Figures | Scripts used |
|---|---|
| Fig. 1E | SMG-surface-cell-tracks-Imaris.ipynb |
| Fig. 1G-J | SMG-get-peripheral-line-profile-step1.ijm <br> SMG-dynamic-peripheral-line-scan.ipynb <br> SMG-get-peripheral-line-profile-step3.ijm |
| Fig. 2A | SMG-surface-cell-division-types.ipynb |
| Fig. 2B | SMG-post-division-return-time.ipynb |
| Fig. 2D | SMG-get-E-cadherin-surface-to-center-line-scan.ijm <br> SMG-E-cad-line-scan-plotting.ipynb |
| Fig. 2F-G | SMG-get-E-cadherin-edge-AUC-peakHeight-by-line-scan.ijm <br> SMG-E-cad-K14RFP-correlation.ipynb |
| Fig. 3B | count-buds.ijm <br> SMG-bud-count-collagenase-recovery.ipynb |
| Fig. 3E | SMG-surface-cell-division-types.ipynb |
| Fig. 3F | SMG-post-division-return-time.ipynb <br> SMG-surface-residence-ratio.ipynb |
| Fig. 3I | SMG-mesenchyme-1-draw-epithelial-ROIs.ijm <br> SMG-mesenchyme-2-get-mesenchyme-DAPI-actin-images.ijm <br> SMG-mesenchyme-cellpose-segmentation.ipynb <br> SMG-mesenchyme-compute-and-plot-shape-metrics.ipynb |
| Fig. 3J | SMG-mesenchyme-cell-tracks-Imaris.ipynb |
| Fig. 3K | SMG-collagenase-compute-epi-and-mes-ROIs.ijm <br> SMG-collagenase-get-pHH3-epi-mes-quantifications.ijm <br> SMG-collagenase-pHH3-plotting.ipynb |
| Fig. 4A-E | E13epi-scRNA-seq-analysis.ipynb |
| Fig. 4F | E13epi-scRNA-seq-plotting.ipynb |
| Fig. 4H | SMG-Cdh1-smFISH-plotting.ipynb |
| Fig. 5C, F, G | count-buds.ijm <br> SMG-bud-count-single-cell-single-bud-culture.ipynb |
| Fig. 5J | SMG-surface-cell-division-types.ipynb |
| Fig. 6D | count-buds.ijm <br> DLD-1-spheroid-bud-count-decoding-plotting.ipynb |
| Fig. 6E-F | DLD-1-spheroid-curvature-analysis.ipynb |
| Fig. 7B, F, I, L | count-buds.ijm <br> DLD-1-spheroid-bud-count-decoding-plotting.ipynb |
| Fig. 7C, G, J, M | DLD-1-spheroid-draw-interior.ijm < br> DLD-1-spheroid-protruded-area-decoding-plotting.ipynb |
| Fig. 7D | DLD-1-spheroid-curvature-analysis.ipynb |
| Fig. 7N | DLD-1-AFM-plotting.ipynb |
| Fig. S1E | SMG-epithelia-track-speed-Imaris.ipynb |
| Fig. S1F-M | SMG-get-peripheral-line-profile-step1.ijm <br> SMG-dynamic-peripheral-line-scan.ipynb <br> SMG-get-peripheral-line-profile-step3.ijm |
| Fig. S2C-E | SMG-live-draw-3d-ROIs-single-time-frame.ijm <br> SMG-compute-3D-mesh.ipynb <br> SMG-tracking-post-division-return-TrackMate.ipynb |
| Fig. S2F | SMG-time-course-pHH3-draw-and-compute-epi-ROIs.ijm <br> SMG-time-course-pHH3-get-pHH3-surface-interior-quantifications.ijm <br> SMG-time-course-pHH3-plotting.ipynb |
| Fig. S2L | Mathematical-modeling-pHH3-plotting.ipynb |
| Fig. S3A | count-buds.ijm <br> SMG-bud-count-Ecad-integrin-blocking-antibody.ipynb |
| Fig. S3B | count-buds.ijm <br> SMG-bud-count-collagenase-titration.ipynb |
| Fig. S3D | count-buds.ijm <br> SMG-bud-count-BB94-GM6001.ipynb |
| Fig. S4A | E13epi-scRNA-seq-analysis.ipynb |
| Fig. S4E | E13epi-scRNA-seq-plotting.ipynb |
| Fig. S5D, F | DLD-1-cell-get-mean-intensity-Ecad-D193-D266-D267.ijm <br> DLD-1-cell-get-background-intensity-Ecad-D193-D266-D267.ijm <br> DLD-1-cell-Western-blot-and-immunofluorescence-quantification.ipynb |
| Fig. S6B, D-F, I | count-buds.ijm <br> DLD-1-spheroid-bud-count-decoding-plotting.ipynb <br> DLD-1-spheroid-draw-interior.ijm <br> DLD-1-spheroid-protruded-area-decoding-plotting.ipynb <br> DLD-1-spheroid-curvature-analysis.ipynb |
| Fig. S7B, D | count-buds.ijm <br> DLD-1-spheroid-bud-count-decoding-plotting.ipynb <br> DLD-1-spheroid-draw-interior.ijm <br> DLD-1-spheroid-protruded-area-decoding-plotting.ipynb|
| Fig. S7F | DLD-1-cell-get-mean-intensity-b1integrin-and-Ecad-D193-D301-D304.ijm <br> DLD-1-cell-get-background-intensity-b1integrin-and-Ecad-D193-D301-D304.ijm <br> DLD-1-cell-Western-blot-and-immunofluorescence-quantification.ipynb |
| Fig. S7K-L | DLD-1-cell-count-cells-attachment-assay.ijm <br> DLD-1-cell-attachment-assay.ipynb |
| Fig. S7N | DLD-1-AFM-plotting.ipynb |

---
### Making and annotating videos

- Image sequences of automated surface rendering and cell tracking were generated in Imaris 9.5.0 (Bitplane). All other image sequences were generated in Fiji.

  - Tracking of daughter cells from surface-derived cell divisions (Movie S7) was performed using TrackMate, a Fiji plugin. Images of tracked cells were exported using the Jython script "TrackMate-tracking-export-spot-tif-series.py" running in Fiji. Exported image sequences of individual cell tracks were assembled and formatted using ImageJ macro scripts "TrackMate-tracking-save-exported-series-as-stack.ijm" and "TrackMate-tracking-equalize-frames-of-merged-spot-stacks.ijm".


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
