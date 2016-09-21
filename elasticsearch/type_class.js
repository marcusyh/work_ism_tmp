{
    "INSTANCE_NAME_BE_REPLACED_HERE": {
        "properties" : {
            "sn" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "time" : {
                "format" : "dateOptionalTime",
                "type" : "date"
            },
            "_recv_time" : {
                "format" : "dateOptionalTime",
                "type" : "date"
            },
            "event" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "duration" : {
                "type" : "long"
            },
            "position" : {
                "type" : "long"
            },
            "title" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "clip" : {
                "type" : "long"
            },
            "ip" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "version" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "_type" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "userid" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "firmware" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "_device" : {
                "type" : "string",
                "index": "not_analyzed"
            }
        }
    }
}
