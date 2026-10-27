# Near Earth Objects (NEOs) Dataset

A data pipeline that retrieves, cleans, and merges near-Earth asteroid observations from NASA's Near Earth Object Web Service (NeoWs) into a single analysis-ready DataFrame.

## Overview

The source of this data is [NASA's NeoWs](https://api.nasa.gov/) (Near Earth Object Web Service), a RESTful API for near-earth asteroid information. The API returns a rich set of attributes for each object; this project narrows that raw payload down to seven variables relevant to characterizing an object's close approach and potential hazard.

> **Note:** NeoWs limits each request to a maximum window of **seven days** between the start and end date. Longer date ranges must be requested in weekly batches.


### Purpose

The purpose of this project is to explore and examine NEO data to uncover relationships or insightful findings. The project focuses heavily on differences between objects labeled as potentially hazardous and nonhazardous. The project uses summary statistics as well as visual analysis of the data to find relationships and for comparison of the two groups.


### Main Findings

There are far more non-hazardous objects and observations than hazardous objects. There are 41 hazardous observations and 5 hazardous objects copmared to 439 non-hazardous observations and 55 non-hazardous objects. Hazardous NEOs appear to be larger but further to Earth than non-hazardou NEOs. The mean estimated diameter for hazardous NEOs is 0.19 km and is a median 44,023,670.87 km from Earth. In comparison, the mean estimated diameter for non-hazardous NEOs is 0.07 km and is a median 41,372,759.99 km from Earth.

 The mean diameter for all NEOs is about 0.08 km, this is closer to the mean diameter of the non-hazardous objects. The median miss distance for all NEOs is 45,154,508.84 km which is closer to the median of the hazardous NEOs. The mean diameter of all objects is closer to the mean diameter of the non-hazardous NEOs because the dataset is very unbalanced with 55 out of 60 objects are non-hazardous.

 It was also found that the larger the NEO, the brighter the it is and the distribution of NEO relative velocity is positiely skewed.


## Variables

| Column | Type | Description |
| --- | --- | --- |
| `Approach Date` | `datetime64[us]` | Date of the object's close approach to Earth |
| `miss_distance` | `float64` | Distance by which the object missed Earth |
| `relative_velocity` | `float64` | Velocity of the object relative to Earth |
| `object_id` | `str` | Unique identifier for the object — **primary key** |
| `absolute_magnitude_h` | `float64` | Absolute magnitude (H) of the object |
| `estimated_diameter` | `float64` | Estimated diameter of the object |
| `is_potentially_hazardous_asteroid` | `bool` | Flag indicating whether the object is classified as potentially hazardous |

## Data Assembly

The NeoWs csv can be created using one of two files. The first, ```/src/read_data_from_api.ipynb```, requests the data from the api and structures it approapriately for analysis. This file can be execute from the ```/src``` directory using ```python3 read_data_from_api.py```. The second, ```/notebook/load_data.ipynb```, performs the same opperations as ```read_data_from_api.ipynb``` but shows the structure of the raw data from the API.

The NeoWs response is structured so that every approach date contains the approach data for all objects observed on that day. Because of this nesting, the data is read into **two separate DataFrames** that are then merged on approach date:

1. **Approach DataFrame** — `Approach Date`, `miss_distance`, and `relative_velocity` for every NEO observed on that day.
2. **Object DataFrame** — `Approach Date`, `object_id`, `absolute_magnitude_h`, `estimated_diameter`, and `is_potentially_hazardous_asteroid`.

`Approach Date` serves as the join key for this merge. Moving forward, however, `object_id` is used as the primary key, as it is the more practical identifier for a single observation.

The resulting dataset containing all NEO observations is named **`neos_df`**.

## Dataset Structure

`neos_df` contains **7 columns**, **480 rows**, and **no missing values**.

```
 #   Column                             Non-Null Count  Dtype
---  ------                             --------------  -----
 0   Approach Date                      480 non-null    datetime64[us]
 1   miss_distance                      480 non-null    float64
 2   relative_velocity                  480 non-null    float64
 3   object_id                          480 non-null    str
 4   absolute_magnitude_h               480 non-null    float64
 5   estimated_diameter                 480 non-null    float64
 6   is_potentially_hazardous_asteroid  480 non-null    bool
```

## Getting Started

### Prerequisites

- Python 3.9+
- An API key from [api.nasa.gov](https://api.nasa.gov/) (the `DEMO_KEY` works for light testing but is heavily rate limited)

### Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

Store your API key as an environment variable rather than hardcoding it:

```bash
export NASA_API_KEY="your_key_here"
```

## Acknowledgments

Data provided by [NASA's Near Earth Object Web Service (NeoWs)](https://api.nasa.gov/), maintained by the Jet Propulsion Laboratory, California Institute of Technology.
