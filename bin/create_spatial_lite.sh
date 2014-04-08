#!/bin/bash

touch $1
spatialite $1 "SELECT InitSpatialMetaData();"
