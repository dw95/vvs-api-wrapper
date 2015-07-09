# coding: utf-8

import datetime as dt
import requests

class EFA(object):

    def __init__(self):

        pass

    @classmethod
    def convert_name_to_id(cls, name, mobile=False):
        if name.strip() != "": #check if string is empty -> return None
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


            best_point_index = 0

            if len(points) > 1:
                for index, point in enumerate(points):
                    if point["best"] == "1":
                        best_point_index = index
                        break

                return points[best_point_index]["stateless"]

            elif len(points) == 1:
                return points["point"]["stateless"] #if one point found (no array to iterate!) -> directly return

            else:
                return None #no points found -> return None

        else:
            return None


    def get_next_connections(self, origin, destination, datetime, departure, search_by_name = True):

        """Get connections for parameter set:
                origin: name of origin
                destination: name of destination
                time: datetime object of departure/arrival
                departure: boolean --> true: time of departure; false: time of arrival
                search_by_name: boolean --> true: search by name; false: search by id"""

        if search_by_name:
            id_origin = self.convert_name_to_id(origin)
            id_destination = self.convert_name_to_id(destination)
            if id_origin == None:
                raise TypeError('Origin not valid or not found.')
            if id_destination == None:
                raise TypeError('Destination not valid or not found.')

        else:
            id_origin = origin
            id_destination = destination

        request_url = "http://m.vvs.de/jqm/controller/XSLT_TRIP_REQUEST2"

        parameters = {}

        #parameters["genC"] = "1"
        #parameters["itOptionsActive"] = "1"
        #parameters["locationServerActive"] = "1"
        #parameters["ptOptionsActive"] = "1"
        parameters["stateless"] = "1"
        parameters["name_origin"] = id_origin
        parameters["name_destination"] = id_destination
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

        #parameters["includedMeans"] = "checkbox" #does only work when inclMOT_x set
        #parameters["inclMOT_0"] = "1"
        #parameters["inclMOT_1"] = "1"
        #parameters["inclMOT_2"] = "1"
        #parameters["inclMOT_3"] = "1"
        #parameters["inclMOT_4"] = "1"
        #parameters["inclMOT_5"] = "1"
        #parameters["inclMOT_6"] = "1"
        #parameters["inclMOT_7"] = "1"
        #parameters["inclMOT_8"] = "1"
        #parameters["inclMOT_9"] = "1"
        #parameters["inclMOT_10"] = "1"
        #parameters["inclMOT_11"] = "1"
        #parameters["inclMOT_12"] = "1"
        #parameters["inclMOT_13"] = "1"
        #parameters["inclMOT_14"] = "1"
        #parameters["inclMOT_15"] = "1"
        #parameters["inclMOT_16"] = "1"
        #parameters["inclMOT_17"] = "1"

        parameters["outputFormat"] = "JSON"

        #parameters["SpEncId"] = "0"
        #parameters["anySigWhenPerfectNoOtherMatches"] = "1"
        #parameters["convertStopsPTKernel2LocationServer"] = "1"
        #parameters["convertPOIsITKernel2LocationServer"] = "1"
        #parameters["verifyAnyLocViaLocServer"] = "1"
        #parameters["w_objPrefAl"] = "12"
        #parameters["w_regPrefAm"] = "1"
        #parameters["calcOneDirection"] = "1" #if not set, first trip is last trip before date/time for departure, else first trip after date/time
        #parameters["searchLimitMinutes"] = "360"


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


class Trip(object):

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



class Leg(object):

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


class Location(object):

    def __init__(self, name, loc_id, loc_type="any"):
        """type: type of location (station / address / etc.)
           name: full name of location
           id: id of location"""

        self.loc_type = loc_type
        self.name = name
        self.loc_id = loc_id


class Stop(object):

    def __init__(self, name):
        self.id = VVS_EFA.convert_name_to_id(name)
        if self.id == None:
            raise TypeError("Station could not be found.")

    def get_next_connections(self, datetime, departure, limit=20):

        """datetime: datetime object of time & date
           departure: boolean, true -> time of departure, false --> time of arrival
           limit: int, limit of results fetched, default: 20"""

        if self.id != None:

            parameters = {}

            parameters["deleteAssignedStops_dm"] = "1"
            parameters["itOptionsActive"] = "1"
            parameters["limit"] = str(limit)
            parameters["locationServerActive"] = "1"
            parameters["mode"] = "direct"
            parameters["name_dm"] = self.id
            parameters["ptOptionsActive"] = "1"
            parameters["stateless"] = "1"
            parameters["type_dm"] = "stop"
            parameters["useAllStops"] = "1"
            parameters["useRealtime"] = "1"
            parameters["itdTime"] = datetime.strftime("%H%M")
            parameters["itdDate"] = datetime.strftime("%Y%m%d")

            if departure:
                parameters["itdTripDateTimeDepArr"] = "dep"
            else:
                parameters["itdTripDateTimeDepArr"] = "arr"

            parameters["outputFormat"] = "JSON"
            parameters["SpEncId"] = "0"
            parameters["anySigWhenPerfectNoOtherMatches"] = "1"
            parameters["convertStopsPTKernel2LocationServer"] = "1"
            parameters["convertPOIsITKernel2LocationServer"] = "1"
            parameters["verifyAnyLocViaLocServer"] = "1"
            parameters["w_objPrefAl"] = "12"
            parameters["w_regPrefAm"] = "1"

            request_url = "http://m.vvs.de/jqm/controller/XSLT_DM_REQUEST"
            req = requests.post(request_url, parameters)
            data = req.json()

            departure_list = data["departureList"]
            connections = []
            for list_entry in departure_list:
                serving_line_data = list_entry["servingLine"]
                serving_line = ServingLine(serving_line_data["key"], serving_line_data["number"], serving_line_data["direction"],
                                           serving_line_data["directionFrom"], serving_line_data["name"])

                stop_id = list_entry["stopID"]
                stop_name = list_entry["stopName"]
                scheduled_datetime = dt.datetime(int(list_entry["dateTime"]["year"]), int(list_entry["dateTime"]["month"]),
                                                 int(list_entry["dateTime"]["day"]), int(list_entry["dateTime"]["hour"]), int(list_entry["dateTime"]["minute"]))

                try: #check if realtime info available
                    realtime_datetime = dt.datetime(int(list_entry["realDateTime"]["year"]), int(list_entry["realDateTime"]["month"]),
                                                    int(list_entry["realDateTime"]["day"]), int(list_entry["realDateTime"]["hour"]), int(list_entry["realDateTime"]["minute"]))

                except: #if not: return None for realtime_datetime
                    realtime_datetime = None

                connection = Connection(stop_id, stop_name, scheduled_datetime, realtime_datetime, serving_line)
                connections.append(connection)

            return connections

        else:
            return None



class Connection(object):
    """docstring for Connection"""
    def __init__(self, stop_id, stop_name, scheduled_datetime, realtime_datetime, serving_line):
        """realtime_datetime: datetime object of projected departure/arrival. None if not available"""
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.scheduled_datetime = scheduled_datetime
        self.realtime_datetime = realtime_datetime
        self.serving_line = serving_line


class ServingLine(object):
    """docstring for ServingLine"""
    def __init__(self, key, number, direction, direction_from, line_type):
        self.key = key
        self.number = number
        self.direction = direction
        self.direction_from = direction_from
        self.line_type = line_type
