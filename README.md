# openmht
Python module for multiple hypothesis tracking. Based on the article:

_C. Kim, F. Li, A. Ciptadi and J. M. Rehg, "Multiple Hypothesis Tracking Revisited," 2015 IEEE International Conference on Computer Vision (ICCV), Santiago, 2015, pp. 4696-4704.
doi: 10.1109/ICCV.2015.533
URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7410890&isnumber=7410356_

Note: This implementation utilizes motion scoring only (no appearance scoring)

### Dependencies
 Install the latest version of [Python 3](https://www.python.org/downloads/)
 
### Installation

```$ pip install openmht```

### Input data
Format the input CSV columns with frame number and pixel positions using the examples under *SampleData/* as a reference.
The U,V values represent the 2D positions of objects/detections in that frame. A value of *None* in the output CSV indicates a missed detection. The *Track* column indicates the final track ID for a detection.

### Parameters
Modify parameters by editing the **params.txt** input file:

| **Parameter** | **Description** |
| --- | --- |
| image_area | The image (frame) area in pixels (Default: 307200) |
| gating_area | Gating area for new detections (Default: 1000) |
| k | Gain or blending factor (Default: 0) |
| q |  Kalman filter process variance (Default: 0.00001) |
| r | Estimate of measurement variance (Default: 0.01) |
| n | N-scan branch pruning parameter |

### Running:
OpenMHT takes 3 parameters: The input CSV, output CSV, and parameter file paths.

```$ python -m openmht InputDetections.csv OutputDetections.csv ParameterFile.txt```

### Example output
<table>
<tr><th>Input</th><th>Output</th></tr>
<tr><td>

| Frame | U | V |
|--|--|--|
0|-0.0411|0.208
0|9.97|10
0|15.2|14.9
1|14|13
1|-0.0099|0.00141
1|9.9|10.1
1|15.1|14.9
2|14.1|13
2|-0.009|0.00141
2|10|10.099
2|15|14.89

</td><td>

|Frame|Track|U|V| 
|--|--|--|--|
0|0|-0.0411|0.208
0|1|9.97|10.0
0|2|15.2|14.9
0|3|None|None
1|0|-0.0099|0.00141
1|1|9.9|10.1
1|2|15.1|14.9
1|3|14.0|13.0
2|0|-0.009|0.00141
2|1|10.0|10.099
2|2|15.0|14.89
2|3|14.1|13.0

</td></tr> </table>
