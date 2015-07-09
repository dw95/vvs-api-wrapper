##VVS API Wrapper

This was created for easy access to the VVS EFA (Elektronische Fahrplanauskunft) in Python.

### Example

```python
# coding: utf-8
import datetime as dt
from vvs_efa import VVS_EFA

vvs_efa = VVS_EFA.EFA()
connections = vvs_efa.getNextConnections("Stadtbibliothek", "Feuersee", dt.datetime(2015, 7, 7, 7, 20), True)


print connections[0].origin.name
print connections[0].destination.name
print connections[0].time_of_departure.strftime("%d.%m.%Y - %H:%M") + " - " + connections[0].time_of_arrival.strftime("%d.%m.%Y - %H:%M")
print str(connections[0].fare) + "€ / " + str(connections[0].zones) + " Zone(n)"
print ""
for leg in connections[0].legs:
    print leg.time_of_departure.strftime("%H:%M") + " - " + leg.time_of_arrival.strftime("%H:%M") + ": "
    print leg.origin.name + " - " + leg.destination.name + " ("+ leg.line + ")" + "\n"


charlottenplatz = VVS_EFA.Stop("Charlottenplatz")
charlottenplatz_departures = charlottenplatz.get_next_connections(dt.datetime(2015, 7, 9, 18, 10), True)

print charlottenplatz_departures[0].stop_id
print charlottenplatz_departures[0].stop_name
print charlottenplatz_departures[0].scheduled_datetime.strftime("%d.%m.%Y - %H:%M")
print charlottenplatz_departures[0].realtime_datetime.strftime("%d.%m.%Y - %H:%M")
print charlottenplatz_departures[0].serving_line.key
print charlottenplatz_departures[0].serving_line.number
print charlottenplatz_departures[0].serving_line.direction
print charlottenplatz_departures[0].serving_line.direction_from
print charlottenplatz_departures[0].serving_line.line_type

```

results in:

```
Stuttgart, Stadtbibliothek
Stuttgart, Feuersee
06.07.2015 - 07:20 - 06.07.2015 - 07:31
2.3€ / 2 Zone(n)
07:20 - 07:22: Stadtbibliothek - Hauptbf (A.-Klett-Pl.) (U12)
07:24 - 07:28: Hauptbf (Arnulf-Klett-Platz) - Stuttgart Hauptbahnhof (tief) ()
07:28 - 07:31: Stuttgart Hauptbahnhof (tief) - Feuersee (S6)

5006075
Charlottenplatz
09.07.2015 - 18:05
09.07.2015 - 18:11
143
43
Feuersee
Killesberg
Bus
```
