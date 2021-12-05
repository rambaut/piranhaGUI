import PySimpleGUI as sg
import os.path
import csv

def csv_to_list(filepath):
    with open(filepath, newline = '') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_list = list(csvreader)

    return csv_list

def setup_layout(samples):

    samples_list = csv_to_list(samples):
