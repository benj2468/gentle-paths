const _ = require('lodash')
const {Client} = require("@googlemaps/google-maps-services-js")
const fs = require('fs')

const client = new Client({})

const LONG_MIN = -122.041105
const LONG_MAX = -121.465146
const LAT_MIN = 46.696071
const LAT_MAX = 47.088650
const increment = 0.01

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
  