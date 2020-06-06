#Covid 19 dashboardp plugin by akamming
"""
<plugin key="COVID19NL" name="Dashboard coronavirus NL" author="akamming" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://coronadashboard.rijksoverheid.nl/json/NL.json">
    <description>
        <h2>Dashboard coronavirus NL</h2><br/>
        <br/>
        Experimental: Loads the counters of the NL corona dashboard into domoticz sensors
    </description>
    <params>
    </params>
</plugin>
"""
import Domoticz
import datetime
import requests
import json

#global vars
timestamp=datetime.datetime.now()
interval=3600  #time in seconds between measurements
url="https://coronadashboard.rijksoverheid.nl/json/NL.json" #url of the json
debug=True
    
def Debug(text):
    if (debug):
        Domoticz.Log("DEBUG: "+str(text))


def UpdateCounterSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Counter").Create()
        Debug ("Updating "+SensorName+"("+str(UnitID)+") with value "+str(Value))
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))

class BasePlugin:
    enabled = False

    def UpdateSensors(self):
        # Make a get request to get the  data
        response = requests.get(url)

        # Print the status code of the response.
        if (response.status_code==200):
            Debug("Retrieve data:")
            data=response.json()
            for key,value in data.items():
                if type(value)==dict:
                    Debug("Key="+key+" = "+str(data[key]["value"])+"(dict)")
                else:
                    Debug("Key="+key+" = "+str(value)+"(str)")
        else:
            Domoticz.Log("Error getting coronadashboard date: "+str(response.status_code))

        UpdateCounterSensor("Intensive care-opnames per dag",1,data["intake_intensivecare_ma"]["value"])




    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        timestamp=datetime.datetime.now()
        self.UpdateSensors()


    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.UpdateSensors()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
