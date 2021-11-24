# Gentle Paths

We utilize algorithmic and topological methods to get us the shortest path from start to apex within a given mountain terrain. Our first approach taken from this\cite{liu_finding_nodate} paper which explains how to take a surface of a terrain, and search for the gentle shortest path within it. This approach takes a a-star algorithm approach to generate a gentle path for any given terrain. Our second approach is more of a topological approach, utilizing a funnel algorithm on a terrain with holes to find the shortest path.
# Course

COSC 049 21F
# How to run this repo
## Getting the data

To get a particular area you'd like to run either algorithm on, you'll need to grab the lat and long of the of terrain. There are 2 ways to do this. The first way is to use already defined terrain's commented in the code. The other is to generate your own data

#### Use already given data

To use data that we have already defined, you can use any of the lines between line 48 and line 64. Ensure that only 1 terrain is uncomment and the other 2 terrains are uncommented. See current code in `gentle-paths/src/maps_fetch/index.js` Line 48:64 to see how it is currently setup.
#### Generate your own data

The API we use only requires a lat and long to generate the terrain wanted. Our API visualizes a box around the terrain so the peramiters you'd give to the API will be the bottom left lat/long and the top right lat/long. To get the terrain data do the following:

1. Grab the bottom left lat/long and the top right lat/long of the terrain you want
2. Go to `gentle-paths/src/maps_fetch/index.js`
3. Name your terrain in the `MAP_NAME` variable (line 56)
4. enter the lat/long of the bottom left point on line 55, in the `b_l` variable
5. enter the lat/long of the top right point on line 56, in the `t_r` variable

All of these variables (`MAP_NAME` , `b_l`, `t_r`, and `increment`) pertain to the data. Thus, ensure these variables are only called once in the code and if there are any other intances of these variable being declared after your first decleration, make sure to comment it out. The following instructions will be how to run the Map API and generate data.

1. Ensure that the proper creditions are saved in a `.env` file. Have the proper Google Maps API key available before running or else you will run into Auth errors. (ask Ben, Ethan, or me for help if you cant figure it out)
2. run `npm i` command to install all dependencies
3. run `node index.js` to generate the terrain

You should now be able to see the dataset with the name you declared in the `gentle-paths/src/maps` directory.
## A* algoithm

To run the following algorithm on the terrain data set, do the following:


If there are any modules not installed, python will alert you which ones. Ensure that you install those before going through steps 1-3.

1. Navigate to `gentle-paths/src/driver.py` and ensure that line 82 is set to the data you want to use. Make sure to change the name if you have your own custom dataset you downloaded from the above sets.
2. Type `python3 driver.py` in the terminal
3. the results of the algorithm should pop up in a 3-d represented graph

## Funnel Algorithm

To run the funnel algorithm, do the following:

If there are any modules not installed, python will alert you which ones. Ensure that you install those before going through steps 1-3.

1. navigate to `gentle-paths/src/funnel_terrain_test.py` and ensure the data you want to use is set on line 173, in the `graph` variable.
2. Type `python3 funnel_terrain_test.py` in the terminal
3. The results will graphically be displayed once the algorithm has completely ran.