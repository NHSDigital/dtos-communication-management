#!/usr/bin/env python3

import xml.dom.minidom
import sys

def pretty_print_xml(input_file):
    # Read the XML file
    with open(input_file, "r") as file:
        xml_string = file.read()

    # Parse and pretty print
    parsed_xml = xml.dom.minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")

    # Write back to file
    with open(input_file, "w") as file:
        file.write(pretty_xml)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pretty_print_xml.py <xml_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    pretty_print_xml(input_file)
    print(f"XML report has been pretty printed to {input_file}") 