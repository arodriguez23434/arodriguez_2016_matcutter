#!/usr/bin/python

import math

#Initialize list of occupied slices and recieve user input for material specifications
ocp_list=list()
print("---Sheet Material Slicer and Cost Calculator---")
ocp_xmat=float(input("What is the length of the material sheet? "));
ocp_ymat=float(input("What is the width of the material sheet? "));
ocp_basecost=float(input("What is the cost of one of these sheets? "));
ocp_xslice=float(input("What is the length of the slices you want to make? "));
ocp_yslice=float(input("What is the width of the slices you want to make? "));
ocp_quantdesired=int(input("How many sliced units do you want? "));
ocp_wastearea=float(input("What is the cost of disposal per unit area? "));
ocp_wastecost=float(input("What is the unit area for waste disposal? "));
print("\nProcessing...")


#Find out the largest x or y coordinate in the list of occupied slices.
#Useful for skipping already occupied slices for performing a second, modified scan.
def get_max_coord(xory):
    if (xory==0 or xory=='x'): temp_int=0
    elif (xory==1 or xory=='y'): temp_int=1
    else: print("\nERROR: get_max_coord called with invalid input, defaulting to x");temp_int=0
    temp_max=0
    while (temp_int<len(ocp_list)):
        if (temp_max<ocp_list[temp_int]): temp_max=ocp_list[temp_int]
        temp_int+=2
    return temp_max

#Check to see if a pair of coordinates are in any generic rectangle
#Used in the main scan function to check for occupied slices.
def scan_slice(xcheck,ycheck,xint,yint,xfin,yfin,tick):
    slice_present=0
    temp_iterate=xint
    while (temp_iterate<=xfin):
        #Is the x coordinate within the slice?
        if (temp_iterate==xcheck): slice_present+=1;
        temp_iterate+=tick
    temp_iterate=yint
    while (temp_iterate<=yfin):
        #Is the y coordinate within the slice?
        if (temp_iterate==ycheck): slice_present+=1;
        temp_iterate+=tick
    if (slice_present<2): return 0 #If not, the slice is free
    else: return 1 #If both coordinates are within the slice, the slice is occupied
    return

#The main scanning function
#Here, we check the x and y coordinates of our list of occupied slices and compare them
#to an iterating x and y coordinate pair that iterates based on the size of our slices.
#If the coordinates are not the list, then the slice is free and is added to the list.
def scan_material(xbase,ybase,xslice,yslice,ocp_list):
    xscan=0;yscan=get_max_coord('y'); 
    #Look in the table of recorded coordinates, then start at the bottom-most slice
    while (yscan+yslice<=ybase): #Line-by-line scan of y-axis
        xscan=0 #We will be iterating the entire x-axis as we go down the y-axis
        while (xscan+xslice<=xbase): #Line-by-line scan of x in every y-axis scan
            is_occupied=0;temp_interval=0
            while temp_interval < len(ocp_list): #Check all existing points for conflicts
                if (xslice<yslice): temp_tick=yslice/xslice
                else: temp_tick=xslice/yslice
                #We want to support decimals while hitting the coordinates we want.
                #So, we iterate each coordinate scan based on larger slice/smaller slice ratio.
                is_occupied+=scan_slice(xscan+xslice,yscan+yslice,ocp_list[temp_interval],ocp_list[temp_interval+1],ocp_list[temp_interval+2],ocp_list[temp_interval+3],temp_tick)
                temp_interval+=4
            if (is_occupied<1): #Does a conflict exist? If not, add coordinates to list
                ocp_list+=[xscan,yscan,xscan+xslice,yscan+yslice]
            xscan+=xslice        
        yscan+=yslice
    yscan=0; 
    while (yscan+yslice<=ybase):
        xscan=get_max_coord('x') 
        #Now, we will repeat the process from the right-most slice from the top of the y-axis
        while (xscan+xslice<=xbase):
            is_occupied=0;temp_interval=0
            while temp_interval < len(ocp_list): 
                if (xslice<yslice): temp_tick=yslice/xslice
                else: temp_tick=xslice/yslice
                is_occupied+=scan_slice(xscan+xslice,yscan+yslice,ocp_list[temp_interval],ocp_list[temp_interval+1],ocp_list[temp_interval+2],ocp_list[temp_interval+3],temp_tick)
                temp_interval+=4
            if (is_occupied<1):
                ocp_list+=[xscan,yscan,xscan+xslice,yscan+yslice]
            xscan+=xslice        
        yscan+=yslice
    return

#Print out the list of occupied slices in a user-readable fashion.
def print_coords():
    temp_i=0
    print("\nThe sheet can be sliced up into rectangular units with these coordinates:")
    while (temp_i<len(ocp_list)-3):
        print("({0:.5f},{1:.5f}) to ({2:.5f},{3:.5f})".format(ocp_list[temp_i],ocp_list[temp_i+1],ocp_list[temp_i+2],ocp_list[temp_i+3]))
        temp_i+=4
    return
    
#Calculate the total area, the sum of all the areas of the slice, and then the cost
#The cost will be based on material + wasted amount
def calculate_cost(xbase,ybase,temp_basecost,temp_wastecost,temp_wastearea,temp_quantdesired):
    area_base=xbase*ybase
    area_slices=0
    slice_quantity=0
    temp_i=0
    while (temp_i<len(ocp_list)):
        #Calculate the total area occupied        
        area_slices+=(ocp_list[temp_i+2]-ocp_list[temp_i])*(ocp_list[temp_i+3]-ocp_list[temp_i+1])
        slice_quantity+=1 #Calculate how many sliced units can be made from a single material 
        temp_i+=4
    area_waste=area_base-area_slices #Calculate the total area wasted
    #Calculate how many material units we will need; always round up
    temp_quanthave=math.ceil(temp_quantdesired/slice_quantity)
    #Calculate the cost of waste disposal per slice
    temp_costperwastedslice=(temp_wastecost*(area_waste/temp_wastearea))
    #Calculate the number of slices leftover from final material   
    temp_leftoverwaste=round((temp_quanthave%(temp_quantdesired/slice_quantity))*slice_quantity)
    #Calculate total waste cost; based on slices used times cost per slice + slices leftover times cost per slice    
    temp_wastecost=(((temp_quanthave-1)*temp_costperwastedslice)+(temp_leftoverwaste*temp_costperwastedslice))
    
    print("\nArea of material sheet: {0:.5f}".format(area_base))
    print("Area of used material: {0:.5f} vs. waste: {1:.5f}".format(area_slices,area_waste))
    print("Sliced units desired: {0}".format(temp_quantdesired))
    print("Slices from sheet: {0}".format(slice_quantity))
    print("Material sheets required: {0}".format(temp_quanthave))
    print("Cost of sheets: ${0:.2f} per sheet totaling to ${1:.2f}".format(temp_basecost,(temp_basecost*temp_quanthave)))  
    print("Cost of waste disposal: ${0:.2f} per sheet totaling to ${1:.2f}".format(temp_costperwastedslice,((temp_quanthave-1)*temp_costperwastedslice)))
    print("Cost of waste disposal from leftovers in last sheet: ${0:.2f}".format((temp_leftoverwaste*temp_costperwastedslice))) 
    print("Aggregate waste cost: ${0:.2f}".format(temp_wastecost))
    print("---\nTotal cost: ${0:.2f}".format((temp_basecost*temp_quanthave)+temp_wastecost))
    return

#Find where slices can be made in the material sheet
scan_material(ocp_xmat,ocp_ymat,ocp_xslice,ocp_yslice,ocp_list)
#Find where slices rotated 90 degrees can be made in the same material sheet
scan_material(ocp_xmat,ocp_ymat,ocp_yslice,ocp_xslice,ocp_list)
#Print out the coordinates of these slices
print_coords()
#Calculate and print the total cost of the whole process - including waste disposal
calculate_cost(ocp_xmat,ocp_ymat,ocp_basecost,ocp_wastecost,ocp_wastearea,ocp_quantdesired)