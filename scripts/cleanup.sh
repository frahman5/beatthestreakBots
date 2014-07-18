#!/bin/bash

## Script to delete instances after they've been used


# Delete all the instances!
gcutil --project='faiyam-bts-1' deleteinstance \
    sn7vmn1 sn7vmn2 
    # sn5vmn1 sn5vmn2 sn6vmn1 sn6vmn2 sn7vmn1 sn7vmn2
