# weather.py

[OpenNMS](http://opennms.org) is the world’s first enterprise grade network management application platform developed under the open source model. This python script will display weather data on the OpenNMS home page.

## Install
1. Edit `weather.py` add your weather station id (https://forecast.weather.gov/stations.php)
2. Edit `weather.py` add your weather zone id (you will receive alerts for this zone - https://www.weather.gov/pimar/PubZone) 
3. Copy `weather.py` to `/opt/opennms/bin`
4. Create a cronjob that will run the `weather.py` script `*/10 * * * * /bin/python /opt/opennms/bin/weather.py > /dev/null 2>&1`
5. Edit `/opt/opennms/jetty-webapps/opennms/index.jsp` and add the below block of code to the appropriate column.
```
<!-- weather box -->
<jsp:include page="/includes/weather.jsp" flush="false" />
```
To add the weather panel to the top of the right column the code would look like
```
<!-- Right Column -->
        <div class="col-md-3" id="index-contentright">
                <!-- weather box -->
                <jsp:include page="/includes/weather.jsp" flush="false" />
```
## Screenshot
![weather.py screenshot](https://raw.githubusercontent.com/jeremyfo/opennms-weather-v2/master/SCREENSHOT.PNG)

## Issues
This script has been tested against the latest versions of OpenNMS Horizon and Meridian. After each OpenNMS upgrade you will need to add the code block back to `index.jsp`

Please report issues on the issue tracker or contact jeremyfo@gmail.com

## FAQ
