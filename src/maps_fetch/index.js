const _ = require('lodash')
const {Client} = require("@googlemaps/google-maps-services-js")
const fs = require('fs')
const dotenv = require('dotenv')
const process = require('process')
const utmObj = require('utm-latlng')

const radius = 6371
var utm = new utmObj();

dotenv.config()

const client = new Client({})


/**
     * Calculates the haversine distance between point A, and B.
     * @param {number[]} latlngA [lat, lng] point A
     * @param {number[]} latlngB [lat, lng] point B
     * @param {boolean} isMiles If we are using miles, else km.
     */
 const haversineDistance = ([lat1, lon1], [lat2, lon2], isMiles = false) => {
  const toRadian = angle => (Math.PI / 180) * angle;
  const distance = (a, b) => (Math.PI / 180) * (a - b);
  const RADIUS_OF_EARTH_IN_KM = 6371;

  const dLat = distance(lat2, lat1);
  const dLon = distance(lon2, lon1);

  lat1 = toRadian(lat1);
  lat2 = toRadian(lat2);

  // Haversine Formula
  const a =
    Math.pow(Math.sin(dLat / 2), 2) +
    Math.pow(Math.sin(dLon / 2), 2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.asin(Math.sqrt(a));

  let finalDistance = RADIUS_OF_EARTH_IN_KM * c;

  if (isMiles) {
    finalDistance /= 1.60934;
  }

  return finalDistance;
};

// Seattle
// const MAP_NAME = 'SEATTLE'
// let b_l = [47.451372, -122.371493]
// let t_r = [47.787456, -122.012248]
// const increment = 0.005

// Rainier
// const MAP_NAME = 'RAINIER'
// let b_l = [46.696071,  -121.465146]
// let t_r = [47.088650, -122.041105]
// const increment = 0.01


// const MAP_NAME = "FRANCONIA"
// let b_l = [43.974171, -71.915121]
// let t_r = [44.234835, -71.482978]
// const increment = 0.006

// const MAP_NAME = "MARK_TWAIN"
// let b_l = [36.566851, -92.180749]
// let t_r = [38.314609, -90.273188]
// const increment = 0.05

const MAP_NAME = 'SI'
let b_l = [47.487434, -121.770493]
let t_r = [47.546380, -121.687076]
const increment = 0.001

// Kansas
// const MAP_NAME = 'KANSAS'
// let b_l = [37.000052, -102.043611]
// let t_r = [40.028416, -95.285846]
// const increment = 0.3

const LONG_MIN = Math.min(b_l[1], t_r[1])
const LONG_MAX = Math.max(b_l[1], t_r[1])
const LAT_MIN = Math.min(b_l[0], t_r[0])
const LAT_MAX = Math.max(b_l[0], t_r[0])


const bottom_right = [b_l[0], t_r[1]]
const top_left = [t_r[0], b_l[1]]
const DX = haversineDistance(b_l, bottom_right) * 1000
const DY = haversineDistance(b_l, top_left) * 1000

const fix = (lat, lng, alt) => {
  return [(lat - LAT_MIN) * DX / (LAT_MAX - LAT_MIN), (lng - LONG_MIN) * DY / (LONG_MAX - LONG_MIN), alt]
}


function getLocations(){
    var current_lat = LAT_MIN;
    var current_long = LONG_MIN;
    let locations = [];
    while(current_lat < (LAT_MAX + increment)){
      while(current_long < (LONG_MAX + increment)){
        locations.push([current_lat, current_long]);
        current_long = current_long + increment;
      }
      current_lat = current_lat + increment;
      current_long = LONG_MIN;
    }
    // console.log('width of grid', distance(LAT_MIN, LONG_MIN, LAT_MAX, LONG_MIN));
    // console.log('height of grid', distance(LAT_MIN, LONG_MIN, LAT_MIN, LONG_MAX));
    console.log('points', locations.length);
    let firstPoints = locations.slice(0, 2);
    console.log('firstPoints', firstPoints);
    // console.log('distance between points', distance(firstPoints[0][0],   firstPoints[0][1], firstPoints[1][0], firstPoints[1][1]));
    return locations.map((item)=>{
      return {
        lat: String(item[0].toFixed(5)), 
        lng: String(item[1].toFixed(5))
      } 
    });
  }

  async function getResult(locations){
    // console.log(locations)
    let response = await client.elevation({
      params: {locations, key: process.env.GOOGLE_API}
    })
    return response.data.results
  }
  async function getElevations(locations=null){
    console.log(locations.length)
    var chunkSize = 500;
    var chunked = _.chunk(locations, chunkSize);
    var lines = [];
    for(var i=0;i<chunked.length;i++){
      var chunk = chunked[i];
      try {
        var result = await getResult(chunk);
      } catch(e){
        console.log('e', e);
        return;
      }
      
      for(var k=0;k<result.length;k++){
        var item = result[k];
        var line = `${item.location.lat} ${item.location.lng} ${item.elevation}\r\n`;
        lines.push(line);
      }
    }
    fs.writeFileSync(`../maps/${MAP_NAME}.txt`, lines.join(''));
  }

  async function convertDataToGrid(){
    let data = await fs.readFileSync(`../maps/${MAP_NAME}.txt`);
    data = data.toString().split('\r\n').filter((item)=>{ return item.length > 0 }).map((item)=>{ return item.split(' ') });
    data = data.map((item)=>{
      lat = item[0];
      lng = item[1];
      alt = item[2];
    return fix(lat, lng, alt).join(' ')
    });
    await fs.writeFileSync(`../maps/${MAP_NAME}.txt`, data.join('\r\n'));
  }

const main = async () => {
  locations = getLocations()
  console.log(locations[0])
  console.log(locations.length)
  await getElevations(locations)
  convertDataToGrid()
}
  
  

main()