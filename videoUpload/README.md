# Video Upload

The video upload directory specifies the site's frontend. The interface consist of two parts - a video upload form, and a heatmap, both of which are directly accessible from the front page.

## Upload Form

The first component to the web page is the form for uploading videos of bikes or e-scooters. As soon as 'Upload Video' is clicked, a form will appear, along with an option for instructions on how to take a video to upload. As soon as the video type, date, time and location are selected (the location may be selected via placing a marker on a map modal which will appear over the form) and the video is chosen,
an option to Submit can be chosen. Once this is done, the video will be passed to the video queue, where it will wait for a free thread to begin processing.

## Heat Map

The second component is the heatmap for displaying speeding data points. The data is first fetched by way of a HTTP GET request to the database and converted from JSON form, while a temporary load message is displayed. Once this is done, the heatmap is visible via another component, with datapoints using the 'location' field of each JS object to determine the coordinates on the map, and their intensity proportional to the recorded speed of each object.
