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
debug=False
    
def Debug(text):
    if (debug):
        Domoticz.Log("Debug: "+str(text))


def UpdateCounterSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Counter").Create()
        Debug ("Updating "+SensorName+"("+str(UnitID)+") with value "+str(Value))
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
        Domoticz.Log("Counter ("+str(SensorName)+")")

def UpdateCustomSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Custom").Create()
        Debug ("Updating "+SensorName+"("+str(UnitID)+") with value "+str(Value))
        Devices[UnitID].Update(nValue=0, sValue=str(Value))
        Domoticz.Log("Counter ("+str(SensorName)+")")

def UpdatePercentageSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Percentage").Create()
        Debug ("Updating "+SensorName+"("+str(UnitID)+") with value "+str(Value))
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
        Domoticz.Log("Percentage ("+str(SensorName)+")")

class BasePlugin:
    enabled = False

    def UpdateSensors(self):
        global timestamp

        # Make a get request to get the  data
        response = requests.get(url)

        # Print the status code of the response.
        if (response.status_code==200):
            Debug("Retrieve data:")
            data=response.json()

            # do some debugging
            for key,value in data.items():
                if type(value)==dict:
                    Debug("Key="+key+" = "+str(data[key]["value"])+"(dict)")
                else:
                    Debug("Key="+key+" = "+str(value)+"(str)")

            #Update the sensors

            UpdateCustomSensor("Intensive care-opnames per dag",1,data["intake_intensivecare_ma"]["value"])
            UpdateCustomSensor("Ziekenhuis opnames per dag",2,data["intake_hospital_ma"]["value"])
            UpdateCustomSensor("Positief getest mensen per dag (per 100.000 inwoners)",3,data["infected_people_delta_normalized"]["value"])
            UpdateCustomSensor("Aantal bestmettelijke mensen (per 100.000 inwoners)",4,data["infectious_people_count_normalized"]["value"])
            UpdateCustomSensor("Totaal aantal besmettelijke mensen",5,data["infectious_people_count"]["value"])
            UpdatePercentageSensor("Reproductiegetal (percentage)",6,float(data["reproduction_index"]["value"]*100))
            UpdateCustomSensor("Positief geteste verpleeghuisbewoners per dag",7,data["infected_people_nursery_count_daily"]["value"])
            UpdateCustomSensor("Overleden verpleeghuisbewoners per dag",8,data["deceased_people_nursery_count_daily"]["value"])


            #Update the timestamp to prevent too many requests to the json call
            timestamp=datetime.datetime.now()

        else:
            Domoticz.Log("Error getting coronadashboard date: "+str(response.status_code))





    def __init__(self):
        return

    def onStart(self):
        Debug("onStart called")
        timestamp=datetime.datetime.now()
        self.UpdateSensors()


    def onStop(self):
        Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Debug("onDisconnect called")

    def onHeartbeat(self):
        Debug("onHeartbeat called")

        ElapsedTime=datetime.datetime.now()-timestamp
        if (ElapsedTime.total_seconds()>interval):
            #enough time passed, let's update the sensors
            self.UpdateSensors()
        else:
            #not enough time passed
            Debug("Elapsed time = "+str(ElapsedTime))

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
