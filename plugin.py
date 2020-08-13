#Covid 19 dashboardp plugin by akamming
"""
<plugin key="COVID19NL" name="Dashboard coronavirus NL" author="akamming" version="1.0.0" wikilink="https://github.com/akamming/domoticz-coronadashboard" externallink="https://coronadashboard.rijksoverheid.nl/json/NL.json">
    <description>
        <h2>Dashboard coronavirus NL</h2><br/>
        <br/>
        Experimental: Loads the counters of the NL corona dashboard into domoticz sensors<br/>
        <br/>
        <h3>Configuration</h3>
        Interval Connfigures the number of seconds between calls.<br/>
        <br/>
        If you want to local data from your safety region(s), enter the id's from 1 or more (comma seperated) safety regions. You can find the id's of the safety regions at the <a href="https://www.rijksoverheid.nl/onderwerpen/veiligheidsregios-en-crisisbeheersing/veiligheidsregios">website of the Rijksoverheid</a><br/>
        <br/> 
        for example: 
        <ul style="list-style-type:square">
            <li>specifying "1" will create sensors for safety region Gronigen</li>
            <li>"1,3,5" will create sensor for Groningen(1), Drenthe(3) and Noord en Oost Gelderland(5).. </li>
            <li>leaving empty will create no sensors for individual safety regions.</li>
        </ul>
        <br/>
        Please bear in mind that every safety region requires an extra call to the API, so a low interval with a lot of safety regions will spam the rijksoverheid dashboard!<br/><br/><br/>
    </description>
    <params>
        <param field="Mode1" label="Interval" width="150px" required="false" default="3600" />
        <param field="Mode2" label="Safety Region(s)" width="300px" default="" />
    </params>
</plugin>
"""
import Domoticz
import datetime
import requests
import json

#global vars
timestamp=datetime.datetime.now()
LastDashboardUpdate=0
mininterval=900 #if interval specified below this value, revert to default interval (see next line)
interval=3600  #time in seconds between measurements
dashboardurl="https://coronadashboard.rijksoverheid.nl/json/NL.json" #url of the json
safetyregionurlprefix="https://coronadashboard.rijksoverheid.nl/json/VR"
safetyregionurlpostfix=".json"
debug=True
SafetyRegions=[]
    
def Debug(text):
    if (debug):
        Domoticz.Log("Debug: "+str(text))


def UpdateCustomSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Custom").Create()
        Debug ("Updating "+Devices[UnitID].Name+"("+str(UnitID)+","+Devices[UnitID].sValue+") with value ["+str(Value)+"]")
        Devices[UnitID].Update(nValue=0, sValue=str(Value))
        Domoticz.Log("Counter ("+Devices[UnitID].Name+")")

def UpdatePercentageSensor(SensorName,UnitID,Value):
       #Creating devices in case they aren't there...
        if not (UnitID in Devices):
            Debug("Creating device "+SensorName)
            Domoticz.Device(Name=SensorName, Unit=UnitID, TypeName="Percentage").Create()
        Debug ("Updating "+Devices[UnitID].Name+"("+str(UnitID)+") with value "+str(Value))
        Devices[UnitID].Update(nValue=int(Value), sValue=str(Value))
        Domoticz.Log("Percentage ("+Devices[UnitID].Name+")")

class BasePlugin:
    enabled = False

    def UpdateSensors(self):
        global timestamp
        global LastDashboardUpdate

        # Make a get request to get the  data
        Debug("Retrieving global json data from dashboard")
        response = requests.get(dashboardurl)

        # Print the status code of the response.
        if (response.status_code==200):
            #Parse the json
            data=response.json()

            #do some debugging
            for key,value in data.items():
                if type(value)==dict:
                    #Debug("Key="+key+" = "+str(data[key]["value"])+"(dict)")
                    Debug("Key="+key+" = (dict)")
                else:
                    Debug("Key="+key+" = "+str(value)+"(str)")

            LastUpdate=int(data["last_generated"])

            Debug("Last updated : "+str(datetime.datetime.fromtimestamp(LastUpdate)))

            if (LastUpdate>LastDashboardUpdate):
                Debug("LastUpdate("+str(LastUpdate)+") > LastDashboardUpdate("+str(LastDashboardUpdate)+"), updating sensors...")
                Domoticz.Log("New data available at dashboard, updating sensors...")

                #Update the sensors
                UpdateCustomSensor("Intensive care-opnames per dag",1,data["intake_intensivecare_ma"]["last_value"]["moving_average_ic"])
                UpdateCustomSensor("Ziekenhuis opnames per dag",2,data["intake_hospital_ma"]["last_value"]["moving_average_hospital"])
                UpdateCustomSensor("Positief getest mensen per dag (per 100.000 inwoners)",3,data["infected_people_delta_normalized"]["last_value"]["infected_daily_increase"])
                UpdateCustomSensor("Aantal bestmettelijke mensen (per 100.000 inwoners)",4,data["infectious_people_count_normalized"]["last_value"]["infectious_avg_normalized"])
                UpdateCustomSensor("Totaal aantal besmettelijke mensen",5,data["infectious_people_count"]["last_value"]["infectious_avg"])
                if (data["reproduction_index"]["last_value"]["reproduction_index_avg"]==None):
                    Debug("reproduction index = none")
                else:
                    UpdatePercentageSensor("Reproductiegetal (percentage)",6,float(data["reproduction_index"]["last_value"]["reproduction_index_avg"])*100)
                UpdateCustomSensor("Positief geteste verpleeghuisbewoners per dag",7,data["infected_people_nursery_count_daily"]["last_value"]["infected_nursery_daily"])
                UpdateCustomSensor("Overleden verpleeghuisbewoners per dag",8,data["deceased_people_nursery_count_daily"]["last_value"]["deceased_nursery_daily"])

                #Update SafetyRegionSensors
                if len(SafetyRegions)>0:
                    for SafetyRegion in SafetyRegions:
                        if len(SafetyRegion)==0: 
                            region=0
                        else:
                            region=int(SafetyRegion)

                        if region>0:
                            # Get json data
                            Debug("Getting json for Safety Region "+str(region))
                            if (region<10):
                                Debug("region<10, adding an extra 0 to url and prefix")
                                response = requests.get(safetyregionurlprefix+"0"+str(region)+safetyregionurlpostfix)
                                prefix="VR0"+str(region)+" "
                            else:
                                response = requests.get(safetyregionurlprefix++str(region)+safetyregionurlpostfix)
                                prefix="VR"+str(region)+" "

                            if (response.status_code==200):
                                #Parse the json
                                data=response.json()

                                # do some debugging
                                for key,value in data.items():
                                    if type(value)==dict:
                                        Debug("Key="+key+" = (dict)")
                                    else:
                                        Debug("Key="+key+" = "+str(value)+"(str)")

                                #Update the sensors
                                #UpdateCustomSensor(prefix+"Intensive care-opnames per dag",region*9+1,data["intake_intensivecare_ma"]["value"])
                                UpdateCustomSensor(prefix+"Ziekenhuis opnames per dag",region*9+2,data["intake_hospital_ma"]["last_value"]["intake_hospital_ma"])
                                UpdateCustomSensor(prefix+"Positief getest mensen per dag (per 100.000 inwoners)",region*9+3,data["infected_people_delta_normalized"]["last_value"]["infected_people_delta_normalized"])
                                #UpdateCustomSensor(prefix+"Aantal bestmettelijke mensen (per 100.000 inwoners)",region*9+4,data["infectious_people_count_normalized"]["value"])
                                #UpdateCustomSensor(prefix+"Totaal aantal besmettelijke mensen",region*9+5,data["infectious_people_count"]["value"])
                                #UpdatePercentageSensor(prefix+"Reproductiegetal (percentage)",region*9+6,float(data["reproduction_index"]["value"]*100))
                                #UpdateCustomSensor(prefix+"Positief geteste verpleeghuisbewoners per dag",region*9+7,data["infected_people_nursery_count_daily"]["value"])
                                #UpdateCustomSensor(prefix+"Overleden verpleeghuisbewoners per dag",region*9+8,data["deceased_people_nursery_count_daily"]["value"])
                                
                                
                            else:
                                Debug("Error retrieving data for region "+SafetyRegion+"("+response.status_code+")")
                        else:
                            Debug("Unable to proces region "+SafetyRegion)
                else:
                    Debug("No safetyregions to process")

                LastDashboardUpdate=LastUpdate #Record the timestamp of the data to prevent double updates...
            else:
                Debug("LastUpdate("+str(LastUpdate)+") < LastDashboardUpdate("+str(LastDashboardUpdate)+"), not updating sensors...")
        else:
            Domoticz.Log("Error getting coronadashboard date: "+str(response.status_code))


    def __init__(self):
        return

    def onStart(self):
        global SafetyRegions
        global interval

        Debug("onStart called")
        #Get interval from var
        if(len(Parameters["Mode1"])>0):
            if int(Parameters["Mode1"])<mininterval:
                interval=mininterval
                Domoticz.Log("Error: Configured interval below minimum interval: leaving at minimum ("+str(interval)+")")
            else:
                interval=int(Parameters["Mode1"])
                Debug("Interval was changed to "+str(interval))
        else:
                Debug("interval not configured: leaving at default ("+str(interval)+")")
            

        #Get SafetyRegions from config
        SafetyRegions=Parameters["Mode2"].split(',')
        if (len(SafetyRegions)==0):
            Debug("Unable to read saferty regions")
        else:
            for SafetyRegion in SafetyRegions:
                Debug("Safety Region "+str(SafetyRegion)+" was read from config")

        ## Update Sensors at start
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
        global timestamp

        Debug("onHeartbeat called")

        ElapsedTime=datetime.datetime.now()-timestamp
        Debug("Elapsed Time in seconds="+str(ElapsedTime.total_seconds()))
        if (ElapsedTime.total_seconds()>(interval-1)):   #correct for 1 second (processing time for the heartbeat)
            #enough time passed, let's update the sensors
            self.UpdateSensors()

            #Update the timestamp to prevent too many requests to the json call
            timestamp=datetime.datetime.now()
        #else:
            #not enough time passed

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
