# Video Queue

The Video Queue is sent the zip packages by the website backend, and moves them to a queue to await processing. When there are packages in the queue, a flag is set that can be read by the processing controller, which is able to request that packages be dequeued and sent to it when there are processing threads available. 

## Zip Package

The package is recieved as a `.zip` file, containing `upload.[mp4/mkv/mov]` and `incident.json`. The `incident.json` file is structured as follows:

```json
{
    location:{
        "word_1":"",
        "word_2":"",
        "word_3":""
    },
    date:{
        "year":1970,
        "month":01,
        "day":01
    },
    time:{
        "hour":0,
        "minutes":0,
        "seconds":0
    },
    vehicle:"[bike/scooter]"
}
```