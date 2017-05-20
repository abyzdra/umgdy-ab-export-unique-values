#-------------------------------------------------------------------------------
# Name:		Export Unique Values
# Author:	Alicja Byzdra
# Institution:	UMGDY
# Created:	24-04-2017
#-------------------------------------------------------------------------------

import arcpy

# coding: utf8

try:
    ################## PARAMETERS #######################
    newTab = arcpy.GetParameterAsText(0)
    oldTab = arcpy.GetParameterAsText(1)
    newIddField = str(arcpy.GetParameterAsText(2))
    oldIddField = str(arcpy.GetParameterAsText(3))
    outputGDB = arcpy.GetParameterAsText(4)
    outputName = arcpy.GetParameterAsText(5)
    ################## PARAMETERS #######################

    desc=arcpy.Describe(oldTab)
    path=desc.path
    path2=path.split("\\")
    folder=str(path2[-1])
    if folder[-4:]==".gdb":
        folder=folder[:-4]


    ################## READ IDDS ########################
    IdOldTab=[]
    with arcpy.da.SearchCursor(oldTab,oldIddField) as cursor:
        for row in cursor:
            IdOldTab.append(row[0])
    del cursor

    IdNewTab=[]
    with arcpy.da.SearchCursor(newTab,newIddField) as cursor:
        for row in cursor:
            IdNewTab.append(row[0])
    del cursor
    ################## READ IDDS ########################


    ################## FIND UNIQUE RECORDS ##############
    notInOldTab=[]
    for ind in range(len(IdOldTab)):
        if IdOldTab[ind] not in IdNewTab:
            notInOldTab.append(IdOldTab[ind].encode('utf-8'))
    ################## FIND UNIQUE RECORDS ##############


    ################## SELECT UNIQUE RECORDS ############
    stringL = str(notInOldTab)
    stringL = stringL.replace("[","(")
    stringL = stringL.replace("]",")")

    query = str(oldIddField)+' IN {0}'.format(stringL)
    arcpy.management.SelectLayerByAttribute(oldTab,"NEW_SELECTION",query)
    arcpy.CopyFeatures_management(oldTab, "in_memory"+"\\"+"tempTab")
    arcpy.management.SelectLayerByAttribute(oldTab,"CLEAR_SELECTION")
    arcpy.AddField_management("in_memory"+"\\"+"tempTab", "src", "TEXT",field_length=50)
    arcpy.CalculateField_management(in_table="in_memory"+"\\"+"tempTab", field="src", expression="""nazwa_gdb( !src! ,'"""+folder+"""')""", expression_type="PYTHON_9.3", code_block="def nazwa_gdb(src,fldr):\n    if src is None:\n        return fldr\n    else:\n        return src")
    ################## SELECT UNIQUE RECORDS ############


    arcpy.CopyFeatures_management(newTab, outputGDB+"\\"+outputName)
    fields=arcpy.ListFields(outputGDB+"\\"+outputName)
    if "src" not in fields:
        arcpy.AddField_management(outputGDB+"\\"+outputName, "src", "TEXT",field_length=50)
    arcpy.Append_management(inputs="in_memory"+"\\"+"tempTab", target=outputGDB+"\\"+outputName, schema_type="NO_TEST",field_mapping="",subtype="")
    arcpy.Delete_management(in_data="in_memory", data_type="Workspace")

    #nowy output
    #10_0

    arcpy.AddMessage("Successful.")

except:
    arcpy.AddError("Error occurred...")
    arcpy.AddMessage(arcpy.GetMessages())

