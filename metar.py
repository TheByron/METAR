'''
AUTHOR: Byron Himes
MODIFIED: 30 March 2016
DESCRIPTION: Takes a METAR reading as input and outputs the interpretation (meaning).
FILES: metar.py
'''

import re

# define a dictionary to label the fields dynamically
fields = {}

def getReading():
    # this function prompts the user to enter the metar report string
    # will modify later to provide options for file input or CL input
    reading = input("Enter METAR reading: ").upper()

    # strip the METAR or SPECI report type info
    if ("METAR" or "SPECI") in reading:
        reading = reading[6:]
    return reading

def degreesToDirection(i):
    # This function takes an integer, i, and converts it to the corresponding
    # compass direction, d, where 0 degrees is N for North
    if type(i) == str:
        i = int(i)
    
    if 0 <= i < 11 or 349 <= i < 360:
        d = "N"
    elif 11 <= i < 34:
        d = "NNE"
    elif 34 <= i < 56:
        d = "NE"
    elif 56 <= i < 79:
        d = "ENE"
    elif 79 <= i < 101:
        d = "E"
    elif 101 <= i < 124:
        d = "ESE"
    elif 124 <= i < 146:
        d = "SE"
    elif 146 <= i < 169:
        d = "SSE"
    elif 169 <= i < 191:
        d = "S"
    elif 191 <= i < 214:
        d = "SSW"
    elif 214 <= i < 236:
        d = "SW"
    elif 236 <= i < 259:
        d = "WSW"
    elif 259 <= i < 281:
        d = "W"
    elif 281 <= i < 304:
        d = "WNW"
    elif 304 <= i < 326:
        d = "NW"
    elif 326 <= i < 349:
        d = "NNW"
    return d

def stationID(fText, key, d):
    # Looks for and culls station id information from metar string
    # Format: AAAA (four alpha chars)
    idPattern = re.compile('[A-Z]{4}\s')
    match = re.search(idPattern, fText)
    if match != None:
        d[key] = "\n\t" + match.group()
        return True
    else:
        return False

def dateTime(fText, key, d):
    # Looks for and culls date & time information from metar string
    # Format: DDTTttZ
    # DD = day of the month (01 - 31)
    # TT = hour of the report (00 - 23)
    # tt = minute of the report (00 - 59)
    # Z is a string literal which indicates Zulu time.
    dtPattern = re.compile('([0-3]\d)([0-2]\d[0-5]\d)Z')
    match = re.search(dtPattern, fText)
    
    if match != None:
        toPrint = ""
        mText = match.group()
        day = mText[0:2]
        hour = mText[2:4]
        minute = mText[4:6]
        toPrint += "\n\tDay of Month: " + day
        toPrint += "\n\tTime: " + hour + ":" + minute
        d[key] = toPrint
        return True
    else:
        return False

def reportModifier(fText, key, d):
    # Looks for and culls report modifier information from metar string
    # Values: "AUTO" or "COR"
    modPattern = re.compile('(AUTO|COR)')
    match = re.search(modPattern, fText)
    if match != None:
        d[key] = "\n\t" + match.group()
        return True
    else:
        return False

def windGroup(fText, key, d):
    # Looks for and culls wind group information from metar string
    # Format: dddff(f)GmmmKT_nnnVxxx
    # ddd = wind direction (000 - 369) OR "VRB"
    # ff(f) = wind speed (00-999)
    # G = string literal indicating "Gust"
    # mmm = wind gust speed (000 - 999)
    # KT = string literal indicating "knots"
    # _ = space
    # nnn = lower end of variability range (000 - 359)
    # V = string literal indicating "variable" (haha)
    # xxx = upper end of variability range (000 - 359)

    # try to match the entire field set first
    windPattern = re.compile(
        '((VRB|[0-3]\d{1,2})(\d{2,3})(G\d{2,3})?KT|00000KT)(\s[0-3]\d{1,2}V[0-3]\d{1,2})?'
    )
    match = re.search(windPattern, fText)

    # if found, break it down into its subgroups for easy printing later
    # go left to right, stripping off the information as we get it
    if match != None:
        toPrint = ""
        mText = match.group()

        # retrieve and strip direction info (ddd)
        dirPattern = re.compile('(VRB|[0-3]\d{1,2})')
        dirMatch = re.search(dirPattern, mText)
        if dirMatch != None:
            ddd = dirMatch.group()

            # if ddd is VRB, change it to read "Variable" for the user's ease
            if ddd == "VRB":
                ddd = "Variable"
            toPrint += "\n\tDirection: " + degreesToDirection(int(ddd))
            mText = mText[dirMatch.end()+1:]

        # retrieve and strip wind speed info (ff(f))
        speedPattern = re.compile('(\d{2,3})')
        speedMatch = re.search(speedPattern, mText)
        if speedMatch != None:
            fff = int(speedMatch.group())
            fff *= 1.15 #convert from km to mi
            if fff == 0:
                toPrint += "\n\tSpeed: Calm (none to very light)"
            else:
                toPrint += "\n\tSpeed: " + "%.f" % fff + "mph"
            mText = mText[speedMatch.end()+1:]

        # retrieve and strip wind gust info (Gmmm)           
        gustPattern = re.compile('(G\d{2,3})')
        gustMatch = re.search(gustPattern, mText)
        if gustMatch != None:
            # the G is a literal, so we're only interested in the speed (mmm)
            mmm = int(gustMatch.group()[1:])
            mmm *= 1.15 #convert from km to mi
            toPrint += "\n\tWind gusts of up to " + "%.f" % mmm + "mph"
            mText = mText[gustMatch.end()+1:]

        # strip 'KT' if it is there (it should be there in a valid wind field)
        kt_loc = mText.find("KT")
        if kt_loc > -1:
            mText = mText[kt_loc + 2:]

        # retrieve and strip variable wind range info (nnnVxxx)
        vrbPattern = re.compile('([0-3]\d{1,2}V[0-3]\d{1,2})')
        vrbMatch = re.search(vrbPattern, mText)
        if vrbMatch != None:
            vrb = vrbMatch.group()
            angle1 = vrb[:vrb.find('V')] + " degrees "
            angle2 = vrb[vrb.find('V')+1:] + " degrees "
            toPrint += "\n\tDirection varying from " + angle1 + "to " + angle2
        d[key] = toPrint
        return True
    else:
        return False

def visibilityGroup(fText, key, d):
    # Looks for and culls visibility group information from metar string
    # Format: VVVVVSM
    # VVVVV = whole numbers, fractions, or mixed fractions.
    #     example values:
    #     M 1/4 where M signifies "less than"
    #     4 3/4
    #     1/4
    # SM = literal meaning "Statute Miles"
    visPattern = re.compile(
        'M?(([1-9]\s[1-9]/[1-9])|([1-9]/[1-9])|(\d{1,2}))SM'
    )
    visMatch = re.search(visPattern, fText)
    if visMatch != None:
        toPrint = ""
        mText = visMatch.group()
        mText = mText[:mText.find("SM")]
        m_loc = mText.find("M")
        if m_loc > -1:
            toPrint += "Less than " + mText[m_loc+1:] + " statute miles"
        elif m_loc == -1:
            toPrint += "\n\t" + mText + " statute miles"
        d[key] = toPrint
        return True
    else:
        return False

def runwayVisibilityRange(fText, key, d):
    # Looks for and culls the runway visibility information from metar string
    # 2 Formats: RDD(D)/VVVVFT or RDD(D)/nnnnVxxxxFT
    # R = string literal indicating that the runway number follows next
    # DD = integer indicating the runway number (00-99)
    # D = [R | L | C] indicating runway approach direction.
    # / = string literal to separate runway no. and constant reportable value
    # VVVV = constant reportable value
    # FT = string literal indicating "feet"
    # nnnn = lowest reportable value in feet
    # V = string literal separating lowest and highest values
    # xxxx = highest reportable value in feet
    shortPattern = re.compile('(R\d{2}[CRL]?/\d{4}FT)')
    longPattern = re.compile('(R\d{2}[CRL]?/\d{4}V\d{4}FT)')

    #try to match long pattern first, then short pattern
    longMatch = re.search(longPattern, fText)
    shortMatch = re.search(shortPattern, fText)
    if longMatch == None and shortMatch == None:
        return False
    elif shortMatch != None:
        # get short pattern data
        toString = ""
        mText = shortMatch.group()

        # strip the 'R' from the front of the string
        mText = mText[1:]

        # retrieve and strip DD(D) info
        DD = mText[:mText.find("/")]
        mText = mText[mText.find("/")+1:]
        toString += "\n\tRunway Number: " + DD
        
        # retrieve constant reportable value
        VVVV = mText[:mText.find("FT")]
        toString += "\n\tVisibility constant at: " + VVVV

        # store output string in dictionary
        d[key] = toString
        return True
    
    elif longMatch != None:
        # get long pattern data
        toString = ""
        mText = longMatch.group()

        # strip the 'R' from the front of the string
        mText = mText[1:]

        # retrieve and strip runway number info, DD(D)
        DD = mText[:mText.find("/")]
        mText = mText[mText.find("/")+1:]
        toString += "\n\tRunway Number: " + DD

        # retrieve and strip lowest reportable value, nnnn
        nnnn = mText[:mText.find("V")]
        mText = mText[mText.find("V")+1:]

        # retrieve highest reportable value, xxxx
        xxxx = mText[:mText.find("FT")]
        toString = "\n\tVisibility varying from " + nnnn + "ft - " + xxxx + "ft"

        # store output string in dictionary
        d[key] = toString
        return True

def presentWeather(fText, key, d):
    # Looks for and culls present weather group information from metar string
    # Format: w'w'
    pass

def skyCondition(fText, key, d):
    # Looks for and culls sky condition information from metar string
    # Format: NNNhhh OR VVsss OR SKC|CLR
    # NNN = amount of sky cover (3 letters)
    # hhh = height of sky cover layer
    # VV = string literal indicating "indefinite ceiling"
    # sss = vertical visibility into indefinite ceiling
    # SKC = string literal used by manual stations = "clear skies"
    # CLR = string literal used by automated stations = "clear skies"
    # NOTE: may sky conditions groups may be present in the metar body

    skyPattern = re.compile('[A-Z]{3}\d{3}')
    vertPattern = re.compile('VV\d{3}')
    clearPattern = re.compile('SKC|CLR')
    skyMatches = re.findall(skyPattern, fText)
    vertMatches = re.findall(vertPattern, fText)
    clearMatches = re.findall(clearPattern, fText)
    
    if len(skyMatches) == 0 and len(vertMatches) == 0 and len(clearMatches) == 0:
        return False
    else:
        toString = ""
        for i in skyMatches:
            if i[:3] == "FEW":
                toString += "\n\tFew clouds at "
                toString += str(int(i[3:]) * 100) + "ft"
            elif i[:3] == "SCT":
                toString += "\n\tScattered clouds at "
                toString += str(int(i[3:]) * 100) + "ft"
            elif i[:3] == "BKN":
                toString += "\n\tBroken clouds at "
                toString += str(int(i[3:]) * 100) + "ft"
            elif i[:3] == "OVC":
                toString += "\n\tOvercast at "
                toString += str(int(i[3:]) * 100) + "ft"
        for i in vertMatches:
            toString += "\n\tIndefinite ceiling with visibility up to "
            toString += str(int(i[3:]) * 100) + "ft"
        for i in clearMatches:
            toString += "\n\tClear skies"
        d[key] = toString
        return True

def tempDewPoint(fText, key, d):
    # Looks for and culls temperature and dew point info from METAR (fText)
    # Format: TsT'T'T'sD'D'D'
    # NOTE: temps are reported in degrees celcius
    # T = string literal indicating "temperature"
    # s = sign of the temperature and dew point (1 for - or 0 for -)
    # T'T'T' = temperature (000-999)
    # D'D'D' = dew point temperature (000-999)
    tdPattern = re.compile('T[01]\d{3}[01]\d{3}')
    tdMatch = re.search(tdPattern, fText)
    if tdMatch != None:
        # if temp and dew point is reported, get the information
        toString = ""
        mText = tdMatch.group()

        # strip literal 'T'
        mText = mText[1:]

        # get temperature and its sign, then strip that info from mText
        temp = str(float(mText[1:4])/10)
        if mText[0] == '1':
            toString += "\n\tTemperature: -" + temp + "ºC"
        elif mText[0] == '0':
            toString += "\n\tTemperature: " + temp + "ºC"
        mText = mText[4:]

        # get dew point and its sign
        dp = str(float(mText[1:])/10)
        if mText[0] == '1':
            toString += "\n\tDew Point: -" + dp + "ºC"
        elif mText[0] == '0':
            toString += "\n\tDew Point: " + dp + "ºC"

        # store output in dictionary
        d[key] = toString
        return True
    else:
        return False

# Program entry:
if __name__ == "__main__":

    # get raw metar reading
    metar = getReading()

    # list of ordered dict keys
    keys = [
        "Station ID: ",
        "Date and Time of Report: ",
        "Report Modifier: ",
        "Wind: ",
        "Visibility: ",
        "Runway Visual Range: ",
        "Present Weather: ",
        "Sky Condition: ",
        "Temperature and Dew Point: ",
        "Altimeter: ",
        "Remarks: "
    ]

    fields = {}

    stationID(metar, keys[0], fields)
    dateTime(metar, keys[1], fields)
    reportModifier(metar, keys[2], fields)
    windGroup(metar, keys[3], fields)
    visibilityGroup(metar, keys[4], fields)
    runwayVisibilityRange(metar, keys[5], fields)
    # presentWeather(metar, keys[6], fields) not implemented yet
    skyCondition(metar, keys[7], fields)
    tempDewPoint(metar, keys[8], fields)
    #altimeter(metar, keys[9], fields) not implemented yet
    

    for k in keys:
        if k in fields.keys():
            print(k, fields[k])

x = input("\n\n\t\tPress key to continue")
