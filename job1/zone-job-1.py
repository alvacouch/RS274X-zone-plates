import math

print("""
%MOMM*%
""")


def zoneplate(wavelength, focallength, zones, feature_limit, size_limit, origpen, name, number):
    print("%AM{}*".format(name))
    print("0 {}zone plate zones={} feature_limit={} size_limit={} wavelength={} focallength={} name={} number={}*"
          .format(("inverse " if origpen==0 else ""), zones, feature_limit, size_limit, wavelength, focallength, name, number))
    # determine first zone that is viable according to limits
    pen = origpen
    for zone in range(zones, 1, -1): 
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
    if origpen==1: 
        if start%2==0:
            start -= 1
    else: 
        if start%2==1:
            start -= 1

    print("0 pen is {} starting zone is {} with feature size {:.6f} and diameter {:.6f}*"
          .format(pen, start, feature, total_diameter))

    pen = 1
    for zone in range(start, 0, -1): 
        radius =math.sqrt(zone*wavelength*focallength 
                       + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("1,{},{:.6f},0,0,0*".format(pen,diameter))
        pen = 1-pen


    # print center dot
    if origpen==1: 
        print("0 zone 0 center*".format(focallength))
        zone = 1
        radius =math.sqrt(zone*wavelength*focallength
                        + (zone*zone*wavelength*wavelength/4))
        diameter=2*radius
        print("1,1,{:.6f},0,0,0*".format(diameter))

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

def sieve(wavelength, focallength, zones, feature_limit, size_limit, name, number):
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

    for zone in range(start,0,-2): 
        radius1 =math.sqrt(zone*wavelength*focallength 
                         + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                         + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        # want the circles inside a zone, centered, and filling the zone
        radius = radius1-radius2
        center = (radius2+radius1)/2
        circles = int(center*2*math.pi / (3*radius)) 
        angle_increment = 2*math.pi/circles
        print("0 zone {} center={:.6f} radius={:.6f} circles={} angle={:.6f}*"
              .format(int(zone/2), center,radius,circles, angle_increment))
        for dot in range(0, circles): 
            x = math.cos(dot*angle_increment)*center
            y = math.sin(dot*angle_increment)*center
            print("1,1,{:.6f},{:.6f},{:.6f},0*".format(radius, x, y))
    # print center dot
    print("0 zone 0 center*".format(focallength))
    zone = 1
    radius =math.sqrt(zone*wavelength*focallength
                    + (zone*zone*wavelength*wavelength/4))
    diameter=2*radius
    print("1,1,{:.6f},0,0,0*".format(diameter))

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
        radius1 =math.sqrt(zone*wavelength*focallength 
                         + (zone*zone*wavelength*wavelength/4))
        radius2 =math.sqrt((zone-1)*wavelength*focallength 
                         + ((zone-1)*(zone-1)*wavelength*wavelength/4))
        # want the circles inside a zone, centered, and filling the zone
        radius = radius1-radius2
        center = (radius2+radius1)/2
        circles = int(center*2*math.pi / (3*radius)) 
        angle_increment = 2*math.pi/circles
        print("0 zone {} center={:.6f} radius={:.6f} circles={} angle={:.6f}*"
              .format(int((zone+1)/2), center,radius,circles, angle_increment))
        for dot in range(0, circles): 
            x = math.cos(dot*angle_increment)*center
            y = math.sin(dot*angle_increment)*center
            print("1,1,{:.6f},{:.6f},{:.6f},0*".format(radius, x, y))

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

wavelengths = {'red':0.00075, 'green': 0.00055, 'blue': 0.00045}
serials = {}
smallest = {}
sizes = {}
starts = {}
focals = {}
colors = {}
serial = 20
size_limit=1.5
for f in [15, 18]: 
    zones=200
    for feature_limit in [0.008,0.012]: 
        for color in ['red', 'green', 'blue']: 
            wavelength = wavelengths[color]

            code = "zp{}-{}-{}".format(f,feature_limit,color)
            (start, total_diameter, smallest_feature) = zoneplate(wavelength, f, zones, feature_limit, size_limit, 1, code, serial)
            serials[code] = serial
            starts[code] = start
            smallest[code] = smallest_feature
            sizes[code] = total_diameter
            focals[code] = f
            colors[code] = color
            serial += 1

            code = "ip{}-{}-{}".format(f,feature_limit,color)
            (start, total_diameter, smallest_feature) = zoneplate(wavelength, f, zones, feature_limit, size_limit, 0, code, serial)
            serials[code] = serial
            starts[code] = start
            smallest[code] = smallest_feature
            sizes[code] = total_diameter
            focals[code] = f
            colors[code] = color
            serial += 1

            code = "ps{}-{}-{}".format(f,feature_limit,color)
            (start, total_diameter, smallest_feature) = sieve(wavelength, f, zones, feature_limit, size_limit, code, serial)
            serials[code] = serial
            starts[code] = start
            smallest[code] = smallest_feature
            sizes[code] = total_diameter
            focals[code] = f
            colors[code] = color
            serial += 1

            code = "is{}-{}-{}".format(f,feature_limit,color)
            (start, total_diameter, smallest_feature) = inverse_sieve(wavelength, f, zones, feature_limit, size_limit, code, serial)
            serials[code] = serial
            starts[code] = start
            smallest[code] = smallest_feature
            sizes[code] = total_diameter
            focals[code] = f
            colors[code] = color
            serial += 1

print()

layout = [["zp15-0.008-red", "zp15-0.008-green", "zp15-0.008-green", "zp15-0.008-blue", 
           "zp15-0.012-red", "zp15-0.012-green", "zp15-0.012-green", "zp15-0.012-blue"], 
          ["ip15-0.008-red", "ip15-0.008-green", "ip15-0.008-green", "ip15-0.008-blue", 
           "ip15-0.012-red", "ip15-0.012-green", "ip15-0.012-green", "ip15-0.012-blue"], 
          ["ps15-0.008-red", "ps15-0.008-green", "ps15-0.008-green", "ps15-0.008-blue", 
           "ps15-0.012-red", "ps15-0.012-green", "ps15-0.012-green", "ps15-0.012-blue"], 
          ["is15-0.008-red", "is15-0.008-green", "is15-0.008-green", "is15-0.008-blue", 
           "is15-0.012-red", "is15-0.012-green", "is15-0.012-green", "is15-0.012-blue"], 
          ["zp18-0.008-red", "zp18-0.008-green", "zp18-0.008-green", "zp18-0.008-blue", 
           "zp18-0.012-red", "zp18-0.012-green", "zp18-0.012-green", "zp18-0.012-blue"], 
          ["ip18-0.008-red", "ip18-0.008-green", "ip18-0.008-green", "ip18-0.008-blue", 
           "ip18-0.012-red", "ip18-0.012-green", "ip18-0.012-green", "ip18-0.012-blue"], 
          ["ps18-0.008-red", "ps18-0.008-green", "ps18-0.008-green", "ps18-0.008-blue", 
           "ps18-0.012-red", "ps18-0.012-green", "ps18-0.012-green", "ps18-0.012-blue"], 
          ["is18-0.008-red", "is18-0.008-green", "is18-0.008-green", "is18-0.008-blue", 
           "is18-0.012-red", "is18-0.012-green", "is18-0.012-green", "is18-0.012-blue"]] 

for x in range(8): 
    lx = 15 + x*30
    for y in range(8): 
        ly = 15 + y*30
        code = layout[x][y]
        print("D{}*".format(serials[code]))
        print("X{:.6f}Y{:.6f}D03*".format(lx,ly))

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
