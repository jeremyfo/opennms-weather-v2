#!/usr/bin/env python
#
# This script gathers weather data from weather.gov api so it can be displayed in
# OpenNMS.
#
# Copyright 2019 Jeremy Ford - jeremyfo@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import sys
if (sys.version_info > (3,0)):
    import urllib.request
else:
    import urllib
import requests # conda install requests or pip install requests

# Add your weather station id
station_id = "KSFO"

# Add your weather zone id you want to receive alerts for
zone_id = "CAZ006"

# Fahrenheit set True; Celsius set False
use_fahrenheit = True

# Show Radar map? If so set Radar Station ID
show_radar = True
radar_id = "MUX"

######

def get_weather_data(station):
    api_url_base = 'https://api.weather.gov/'
    current_obs_url = '{0}/stations/{1}/observations/latest'.format(api_url_base, station)
    response = requests.get(current_obs_url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None

def get_alert_data(zone):
    api_url_base = 'https://api.weather.gov/'
    current_alert_url = '{0}/alerts/active/zone/{1}'.format(api_url_base, zone)
    response = requests.get(current_alert_url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None

def get_radar_data(station):
    radar_url = 'https://radblast.wunderground.com/cgi-bin/radar/WUNIDS_map?station={0}&num=10&delay=50&rainsnow=1&smooth=1'.format(station)
    if (sys.version_info > (3,0)):
        radar = urllib.request.urlretrieve(radar_url,'/opt/opennms/jetty-webapps/opennms/includes/radar.gif')
    else:
        radar = urllib.urlretrieve(radar_url,'/opt/opennms/jetty-webapps/opennms/includes/radar.gif')
    return None

def get_compass(degree):
    value = int((degree / 22.5) + .5)
    compass = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return compass[(value % 16)]

def main():
    # I have noticed the weather.gov api returns _null_ for values randomly or if there is nothing to report (instead of 0)
    # Need to check each value if not the script will crash...

    # Get Current Observations
    obs = get_weather_data(station_id)

    if obs['properties']['timestamp']:
        obs_time = obs['properties']['timestamp']
    else:
        obs_time = '00:00:00'

    if obs['properties']['textDescription']:
        text = obs['properties']['textDescription']
    else:
        text = "Null"

    if obs['properties']['icon']:
        icon = obs['properties']['icon']
    else:
        icon = "Null"

    if obs['properties']['temperature']['value']:
        tempC = round(obs['properties']['temperature']['value'],1)
        tempF = round(9.0/5.0 * tempC + 32, 1)
    else:
        tempC = 0
        tempF = 0

    if obs['properties']['relativeHumidity']['value']:
        humidity = round(obs['properties']['relativeHumidity']['value'],1)
    else:
        humidity = "Null"

    if obs['properties']['windChill']['value']:
        windChillC = round(obs['properties']['windChill']['value'],1)
        windChillF = round(9.0/5.0 * windChillC + 32, 1)
    else:
        windChillC = "N/A"
        windChillF = "N/A"

    if obs['properties']['heatIndex']['value']:
        heatIndexC = round(obs['properties']['heatIndex']['value'],1)
        heatIndexF = round(9.0/5.0 * heatIndexC + 32, 1)
    else:
        heatIndexC = "N/A"
        heatIndexF = "N/A"

    if obs['properties']['dewpoint']['value']:
        dewpointC = round(obs['properties']['dewpoint']['value'],1)
        dewpointF = round(9.0/5.0 * dewpointC + 32, 1)
    else:
        dewpointC = 0
        dewpointF = 0

    if obs['properties']['precipitationLast6Hours']['value']:
        precip = round(obs['properties']['precipitationLast6Hours']['value'],2)
    else:
        precip = '0.00'

    # Convert m/s to mph
    if obs['properties']['windSpeed']['value']:
        windSpeed = round(obs['properties']['windSpeed']['value'] * 2.23694,2)
    else:
        windSpeed = 0

    # Convert m/s to mph
    if obs['properties']['windGust']['value']:
        windGust = round(obs['properties']['windGust']['value'] * 2.23694,2)
    else:
        windGust = 0

    if obs['properties']['windDirection']['value']:
        windDirection = get_compass(obs['properties']['windDirection']['value'])
    else:
        windDirection = 0

    # Get current alerts
    alerts = get_alert_data(zone_id)

    html_top = """
    <%@page language="java"
            contentType="text/html"
            session="true"
    %>

    <div class="panel panel-default">
            <div class="panel-heading">
                    <h3 class="panel-title">Current Weather</a></h3>
            </div>
    <br>
    """

    html_bot = """
    </div>
    """

    myFile = open('/opt/opennms/jetty-webapps/opennms/includes/weather.jsp', 'w+')
    myFile.write('{0}\n'.format(html_top))
    myFile.write('<ul style="list-style-type:none">\n')
    myFile.write('<li><img src="{0}" alt="Current Conditions"></li>\n'.format(icon))
    myFile.write('<br><li><b>Current Conditions: {0}</b></li>\n'.format(text))
    if use_fahrenheit:
        myFile.write('<li><b>Temperature: {0}</b></li>\n'.format(str(tempF)))
        myFile.write('<li><b>WindChill: {0}</b></li>\n'.format(str(windChillF)))
        myFile.write('<li><b>HeatIndex: {0}</b></li>\n'.format(str(heatIndexF)))
        myFile.write('<li><b>Dewpoint: {0}</b></li>\n'.format(str(dewpointF)))
    else:
        myFile.write('<li><b>Temperature: {0}</b></li>\n'.format(str(tempC)))
        myFile.write('<li><b>WindChill: {0}</b></li>\n'.format(str(windChillC)))
        myFile.write('<li><b>HeatIndex: {0}</b></li>\n'.format(str(heatIndexC)))
        myFile.write('<li><b>Dewpoint: {0}</b></li>\n'.format(str(dewpointC)))
    myFile.write('<li><b>Wind Speed: {0} MPH Direction: {1}</b></li>\n'.format(str(windSpeed), str(windDirection)))
    myFile.write('<li><b>Wind Gust: {0}</b></li>\n'.format(str(windGust)))
    myFile.write('<li><b>Humidity: {0}%</b></li>\n'.format(str(humidity)))
    myFile.write('<li><b>Precipitation: {0}</b></li>\n'.format(str(precip)))
    if not len(alerts['features']):
        myFile.write('<li><b>There are currently no alerts for {0} </b></li>\n'.format(station_id))
    else:
        for alert in alerts['features']:
            myFile.write('<li><font color=red><b>{0}</b></font></li>\n'.format(alert['properties']['headline']))
    myFile.write('<li>Observation Time {0} - {1}</li></ul>\n'.format(obs_time, station_id))
    if radar_id:
        get_radar_data(radar_id)
        myFile.write('<hr><center><img src="/opennms/includes/radar.gif"></center>\n')
    myFile.write('{0}\n'.format(html_bot))
    myFile.close

if __name__ == '__main__':
    main()
