"""
Have you ever wanted to take your Google Docs changelog bulleted lists and automatically create a new json object so
that you can deploy the changelog update easily to Virtrolio? Your solution hath come!

How to use this script:
- Ensure that this script is in the same folder as...
  - The changelog.json that you want to update
  - The changelogInput.txt where you will copy paste the changelog items into
- Go to the Google Docs with your changelog, copy paste the bullet list items, and paste into changelogInput.txt
- Run the python script
- Voilà, your changelog.json has now been updated with the new update content! Update the changelog.json on the server
  and the changelog modal on the website will automatically format the newest update properly

"""

import codecs
import json

# Extract data from files
try:
    with codecs.open("changelogInput.txt", encoding='utf-8') as log_file:  # utf-8 encoding allows for emojis!
        # Extract lines of input text file
        input_items = log_file.readlines()
        if not input_items:
            raise ValueError("changelogInput.txt is empty")
except FileNotFoundError:
    raise FileNotFoundError("'changelogInput.txt' not found in current directory.")

try:
    with codecs.open("changelog.json", encoding='utf-8') as changelogJSON:
        # Extract current changelog JSON into dictionary array
        changelog = json.load(changelogJSON)
except FileNotFoundError:
    raise FileNotFoundError("'changelog.json' not found in current directory.")


except json.JSONDecodeError:
    with open("changelog.json") as f:
        checkJSONContent = f.read()

    if checkJSONContent == "":
        input("changelog.json is empty. Press enter to add an empty array [].")
        changelog = []  # Adds empty array to JSON
    else:
        raise json.JSONDecodeError

items = []

# Extract each changelog item and append dictionary (aka JSON object) to items
for i in range(len(input_items)):

    item = input_items[i]
    item_type, itemNoTag = item[0:5], item[5:]

    try:
        location, content = itemNoTag.split(":", 1)[0], itemNoTag.split(":", 1)[1]
    except IndexError:
        raise IndexError("No location found for following item, use [TAG] Location: Content format: " + item)

    allowed_locations = ['Sitewide', 'Signing', 'My Virtrolio', 'About Us',
                         'Legal', 'Navbar', 'Viewing', 'FAQ', 'Footer']

    if not (location in allowed_locations):
        raise ValueError("Invalid location used for this item: " + item)

    if item_type == "[NEW]":
        item_type = "NEW"
        item_type_CSS = "changelog-new"
    elif item_type == "[UPD]":
        item_type = "UPD"
        item_type_CSS = "changelog-upd"
    elif item_type == "[FIX]":
        item_type = "FIX"
        item_type_CSS = "changelog-fix"
    else:
        raise ValueError("Invalid [TAG] for item, lease follow '[TAG] Location: Content' format: " + item)

    items.append({
        "type": item_type.strip(),
        "typeCSS": item_type_CSS,
        "location": location.strip(),
        "content": content.strip(),
    })

versionNumber = input("What is the version number? (Example: 1.1.0): ")

# Create a new dictionary (aka JSON object) and input relevant properties
updateDictionary = {
    "versionNumber": "v" + versionNumber,
    "items": items
}

# Insert new update to beginning of changelog dictionary array (so the new entry displays at top on the website)
changelog.insert(0, updateDictionary)

# Rewrite JSON file with proper indentation
with codecs.open("changelog.json", encoding='utf-8', mode="w+") as changelogJSON:
    changelogJSON.write(json.dumps(changelog, indent=2))
