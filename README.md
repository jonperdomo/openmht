# openmht
Python module for multiple hypothesis tracking. Based on the article:

_C. Kim, F. Li, A. Ciptadi and J. M. Rehg, "Multiple Hypothesis Tracking Revisited," 2015 IEEE International Conference on Computer Vision (ICCV), Santiago, 2015, pp. 4696-4704.
doi: 10.1109/ICCV.2015.533
URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7410890&isnumber=7410356_

## Dependencies
 Install the latest version of [Python 3](https://www.python.org/downloads/)

## Usage
Format the input CSV file using the following example: 

| Frame | U | V |
| ------------- | ------------- | ------------- |
| 0  | 9.97  | 10  |
| 0  | 15.2  | 14.9  |
| 1  | 9.9  | 10.1  |
| 1  | 15  | 14.89  |

Example output:

| Frame | Track | U | V |
| ------------- | ------------- | ------------- | ------------- |
| 0  | 0  |  9.97  | 10  |
| 0  | 1  |  15.2  | 14.9  |
| 1  | 0  |  9.9  | 10.1  |
| 1  | 1  |  15  | 14.89  |

Running OpenMHT in the command line:

```$ python C:/Users/*/openmht.py -i C:/Users/*/InputDetections.csv -o C:/Users/*/OutputDetections.csv```


## Parameters
Modify the Kalman filter parameters by editing the file **params.txt**:

_image_area_: Image / frame area in pixels (Default: 307200)

_gating_area_:  Gating area for new detections (Default: 1000)

_k_: Gain or blending factor (Default: 0)

_q_:  Kalman filter process variance (Default: 0.00001)

_r_: Estimate of measurement variance (Default: 0.01)
