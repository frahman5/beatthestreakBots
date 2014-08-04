#!/bin/bash

## Script to delete instances after they've been used

# Delete all the instances, updating first
gcutil --project='faiyam-bts-1' deleteinstance sn5 sn6 sn7 sn8 sn9 sn10 sn11 \
                                              sn12 sn13 sn14 sn15 sn16 sn17
#gcutil --project='faiyam-bts-1' deleteinstance sn5 sn6 sn7 sn8 sn9 sn11 sn12 sn13 sn14 sn15 sn17
