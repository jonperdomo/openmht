# openmht
[![unit tests](https://github.com/jonperdomo/openmht/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/jonperdomo/openmht/actions/workflows/unit-tests.yml)

Python module for multiple hypothesis tracking. Based on the article:

_C. Kim, F. Li, A. Ciptadi and J. M. Rehg, "Multiple Hypothesis Tracking Revisited," 2015 IEEE International Conference on Computer Vision (ICCV), Santiago, Chile, 2015, pp. 4696-4704, doi: 10.1109/ICCV.2015.533._

URL: https://ieeexplore.ieee.org/document/7410890

This implementation utilizes motion scoring only (no appearance scoring)

## Installation

 Install the latest version of [Python 3](https://www.python.org/downloads/)

```$ pip install openmht```

To also plot tracks after completion, install matplotlib:

```$ pip install matplotlib```

## Formatting the Input CSV File
Format the input CSV columns with frame number and pixel positions using the examples under **SampleData/** as a reference.
The **U,V** values represent the 2D positions of objects/detections in that frame. A value of **None** in the output CSV indicates a missed detection. The **Track** column indicates the final track ID for a detection.

## MHT Parameters
Modify parameters by editing the **params.txt** input file. Please read the paper mentioned above to understand how these parameters can be updated to improve performance and accuracy:

| Parameter | Description                                                                                                                                                     |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v         | The image (frame) area in pixels (Default: 307200). The likelihood under the null hypothesis for an observation becomes the probability of detection P<sub>D</sub>=1/**V**.  |
| dth       | Gating area for new detections implemented as the threshold for the Mahalinobis distance d<sup>2</sup> between the observation and prediction (Default=1000).   |

Kalman filter parameters:

| Parameter | Description                                                                                                                            |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------|
| k         | Gain or blending factor. Higher gain results in a greater influence of the measurement relative to the filter's prediction (Default=0) |
| q         | Initial estimate of the process noise covariance (Default=0.00001)                                                                     |
| r         | Initial estimate of the measurement noise covariance (Default=0.01)                                                                    |

Track tree pruning parameters:

| Parameter | Description                                                                                                                                                                       |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| n         | Go back **N** frames and prune branches that diverge from the solution. Larger N yields a more accurate solution due to a larger window| but will take a longer time (Default=1). |
| bth       | If the number of branches exceeds the number **B<sub>th</sub>**| then prune the track tree to only retain the top **B<sub>th</sub>** branches.                                                          |
| nmiss     | A track hypothesis is deleted if it reaches **N<sub>miss</sub>** consecutive frames of missing observations| which are due to occlusion or a false negative.                                 |

## Running the Program
**OpenMHT** takes in the input CSV detections and the parameter file, and saves to the provided output CSV file:

```$ python -m openmht InputDetections.csv OutputDetections.csv ParameterFile.txt```

For generating track plots, add the **--plot** parameter (requires **matplotlib**):

```$ python -m openmht ... --plot```

## Example Results

Results from running **SampleData/SampleInput.csv**:

![OutputTracks](https://github.com/jonperdomo/openmht/assets/14855676/e694aebe-dd62-4d0b-bb1f-0e0d3f5a9339)

<table>
<tr><th>Input</th><th>Output</th></tr>
<tr><td>

| Frame | U | V |
|--|--|--|
0|0.0703|0.3163
1|0.1071|0.3746
1|0.1325|0.1618
2|0.1694|0.4534
2|0.1809|0.1910
2|0.4205|0.0977
3|0.2200|0.5700
3|0.2408|0.2755
3|0.5081|0.1618
4|0.2938|0.6429
4|0.3007|0.3222
4|0.5703|0.2201
5|0.3445|0.7157
5|0.3767|0.4184
5|0.6555|0.2988
6|0.4297|0.8149
6|0.4459|0.4767
6|0.7247|0.3688
7|0.4850|0.8703

</td><td>

|Frame|Track|U|V| 
|--|--|--|--|
0|0|0.0703|0.3163
0|1|None|None
0|2|None|None
0|3|None|None
1|0|0.1071|0.3746
1|1|0.1325|0.1618
1|2|None|None
1|3|None|None
2|0|0.1694|0.4534
2|1|0.1809|0.191
2|2|0.4205|0.0977
2|3|None|None
3|0|0.22|0.57
3|1|0.2408|0.2755
3|2|0.5081|0.1618
3|3|None|None
4|0|0.2938|0.6429
4|1|0.3007|0.3222
4|2|0.5703|0.2201
4|3|None|None
5|0|0.3445|0.7157
5|1|0.3767|0.4184
5|2|0.6555|0.2988
5|3|None|None
6|0|None|None
6|1|0.4459|0.4767
6|2|0.7247|0.3688
6|3|0.4297|0.8149
7|0|None|None
7|1|None|None
7|2|None|None
7|3|0.485|0.8703

</td></tr> </table>
