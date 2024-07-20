import math
import random
import array
import sys
import time

import pcb_tools as pcb
import pcb_tools.primitives as pcb_primitive
import primitives as glif
import gerber_writer

# initialize label writing, which will be done at the end, 
# after all of the plates have been printed. 
primitives=[]  # a list of primitives that will be printed by the gerber writer
g=gerber_writer.gerber_writer("labels.gbr") # print output to labels.gbr

# print header for the print file
print("""
%MOMM*%
%FSLAX36Y36*%
%LPD*%
""")

# needed for certain kinds of layouts; disabled now. 
def rescale(value):
    return value


#======================
# classical zone plate 
#======================

def zoneplate(wavelength, focallength, zone_limit, feature_limit, size_limit, 
              origpen, name, number, center_dot=True):
    # wavelength: Wavelength of light in mm. 
    # focallength: offset from zone plate to sensor in mm. 
    # zone_limit: maximum number of zones allowed. 
    # feature_limit: smallest feature allowed. 
    # size_limit: largest size of zone plate allowed (diameter in mm)
    # origpen: 1 for odd harmonics, 0 for even harmonics. 
    # name: ascii name of macro to be defined. 
    # number: number of aperture to assign. 
    # center_dot: whether to print the center dot or not. 

    # begin a macro 
    print("%AM{}*".format(name))  
    # comment on what the macro contains 
    print("0 {}zone plate zone_limit={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(("inverse " if origpen==0 else ""), zone_limit, feature_limit, size_limit, wavelength, focallength, name, number))

    # determine outermost zone that is viable according to printing limits
    pen = origpen  # 1 means writing, 0 means blank
    for zone in range(zone_limit, 3, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                       + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        feature = radius-radius2
        size= radius*2
        if feature>=feature_limit and size<=size_limit: 
            start = zone
            total_diameter = size
            smallest_feature=feature
            break
        pen = 1-pen

    # make odd if odd zones shown (origpen==1), even if even zones. 
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
    #### These are debugging printouts that don't affect rendering
    # print("%TAfocal_length,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))

    # define an aperture for the zone plate
    # (This doesn't print anything.) 
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_feature)

#=======================
# pinhole sieve, odd harmonics 
#=======================

def sieve(wavelength, focallength, zone_limit, feature_limit, size_limit, 
          name, number, center_dot=True, divisor=3):
    # wavelength: Wavelength of light in mm. 
    # focallength: offset from zone plate to sensor in mm. 
    # zone_limit: maximum number of zones allowed. 
    # feature_limit: smallest feature allowed. 
    # size_limit: largest size of zone plate allowed (diameter in mm)
    # name: ascii name of macro to be defined. 
    # number: number of aperture to assign. 
    # center_dot: whether to print the center dot or not. 
    # zone_limit: largest zone number allowed, subject to printer limits
    # feature_limit: the size of the smallest feature and/or feature separation.
    # size_limit: a limit upon the diameter of the zone plate. 
    # divisor: how many diameters to skip between dots: minimum 2. 

    # start a macro 
    print("%AM{}*".format(name))

    # a comment on the contents of the macro 
    print("0 pinhole sieve max_zones={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(zone_limit, feature_limit, size_limit, wavelength, focallength, name, number))

    # determine first zone that is viable according to limits
    for zone in range(zone_limit, 1, -1): 
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
    ### documentation that doesn't affect printing. 
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))

    # Define an aperture for this zone plate. 
    # (This does not print anything.) 
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_feature)

#===============================
# inverse sieve, even harmonics
#===============================

def inverse_sieve(wavelength, focallength, zone_limit, feature_limit, size_limit, name, number, divisor=3):
    # wavelength: Wavelength of light in mm. 
    # focallength: offset from zone plate to sensor in mm. 
    # zone_limit: maximum number of zones allowed. 
    # feature_limit: smallest feature allowed. 
    # size_limit: largest size of zone plate allowed (diameter in mm)
    # name: ascii name of macro to be defined. 
    # number: number of aperture to assign. 
    # center_dot: whether to print the center dot or not. 
    # zone_limit: largest zone number allowed, subject to printer limits
    # feature_limit: the size of the smallest feature and/or feature separation.
    # size_limit: a limit upon the diameter of the zone plate. 
    # divisor: how many diameters to skip between dots: minimum 2. 
    print("%AM{}*".format(name))
    print("0 inverse sieve zone_limit={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(zone_limit, feature_limit, size_limit, wavelength, focallength, name, number))

    # determine first zone that is viable according to limits
    for zone in range(zone_limit, 1, -1): 
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
        circles = int(center*2*math.pi / (divisor*diameter)) 
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
    ### documentation that doesn't affect printing
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_feature,{:.6f}*%".format(smallest_feature))

    # Define an aperture with the current macro and number. 
    print("%ADD{}{}*%".format(number, name))
    print()
    return (start, total_diameter, smallest_feature)


#============================
# probabilistic zone sieve 
#============================

def prob(wavelength, focallength, zone_limit, diameter_limit, size_limit, name, number, center_dot=True):
    # wavelength: Wavelength of light in mm. 
    # focallength: offset from zone plate to sensor in mm. 
    # zone_limit: maximum number of zones allowed. 
    # feature_limit: smallest feature allowed. 
    # size_limit: largest size of zone plate allowed (diameter in mm)
    # name: ascii name of macro to be defined. 
    # number: number of aperture to assign. 
    # center_dot: whether to print the center dot or not. 
    # zone_limit: largest zone number allowed, subject to printer limits
    # feature_limit: the size of the smallest feature and/or feature separation.
    # size_limit: a limit upon the diameter of the zone plate. 
    print("%AM{}*".format(name))

    print("0 prob max_zones={} diameter_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(zone_limit, diameter_limit, size_limit, wavelength, focallength, name, number))

    # determine first zone that is viable according to limits
    for zone in range(zone_limit, 1, -1): 
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

    # create usage maps for eligible zones to determine collisions. 
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
        

    for trial in range(0,10000): 
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
    ### documentation that doesn't affect printing
    # print("%TAfocallength,{}*%".format(focallength))
    # print("%TAwavelength,{}*%".format(wavelength))
    # print("%TAmaximum_zone,{}*%".format(start))
    # print("%TAtotal_diameter,{:.6f}*%".format(total_diameter))
    # print("%TAsmallest_diameter,{:.6f}*%".format(smallest_diameter))

    # define an aperture with the current macro and the given number. 
    print("%ADD{}{}*%".format(number, name))

    print()
    return (start, total_diameter, smallest_diameter)

#=============================
# now create the zone plates 
#=============================

wavelengths = {'red':0.00075, 'green': 0.00055, 'blue': 0.00045}
serials = {}
smallest = {}
sizes = {}
starts = {}
focals = {}
colors = {}
serial = 20
divisor = 2 # spacing of circles >= 2
size_limit=3.0
feature_limit=0.008
for f in [22, 25, 32, 38]: 
    zone_limit=200
    for center in [True, False]:
        for color in ['red', 'green', 'blue']: 
            wavelength = wavelengths[color]

            code = "zp{}-{}-{}".format(f,'pinhole' if center else 'blank', color)
            (start, total_diameter, smallest_feature) = zoneplate(wavelength, f, zone_limit, 
                feature_limit, size_limit, 1, code, serial, center)
            serials[code] = serial
            starts[code] = start
            smallest[code] = smallest_feature
            sizes[code] = total_diameter
            focals[code] = f
            colors[code] = color
            serial += 1

            code = "ps{}-{}-{}".format(f,'pinhole' if center else 'blank',color)
            (start, total_diameter, smallest_feature) = sieve(wavelength, f, zone_limit, 
                feature_limit, size_limit, code, serial, center, divisor)
            serials[code] = serial
            starts[code] = start
            smallest[code] = smallest_feature
            sizes[code] = total_diameter
            focals[code] = f
            colors[code] = color
            serial += 1


print()

layout = [["zp22-pinhole-red", "zp22-blank-red", "zp22-pinhole-green", "zp22-blank-green", 
           "zp22-pinhole-green", "zp22-blank-green", "zp22-pinhole-blue", "zp22-blank-blue"], 
          ["ps22-pinhole-red", "ps22-blank-red", "ps22-pinhole-green", "ps22-blank-green", 
           "ps22-pinhole-green", "ps22-blank-green", "ps22-pinhole-blue", "ps22-blank-blue"], 
          ["zp25-pinhole-red", "zp25-blank-red", "zp25-pinhole-green", "zp25-blank-green", 
           "zp25-pinhole-green", "zp25-blank-green", "zp25-pinhole-blue", "zp25-blank-blue"], 
          ["ps25-pinhole-red", "ps25-blank-red", "ps25-pinhole-green", "ps25-blank-green", 
           "ps25-pinhole-green", "ps25-blank-green", "ps25-pinhole-blue", "ps25-blank-blue"],
          ["zp32-pinhole-red", "zp32-blank-red", "zp32-pinhole-green", "zp32-blank-green", 
           "zp32-pinhole-green", "zp32-blank-green", "zp32-pinhole-blue", "zp32-blank-blue"], 
          ["ps32-pinhole-red", "ps32-blank-red", "ps32-pinhole-green", "ps32-blank-green", 
           "ps32-pinhole-green", "ps32-blank-green", "ps32-pinhole-blue", "ps32-blank-blue"],
          ["zp38-pinhole-red", "zp38-blank-red", "zp38-pinhole-green", "zp38-blank-green", 
           "zp38-pinhole-green", "zp38-blank-green", "zp38-pinhole-blue", "zp38-blank-blue"],
          ["ps38-pinhole-red", "ps38-blank-red", "ps38-pinhole-green", "ps38-blank-green", 
           "ps38-pinhole-green", "ps38-blank-green", "ps38-pinhole-blue", "ps38-blank-blue"]]

for x in range(8): 
    lx = 15 + x*30
    tx = lx-14
    for y in range(8): 
        ly = 15 + y*30
        ty = ly-14
        code = layout[x][y]
        print("D{}*".format(serials[code]))
        print("X{:6f}Y{:6f}D03*".format(rescale(lx),rescale(ly)))
        g.primitives+=[glif.text(tx*1000000,ty*1000000, "{}-{:.2}mm".format(code,sizes[code]), 0.5, 0, 0, "", 0.1)]


print("""
%TD*%

%AMpoint*
1,1,0.1,0,0,0*
%

%ADD11point*%

D11*

X30.0Y0.0D02*
X30.0Y240.0D01*

X60.0Y0.0D02*
X60.0Y240.0D01*

X90.0Y0.0D02*
X90.0Y240.0D01*

X120.0Y0.0D02*
X120.0Y240.0D01*

X150.0Y0.0D02*
X150.0Y240.0D01*

X180.0Y0.0D02*
X180.0Y240.0D01*

X210.0Y0.0D02*
X210.0Y240.0D01*

X0.0Y30.0D02*
X240.0Y30.0D01*

X0.0Y60.0D02*
X240.0Y60.0D01*

X0.0Y90.0D02*
X240.0Y90.0D01*

X0.0Y120.0D02*
X240.0Y120.0D01*

X0.0Y150.0D02*
X240.0Y150.0D01*

X0.0Y180.0D02*
X240.0Y180.0D01*

X0.0Y210.0D02*
X240.0Y210.0D01*

%AMreference-circle*
1,1,25.6,0,0,0*
1,0,25.4,0,0,0*
%

%ADD14reference-circle*%
D14*
""")
for x in range(15, 30*8, 30):
    for y in range(15, 30*8, 30):
        print("X{:.6f}Y{:.6f}D03*".format(x, y))

g.write()
f = open("labels.gbr", "r")
f.readline()
f.readline()
f.readline()
print(f.read())


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
