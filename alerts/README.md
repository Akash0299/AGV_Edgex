# Color Changer
Test app for REST commands. 
Web interface shows a 300x300px colored square on port 5000. 
REST API accepts changes to the color. 
Web interface uses JS and AJAX to auto refresh, reflecting any new updates pushed via the REST API. 

Example: 
Access web page over port 5000
Push REST call: 
Method: PUT
URI: <ip>:5000/api/v1/device/id/changeColor
BODY: 
{
    "color": "orange"
}
