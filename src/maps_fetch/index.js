const _ = require('lodash')
const {Client} = require("@googlemaps/google-maps-services-js")
const fs = require('fs')
const dotenv = require('dotenv')
const process = require('process')
const utmObj = require('utm-latlng')

const radius = 6371
var utm = new utmObj();

// This function converts lat and lng coordinates to GLOBAL X and Y positions
function latlngToGlobalXY(lat, lng){
  //Calculates x based on cos of average of the latitudes
  let x = radius*lng*Math.cos((b_l[0] + t_r[0])/2);
  //Calculates y based on latitude
  let y = radius*lat;
  return {x,y}
}

dotenv.config()

const client = new Client({})

// Seattle

let b_l = [30.954148, 34.424824]
let t_r = [31.977915, 35.541891]
const increment = 0.05

// Mt. Rainier
// let b_l = [46.696071,  -121.465146]
// let t_r = [47.088650, -122.041105]
// const increment = 0.03


// Kansas
// const b_l = [37.000052, -102.043611]
// const t_r = [40.028416, -95.285846]
// const increment = 0.3

const LONG_MIN = Math.min(b_l[1], t_r[1])
const LONG_MAX = Math.max(b_l[1], t_r[1])
const LAT_MIN = Math.min(b_l[0], t_r[0])
const LAT_MAX = Math.max(b_l[0], t_r[0])

const {x: x_min, y: y_min} = latlngToGlobalXY(LAT_MIN, LONG_MIN)

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
        const {Easting: x, Northing: y} = utm.convertLatLngToUtm(item.location.lat, item.location.lng, 1)
        var line = `${x} ${y} ${item.elevation}\r\n`;
        lines.push(line);
      }
    }
    fs.writeFileSync('data.txt', lines.join(''));
  }

  async function convertDataToGrid(){
    let data = await fs.readFile('data.txt');
    data = data.toString().split('\r\n').filter((item)=>{ return item.length > 0 }).map((item)=>{ return item.split(' ') });
    data = data.map((item)=>{
      lat = item[0];
      lng = item[1];
      alt = item[2];
    return [
        ((lat - LAT_MIN) / increment).toFixed(0),
        ((lng - LONG_MIN) / increment).toFixed(0),
        alt
      ].join(' ')
    });
    await fs.writeFile('grid.txt', data.join('\r\n'));
  }


  locations = getLocations()
  console.log(locations[0])
  console.log(locations.length)
  getElevations(locations)
  