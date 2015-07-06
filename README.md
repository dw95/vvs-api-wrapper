**Example**

vvs_efa = VVS_EFA()
connections = vvs_efa.getNextConnections("Hauptbahnhof", "Charlottenplatz", dt.datetime(2015, 7, 7, 7, 20), True)


print connections[0].origin.name
print connections[0].destination.name
print connections[0].time_of_departure.strftime("%d.%m.%Y - %H:%M") + " - " + connections[0].time_of_arrival.strftime("%d.%m.%Y - %H:%M")
print str(connections[0].fare) + "€ / " + str(connections[0].zones) + " Zone(n)"
print ""
for leg in connections[0].legs:
    print leg.time_of_departure.strftime("%H:%M") + " - " + leg.time_of_arrival.strftime("%H:%M") + ": "
    print leg.origin.name + " - " + leg.destination.name + " ("+ leg.line + ")" + "\n"
