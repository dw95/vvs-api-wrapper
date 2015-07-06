# coding: utf-8

import datetime as dt
import requests

class VVS_EFA:

    def __init__(self):

        pass

    @classmethod
    def convertNameToId(cls, name, mobile=False):

        if mobile:
            request_url = "http://m.vvs.de/jqm/controller/XSLT_STOPFINDER_REQUEST"
            parameters = {}
            parameters["name_sf"] = name
            parameters["language"] = "de"
            parameters["stateless"] = "1"
            parameters["locationServerActive"] = "1"
            parameters["anyObjFilter_sf"] = "0"
            parameters["anyMaxSizeHitList"] = "500"
            parameters["outputFormat"] = "JSON"
            parameters["SpEncId"] = "0"
            parameters["type_sf"] = "any"
            parameters["anySigWhenPerfectNoOtherMatches"] = "1"
            parameters["convertAddressesITKernel2LocationServer"] = "1"
            parameters["convertCoord2LocationServer"] = "1"
            parameters["convertCrossingsITKernel2LocationServer"] = "1"
            parameters["convertStopsPTKernel2LocationServer"] = "1"
            parameters["convertPOIsITKernel2LocationServer"] = "1"
            parameters["tryToFindLocalityStops"] = "1"
            parameters["w_objPrefAl"] = "12"
            parameters["w_regPrefAm"] = "1"

        else:
            request_url = "http://www2.vvs.de/vvs/XSLT_STOPFINDER_REQUEST"
            parameters = {}
            parameters["suggest_macro"] = "vvs"
            parameters["name_sf"] = name

        req = requests.post(request_url, parameters)

        points = req.json()["stopFinder"]["points"]

        max_quality = 0
        max_quality_index = 0
        best_point_index = 0

        for index, point in enumerate(points):

            if point["quality"] > max_quality:
                max_quality = point["quality"]
                max_quality_index = index

            if point["best"] == "1":
                best_point_index = index

        #print points[max_quality_index]["stateless"] #highest quality rating (only stops)
        #name + ": " + points[best_point_index]["stateless"] #vvs best ranked (best attribute set to true)

        return points[best_point_index]["stateless"]


    def getNextConnections(self, origin, destination, datetime, departure):

        """Get connections for parameter set:
                origin: name of origin
                destination: name of destination
                time: datetime object of departure/arrival
                departure: boolean --> true: time of departure; false: time of arrival"""

        request_url = "http://m.vvs.de/jqm/controller/XSLT_TRIP_REQUEST2"

        parameters = {}

        parameters["genC"] = "1"
        parameters["itOptionsActive"] = "1"
        parameters["locationServerActive"] = "1"
        parameters["ptOptionsActive"] = "1"
        parameters["stateless"] = "1"
        parameters["name_origin"] = VVS_EFA.convertNameToId(origin)
        parameters["name_destination"] = VVS_EFA.convertNameToId(destination)
        parameters["type_destination"] = "any"
        parameters["type_origin"] = "any"
        parameters["use_realtime"] = "1"
        parameters["itdTime"] = datetime.strftime("%H%M") #"2105"
        parameters["date"] = datetime.strftime("%Y%m%d")  #"20141216"

        if departure:
            parameters["itdTripDateTimeDepArr"] = "dep"
        else:
            parameters["itdTripDateTimeDepArr"] = "arr"

        parameters["routeType"] = "LEASTTIME"
        parameters["changeSpeed"] = "normal"
        parameters["includedMeans"] = "checkbox"
        parameters["inclMOT_0"] = "1"
        parameters["inclMOT_1"] = "1"
        parameters["inclMOT_2"] = "1"
        parameters["inclMOT_3"] = "1"
        parameters["inclMOT_4"] = "1"
        parameters["inclMOT_5"] = "1"
        parameters["inclMOT_6"] = "1"
        parameters["inclMOT_7"] = "1"
        parameters["inclMOT_8"] = "1"
        parameters["inclMOT_9"] = "1"
        parameters["inclMOT_10"] = "1"
        parameters["inclMOT_11"] = "1"
        parameters["inclMOT_12"] = "1"
        parameters["inclMOT_13"] = "1"
        parameters["inclMOT_14"] = "1"
        parameters["inclMOT_15"] = "1"
        parameters["inclMOT_16"] = "1"
        parameters["inclMOT_17"] = "1"
        parameters["outputFormat"] = "JSON"
        parameters["SpEncId"] = "0"
        parameters["anySigWhenPerfectNoOtherMatches"] = "1"
        parameters["convertStopsPTKernel2LocationServer"] = "1"
        parameters["convertPOIsITKernel2LocationServer"] = "1"
        parameters["verifyAnyLocViaLocServer"] = "1"
        parameters["w_objPrefAl"] = "12"
        parameters["w_regPrefAm"] = "1"
        parameters["calcOneDirection"] = "1"
        parameters["searchLimitMinutes"] = "360"


        req = requests.post(request_url, parameters)

        data = req.json()
        trips = data["trips"]
        trip_objs = []

        if trips != None:
            for trip in trips:
                #Trip attributes
                #trip_duration = trip["duration"]
                trip_fare = float(trip["itdFare"]["fares"]["fare"]["fareAdult"])
                trip_zones = abs(int(trip["itdFare"]["tariffZones"]["tariffZone"]["toPR"]) - int(trip["itdFare"]["tariffZones"]["tariffZone"]["fromPR"]))
                trip_origin = Location(name = data["origin"]["points"]["point"]["name"], loc_id = data["origin"]["points"]["point"]["stateless"], loc_type = data["origin"]["points"]["point"]["anyType"])
                trip_destination = Location(name = data["destination"]["points"]["point"]["name"], loc_id = data["destination"]["points"]["point"]["stateless"], loc_type = data["destination"]["points"]["point"]["anyType"])

                #print "Dauer: %s \nPreis: %s\n" % (trip_duration, trip_fare)

                trip_legs = []
                for leg in trip["legs"]:
                    origin = Location(name=leg["points"][0]["name"], loc_id=leg["points"][0]["ref"]["id"])
                    destination = Location(name=leg["points"][1]["name"], loc_id=leg["points"][1]["ref"]["id"])

                    origin_realtime_date = leg["points"][0]["dateTime"]["rtDate"] #17.12.2014
                    origin_realtime_time = leg["points"][0]["dateTime"]["rtTime"] #16:35

                    destination_realtime_date = leg["points"][1]["dateTime"]["rtDate"]
                    destination_realtime_time = leg["points"][1]["dateTime"]["rtTime"]

                    origin_departure_real_datetime = dt.datetime.strptime(origin_realtime_date + "-" + origin_realtime_time, "%d.%m.%Y-%H:%M")
                    destination_arrival_real_datetime = dt.datetime.strptime(destination_realtime_date + "-" + destination_realtime_time, "%d.%m.%Y-%H:%M")

                    duration = leg["timeMinute"]
                    mode = leg["mode"]["product"]
                    line = leg["mode"]["number"]
                    direction = leg["mode"]["destination"]

                    l = Leg(origin, destination, origin_departure_real_datetime, destination_arrival_real_datetime, mode, line, direction)

                    trip_legs.append(l)

                    #print "%s-%s: (%s min)\n     %s - %s" %(origin_departure_real_time, destination_arrival_real_time, duration, origin, destination)


                trip_time_of_departure = trip_legs[0].time_of_departure
                trip_time_of_arrival = trip_legs[-1].time_of_arrival

                trip_obj = Trip(trip_origin, trip_destination, trip_time_of_departure, trip_time_of_arrival, trip_legs, trip_fare, trip_zones)
                trip_objs.append(trip_obj)

        else:
            print "No trips found."


        return trip_objs


class Trip:

    def __init__(self, origin, destination, time_of_departure, time_of_arrival, legs, fare, zones):
        """origin:            location object of origin
           destination:       location object of destination
           time_of_departure: datetime object of trip departure time / date
           time_of_arrival:   datetime object of trip arrival time / date
           legs:              list of Leg objects
           fare:              fare of trip (float)
           zones:             number of zones travelled (int)"""

        self.origin = origin
        self.destination = destination
        self.time_of_departure = time_of_departure
        self.time_of_arrival = time_of_arrival
        self.legs = legs
        self.fare = fare
        self.zones = zones



class Leg:

    def __init__(self, origin, destination, time_of_departure, time_of_arrival, mode, line, direction):
        """origin:            leg origin (station / address / etc.)
           destination:       leg destination (station / address / etc.)
           time_of_departure: departure datetime object
           time_of_arrival:   arrival datetime object
           mode:              mode of transportation (U-Bahn / S-Bahn / Bus / Walking)
           line:              U-Bahn / S-Bahn / Bus Line
           direction:         ulitmate destination of U-Bahn / S-Bahn / Bus Line"""

        self.origin = origin
        self.destination = destination
        self.time_of_departure = time_of_departure
        self.time_of_arrival = time_of_arrival
        self.mode = mode
        self.line = line
        self.direction = direction


class Location:

    def __init__(self, name, loc_id, loc_type="any"):
        """type: type of location (station / address / etc.)
           name: full name of location
           id: id of location"""

        self.loc_type = loc_type
        self.name = name
        self.loc_id = loc_id
