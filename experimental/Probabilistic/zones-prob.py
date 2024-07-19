import math
import random
import array
import sys
import time

import pcb_tools as pcb
import pcb_tools.primitives as pcb_primitive
import primitives as glif
import gerber_writer

primitives=[]

g=gerber_writer.gerber_writer("labels.gbr")

print("""
%MOMM*%
%FSLAX36Y36*%
%LPD*%
""")

def rescale(value):
    return value


#======================
# classical zone plate 
#======================

def zoneplate(wavelength, focallength, zones, feature_limit, size_limit, origpen, name, number, center_dot=True):
    print("%AM{}*".format(name))
    print("0 {}zone plate zones={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(("inverse " if origpen==0 else ""), zones, feature_limit, size_limit, wavelength, focallength, name, number))
    # determine first zone that is viable according to limits
    pen = origpen
    for zone in range(zones, 3, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        feature = radius-radius2
        size= radius*2
        if feature>=feature_limit: # and size<=size_limit: 
            start = zone
            total_diameter = size
            smallest_feature=feature
            break
        pen = 1-pen
    if origpen==1: 
        if start%2==0:
            start -= 1
    else: 
        if start%2==1:
            start -= 1

    print("0 pen is {} starting zone is {} with feature size {:.6f} and diameter {:.6f}*"
          .format(pen, start, feature, total_diameter))

    pen = 1
    for zone in range(start, 1, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("1,{},{:6f},0,0,0*".format(pen,rescale(diameter)))
        pen = 1-pen

    # print center dot
    if origpen==1 and center_dot: 
        print("0 zone 0 center*".format(focallength))
        zone = 1
        radius =math.sqrt(zone*wavelength*focallength
                        + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("1,1,{:6f},0,0,0*".format(rescale(diameter)))

    print("%")

    print()
    # print("%TAfocal_length,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_feature)

#=======================
# pinhole sieve 
#=======================

def sieve(wavelength, focallength, zones, feature_limit, size_limit, name, number, center_dot=True, divisor=3):
    """ This doesn't invoke enough Fresnel diffraction """
    print("%AM{}*".format(name))

    print("0 pinhole sieve max_zones={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(zones, feature_limit, size_limit, wavelength, focallength, name, number))

    # determine first zone that is viable according to limits
    for zone in range(zones, 1, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        feature = radius-radius2
        size = 2*radius
        if feature>=feature_limit and size<=size_limit:
            start = zone
            total_diameter = size
            smallest_feature = feature
            break
    if start % 2 == 0:  # make odd
        start -= 1
    print("0 starting zone is {} with feature size {:.6f} and diameter {:.6f}*"
          .format(start, feature, total_diameter))

    for zone in range(start,1,-2): 
        radius1 =math.sqrt(zone*wavelength*focallength 
                         + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                         + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        # want the circles inside a zone, centered, and filling the zone
        diameter = radius1-radius2
        center = (radius2+radius1)/2
        circles = int(center*2*math.pi / (divisor*diameter)) 
        angle_increment = 2*math.pi/circles
        total_area = math.pi*(diameter/2)*(diameter/2)*circles
        print("0 zone {} center={:.6f} diameter={:.6f} divisor={} circles={} angle={:.6f} area={:.6f}*"
              .format(zone, center, diameter, divisor, circles, angle_increment, total_area))
        for dot in range(0, circles): 
            x = math.cos(dot*angle_increment)*center
            y = math.sin(dot*angle_increment)*center
            print("1,1,{:6f},{:6f},{:6f},0*".format(rescale(diameter), rescale(x), rescale(y)))

    # print center dot
    if (center_dot): 
        print("0 zone 0 center*".format(focallength))
        zone = 1
        radius =math.sqrt(zone*wavelength*focallength
                        + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("1,1,{:6f},0,0,0*".format(rescale(diameter)))

    print("%")

    print()
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_feature)


#===============================
# inverse sieve, even harmonics
#===============================

def inverse_sieve(wavelength, focallength, zones, feature_limit, size_limit, name, number):
    print("%AM{}*".format(name))
    print("0 inverse sieve zones={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(zones, feature_limit, size_limit, wavelength, focallength, name, number))

    # determine first zone that is viable according to limits
    for zone in range(zones, 1, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        feature = radius-radius2
        size = 2*radius
        if feature>=feature_limit and size<=size_limit: 
            start = zone
            total_diameter = size
            smallest_feature = feature
            break
    if start % 2 != 0:  # make even
        start -= 1
    print("0 starting zone is {} with feature size {:.6f} and diameter {:.6f}*"
          .format(start, feature, total_diameter))

    for zone in range(start,1,-2): 
        total_area=0
        radius1 =math.sqrt(zone*wavelength*focallength 
                         + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                         + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        # want the circles inside a zone, centered, and filling the zone
        diameter = radius1-radius2
        center = (radius2+radius1)/2
        circles = int(center*2*math.pi / (3*diameter)) 
        angle_increment = 2*math.pi/circles
        total_area = math.pi*(diameter/2)*(diameter/2)*circles
        print("0 zone {} center={:.6f} diameter={:.6f} circles={} angle increment={:.6f} area={:.6f}*"
              .format(zone, center, diameter, circles, angle_increment, total_area))
        for dot in range(0, circles): 
            x = math.cos(dot*angle_increment)*center
            y = math.sin(dot*angle_increment)*center
            print("1,1,{:6f},{:6f},{:6f},0*".format(rescale(diameter), rescale(x), rescale(y)))

    print("%")

    print()
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_feature)


#============================
# probabilistic zone sieve 
#============================

def prob(wavelength, focallength, zones, diameter_limit, size_limit, macro_limit, name, number, center_dot=True):
    print("%AM{}*".format(name))

    print("0 prob max_zones={} diameter_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(zones, diameter_limit, size_limit, wavelength, focallength, name, number))

    # determine first zone that is viable according to limits
    start=zones
    total_diameter=0
    smallest_diameter=0
    for zone in range(zones, 1, -1): 
        radius1 =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        diameter = radius1-radius2
        size = 2*radius1
        if diameter>=diameter_limit and size<=size_limit:
            start = zone
            total_diameter = size
            smallest_diameter = diameter
            break
    if start % 2 == 0:  # make odd
        start -= 1
    print("0 outer zone is {} with feature diameter {:.6f} and total diameter {:.6f}*"
          .format(start, diameter, total_diameter))

    # create usage maps for eligible zones
    radius1 = {}
    radius2 = {}
    center = {}
    diameter = {}
    size = {}
    cells = {}
    mapper = {}
    for zone in range(start, 1, -2):
        radius1[zone] =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2[zone] =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        center[zone] = (radius1[zone]+radius2[zone])/2
        diameter[zone] = radius1[zone]-radius2[zone]
        size[zone] = 2*radius1[zone]
        cells[zone] = int(2*math.pi*center[zone]/diameter[zone])
        print("0 cells[{}]={}".format(zone, cells[zone]))
        mapper[zone] = array.array('b', [0]*cells[zone])
        

    for trial in range(0,macro_limit): 
        zone = random.randrange(start, 1, -2)
        # want the circles inside a zone, centered, and filling the zone
        angle = random.uniform(0,2*math.pi)
        target = int(angle*center[zone]/diameter[zone]) % cells[zone]
        # we want the cell to be at least one diameter = 2 steps from the target. 
        # (*)( )(*)( )(*)
        inc = True
        for t in range(target-2, target+3):
            if mapper[zone][(t+cells[zone])%cells[zone]]:
                inc=False
                break
        if inc: 
            # print("0 zone {} center={:.6f} radius={:.6f} angle={:.6f} target={}*"
            #       .format(zone, center, (radius1[zone]-radius2[zone])/2, angle, target))
            mapper[zone][target]=1
            radians = angle
            x = math.cos(angle)*center[zone]
            y = math.sin(angle)*center[zone]
            print("1,1,{:6f},{:6f},{:6f},0*".format(rescale(diameter[zone]), rescale(x), rescale(y)))

        else: 
            pass
            # print("0 zone {} center={:.6f} radius={:.6f} angle={:.6f} target={} REJECTED*"
            #       .format(zone, center, (radius1[zone]-radius2[zone])/2, angle, target))
    # print center dot
    if (center_dot): 
        print("0 zone 0 center*".format(focallength))
        zone = 1
        radius =math.sqrt(zone*wavelength*focallength
                        + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("1,1,{:6f},0,0,0*".format(rescale(diameter)))

    print("%")

    print()
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_diameter,{:.6f}*%".format(smallest_diameter))
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_diameter)

#=======================
# arc sieve 
#=======================
# This differs from the others; it doesn't define an aperture. 
def arcs(x, y, number, wavelength, focallength, zones, feature_limit, size_limit, center_dot=True, divisor=3):
    """ partial Fresnel diffraction via equal-area arcs """
    print("G04 arc plate max_zones={} feature_limit={} size_limit={} wavelength={} focallength={} number={}*"
          .format(zones, feature_limit, size_limit, wavelength, focallength, number))

    # determine first zone that is viable according to limits
    for zone in range(zones, 1, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        feature = radius-radius2
        size = 2*radius
        if feature>=feature_limit and size<=size_limit:
            start = zone
            total_diameter = size
            smallest_feature = feature
            break
    if start % 2 == 0:  # make odd
        start -= 1
    print("G04 starting zone is {} with feature size {:.6f} and diameter {:.6f}*"
          .format(start, feature, total_diameter))

    # compute the generator of the arc that is a pinhole in the first zone. 
    topzone = 3 # the first zone that is printed.
    topnumber = number
    number += 1
    topradius1 =math.sqrt(topzone*wavelength*focallength 
                     + (topzone*topzone*wavelength*wavelength/4))
    topradius2 =math.sqrt((topzone-1)*wavelength*focallength 
                     + ((topzone-1)*(topzone-1)*wavelength*wavelength/4))
    # want the circles inside a zone, centered, and filling the zone
    topdiameter = topradius1-topradius2
    topcenter = (topradius2+topradius1)/2
    topcircles = int(topcenter*2*math.pi / (divisor*topdiameter)) 
    if (topcircles%2):
        topcircles -= 1  # make even
    angle_increment = 2*math.pi/topcircles
    # difference between beginning and ending points
    angle_diff = math.atan(topdiameter/2/topcenter)
    print("G04 zone={} center={:.6f} diameter={:.6f} divisor={} circles={} angle={:.6f}*"
          .format(topzone, topcenter, topdiameter, divisor, topcircles, angle_increment))
    print("%ADD{}C,{:6f}*%".format(topnumber, topdiameter))
    apertures = {}
    apertures[topzone] = topnumber
    for dot in range(0, topcircles): 
        # print top dot
        x1 = math.cos(dot*angle_increment)*topcenter + x
        y1 = math.sin(dot*angle_increment)*topcenter + y
        print("D{}*X{:6f}Y{:6f}D03*".format(topnumber, x1, y1))
        for zone in range(5, start+2, 2): 
            radius1 = math.sqrt(zone*wavelength*focallength 
                              + (zone*zone*wavelength*wavelength/4))
            radius2 = math.sqrt((zone-1)*wavelength*focallength 
                              + ((zone-1)*(zone-1)*wavelength*wavelength/4))
            # want the circles inside a zone, centered, and filling the zone
            diameter = radius1-radius2
            center = (radius2+radius1)/2
            if zone in apertures:
                aperture = apertures[zone]
            else: 
                print("%ADD{}C,{:6f}*%".format(number, diameter))
                apertures[zone] = number
                aperture = number
                number += 1
            # center of arc
            xc = x + math.cos(dot*angle_increment)*center
            yc = y + math.sin(dot*angle_increment)*center
            # print("D{}*X{:6f}Y{:6f}D03*".format(number, xc, yc))

            # endpoint of arc = angle_diff-angle of diameter
            x1 = x + math.cos(dot*angle_increment + angle_diff - math.atan(diameter/2/center))*center; 
            y1 = y + math.sin(dot*angle_increment + angle_diff - math.atan(diameter/2/center))*center; 
            # print("D{}*X{:6f}Y{:6f}D03*".format(number, x1, y1))

            # endpoint of arc
            x2 = x + math.cos(dot*angle_increment - angle_diff + math.atan(diameter/2/center)) * center; 
            y2 = y + math.sin(dot*angle_increment - angle_diff + math.atan(diameter/2/center)) * center; 
            # print("D{}*X{:6f}Y{:6f}D03*".format(number, x2, y2))


            print("D{}*G75*G01X{:6f}Y{:6f}D02*".format(aperture, x1, y1))
            print("G02X{:6f}Y{:6f}I{:6f}J{:6f}D01*G01*".format(x2, y2, x-x1, y-y1))
            # number += 1

    # print center dot
    if (center_dot): 
        zone = 1
        radius =math.sqrt(zone*wavelength*focallength
                        + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("%ADD{}C,{:6f}*%".format(number, diameter))
        print("D{}*X{:6f}Y{:6f}D03*".format(number, x, y))
    print("G04 maximum g-code number is {}".format(number))

    print()
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))
    # print("%ADD{}{}*%".format(number, name))
    # print()
    return (start, total_diameter, smallest_feature, number)

#=============================
# now create the zone plates 
#=============================
# x=125.0
# y=125.0
# number=20
# wavelength=0.00055
# focallength=2000
# zones=100000
# feature_limit=0.008
# size_limit=1000
# center_dot=True
# divisor=2
# arcs(x, y, number, wavelength, focallength, zones, feature_limit, size_limit, center_dot, divisor)

###COUCH wavelengths = {'red':0.00065, 'green': 0.00055, 'blue': 0.00045}
###COUCH # red was 0.00075, which is infrared. 
###COUCH number = 20  # starting number for aperture
###COUCH serials = {}
###COUCH smallest = {}
###COUCH sizes = {}
###COUCH starts = {}
###COUCH focals = {}
###COUCH colors = {}
###COUCH serial = 20
###COUCH divisor = 2 # spacing of circles >= 2
###COUCH size_limit=3.0
###COUCH feature_limit=0.008
###COUCH for f in [22, 25, 32, 38]: 
###COUCH     zones=200
###COUCH     for center in [True, False]:
###COUCH         for color in ['red', 'green', 'blue']: 
###COUCH             wavelength = wavelengths[color]
###COUCH 
###COUCH             code = "zp{}-{}-{}".format(f,'pinhole' if center else 'blank', color)
###COUCH             (start, total_diameter, smallest_feature) = zoneplate(wavelength, f, zones, 
###COUCH                 feature_limit, size_limit, 1, code, serial, center)
###COUCH             serials[code] = serial
###COUCH             starts[code] = start
###COUCH             smallest[code] = smallest_feature
###COUCH             sizes[code] = total_diameter
###COUCH             focals[code] = f
###COUCH             colors[code] = color
###COUCH             serial += 1
###COUCH 
###COUCH             code = "ps{}-{}-{}".format(f,'pinhole' if center else 'blank',color)
###COUCH             (start, total_diameter, smallest_feature, number) = arcs(wavelength, f, zones, 
###COUCH                 feature_limit, size_limit, code, serial, center, divisor, number)
###COUCH             # (start, total_diameter, smallest_feature) = prob(wavelength, f, zones, 
###COUCH             #     feature_limit, size_limit, code, serial, center)
###COUCH             serials[code] = serial
###COUCH             starts[code] = start
###COUCH             smallest[code] = smallest_feature
###COUCH             sizes[code] = total_diameter
###COUCH             focals[code] = f
###COUCH             colors[code] = color
###COUCH             serial += 1
###COUCH 
###COUCH 
###COUCH print()
###COUCH 
###COUCH layout = [["zp22-pinhole-red", "zp22-blank-red", "zp22-pinhole-green", "zp22-blank-green", 
###COUCH            "zp22-pinhole-green", "zp22-blank-green", "zp22-pinhole-blue", "zp22-blank-blue"], 
###COUCH           ["ps22-pinhole-red", "ps22-blank-red", "ps22-pinhole-green", "ps22-blank-green", 
###COUCH            "ps22-pinhole-green", "ps22-blank-green", "ps22-pinhole-blue", "ps22-blank-blue"], 
###COUCH           ["zp25-pinhole-red", "zp25-blank-red", "zp25-pinhole-green", "zp25-blank-green", 
###COUCH            "zp25-pinhole-green", "zp25-blank-green", "zp25-pinhole-blue", "zp25-blank-blue"], 
###COUCH           ["ps25-pinhole-red", "ps25-blank-red", "ps25-pinhole-green", "ps25-blank-green", 
###COUCH            "ps25-pinhole-green", "ps25-blank-green", "ps25-pinhole-blue", "ps25-blank-blue"],
###COUCH           ["zp32-pinhole-red", "zp32-blank-red", "zp32-pinhole-green", "zp32-blank-green", 
###COUCH            "zp32-pinhole-green", "zp32-blank-green", "zp32-pinhole-blue", "zp32-blank-blue"], 
###COUCH           ["ps32-pinhole-red", "ps32-blank-red", "ps32-pinhole-green", "ps32-blank-green", 
###COUCH            "ps32-pinhole-green", "ps32-blank-green", "ps32-pinhole-blue", "ps32-blank-blue"],
###COUCH           ["zp38-pinhole-red", "zp38-blank-red", "zp38-pinhole-green", "zp38-blank-green", 
###COUCH            "zp38-pinhole-green", "zp38-blank-green", "zp38-pinhole-blue", "zp38-blank-blue"],
###COUCH           ["ps38-pinhole-red", "ps38-blank-red", "ps38-pinhole-green", "ps38-blank-green", 
###COUCH            "ps38-pinhole-green", "ps38-blank-green", "ps38-pinhole-blue", "ps38-blank-blue"]]
###COUCH 
###COUCH for x in range(8): 
###COUCH     lx = 15 + x*30
###COUCH     tx = lx-14
###COUCH     for y in range(8): 
###COUCH         ly = 15 + y*30
###COUCH         ty = ly-14
###COUCH         code = layout[x][y]
###COUCH         print("D{}*".format(serials[code]))
###COUCH         print("X{:6f}Y{:6f}D03*".format(rescale(lx),rescale(ly)))
###COUCH         g.primitives+=[glif.text(tx*1000000,ty*1000000, "{}-{:.2}mm".format(code,sizes[code]), 0.5, 0, 0, "", 0.1)]
###COUCH 
###COUCH 
###COUCH print("""
###COUCH %TD*%
###COUCH 
###COUCH %AMpoint*
###COUCH 1,1,0.1,0,0,0*
###COUCH %
###COUCH 
###COUCH %ADD11point*%
###COUCH 
###COUCH D11*
###COUCH 
###COUCH X30.0Y0.0D02*
###COUCH X30.0Y240.0D01*
###COUCH 
###COUCH X60.0Y0.0D02*
###COUCH X60.0Y240.0D01*
###COUCH 
###COUCH X90.0Y0.0D02*
###COUCH X90.0Y240.0D01*
###COUCH 
###COUCH X120.0Y0.0D02*
###COUCH X120.0Y240.0D01*
###COUCH 
###COUCH X150.0Y0.0D02*
###COUCH X150.0Y240.0D01*
###COUCH 
###COUCH X180.0Y0.0D02*
###COUCH X180.0Y240.0D01*
###COUCH 
###COUCH X210.0Y0.0D02*
###COUCH X210.0Y240.0D01*
###COUCH 
###COUCH X0.0Y30.0D02*
###COUCH X240.0Y30.0D01*
###COUCH 
###COUCH X0.0Y60.0D02*
###COUCH X240.0Y60.0D01*
###COUCH 
###COUCH X0.0Y90.0D02*
###COUCH X240.0Y90.0D01*
###COUCH 
###COUCH X0.0Y120.0D02*
###COUCH X240.0Y120.0D01*
###COUCH 
###COUCH X0.0Y150.0D02*
###COUCH X240.0Y150.0D01*
###COUCH 
###COUCH X0.0Y180.0D02*
###COUCH X240.0Y180.0D01*
###COUCH 
###COUCH X0.0Y210.0D02*
###COUCH X240.0Y210.0D01*
###COUCH 
###COUCH %AMreference-circle*
###COUCH 1,1,25.6,0,0,0*
###COUCH 1,0,25.4,0,0,0*
###COUCH %
###COUCH 
###COUCH %ADD14reference-circle*%
###COUCH D14*
###COUCH """)
###COUCH for x in range(15, 30*8, 30):
###COUCH     for y in range(15, 30*8, 30):
###COUCH         print("X{:.6f}Y{:.6f}D03*".format(x, y))
###COUCH 
###COUCH g.write()
###COUCH f = open("labels.gbr", "r")
###COUCH f.readline()
###COUCH f.readline()
###COUCH f.readline()
###COUCH print(f.read())


print("""
M02*
""")
# # a debugging printout 
# for x in range(8): 
#     lx = 2 + x*2
#     for y in range(8): 
#         ly = 2 + y*2
#         code = layout[x][y]
#         print("D{}*".format(serials[code]))
#         print("X{:.6f}Y{:.6f}D03*".format(lx,ly))
# 
# print("M02*")

# # Map output
# from pprint import pprint
# 
# layout2 = [[0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0]]
# for x in range(8): 
#     for y in range(8): 
#         layout2[x][y] = serials[layout[x][y]]
# pprint(layout2)
# 
# layout2 = [[0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0]]
# for x in range(8): 
#     for y in range(8): 
#         layout2[x][y] = int(smallest[layout[x][y]]*1000000)/1000000
# pprint(layout2)
# 
# layout2 = [[0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0]]
# for x in range(8): 
#     for y in range(8): 
#         layout2[x][y] = int(sizes[layout[x][y]]*1000000)/1000000
# pprint(layout2)
# 
# layout2 = [[0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0]]
# for x in range(8): 
#     for y in range(8): 
#         layout2[x][y] = starts[layout[x][y]]
# pprint(layout2)
# 
# layout2 = [[0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0]]
# for x in range(8): 
#     for y in range(8): 
#         layout2[x][y] = focals[layout[x][y]]
# pprint(layout2)
# 
# layout2 = [[0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0], 
#            [0,0,0,0,0,0,0,0]]
# for x in range(8): 
#     for y in range(8): 
#         layout2[x][y] = colors[layout[x][y]]
# pprint(layout2)

#=============================
# now create the zone plates 
#=============================
x=125.0
y=125.0
number=20
wavelength=0.00055
focallength=100
zones=100
feature_limit=0.008
size_limit=1000
macro_limit=1000
center_dot=True
diameter_limit=100
divisor=3
name='prob'
# origpen=1
# zoneplate(wavelength, focallength, zones, feature_limit, size_limit, origpen, name, number, center_dot)


prob(wavelength, focallength, zones, diameter_limit, size_limit, macro_limit, name, number, center_dot)
print("D{}*".format(number))
print("X{:6f}Y{:6f}D03*".format(x,y))

print("M02*")
