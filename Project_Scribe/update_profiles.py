import json, os
from pathlib import Path

PROFILES_DIR = Path("C:/Azazael/azazael/Project_Scribe/profiles")

# New field names to add to all profiles
NEW_FIELDS = {
    "project": "",           # proposal title
    "amount": "",            # requested amount
    "otherfunding": "",      # other funding
    "requestor": "",         # requestor name
    "email": "",             # contact email
    "pgp": "",               # PGP key
    "website2": "",          # optional website 2
    "website3": "",          # optional website 3
    "website4": "",          # optional website 4
    "pgp": "",               # PGP key
}

# Map old field names to new field names
FIELD_MAPPING = {
    "contact_email": "email",
    "requested_amount": "amount",
    "other_funding": "otherfunding",
    "requestor_name": "requestor",
    "project_title": "project",
    "project_description": "project_description",  # keep
    "contact_name": "requestor",  # map contact_name to requestor
    "contact_email": "email",
    "project_name": "project",  # also map project_name to project
}

def update_profile(profile_path):
    with open(profile_path, encoding='utf-8') as f:
        data = json.load(f)
    
    # Add new fields at top level if not present
    for key, default in NEW_FIELDS.items():
        if key not in data:
            data[key] = default
    
    # Map old field names to new field names (keep both for compatibility)
    for old_key, new_key in FIELD_MAPPING.items():
        if old_key in data and data[old_key] and new_key not in data:
            data[new_key] = data[old_key]
        elif old_key in data and data[old_key] and new_key in data and not data[new_key]:
            data[new_key] = data[old_key]
    
    # Also ensure project field is set from project_name if not present
    if "project" not in data or not data["project"]:
        data["project"] = data.get("project_name", "")
    
    # Ensure email is set from contact_email
    if "email" not in data or not data["email"]:
        data["email"] = data.get("contact_email", "")
    
    # Ensure amount is set from requested_amount or funding_amount
    if "amount" not in data or not data["amount"]:
        data["amount"] = data.get("requested_amount", data.get("funding_amount", "").replace("$", "").replace(",", ""))
    
    # Ensure requestor is set from contact_name
    if "requestor" not in data or not data["requestor"]:
        data["requestor"] = data.get("contact_name", "")
    
    # Ensure email is set
    if "email" not in data or not data["email"]:
        data["email"] = data.get("contact_email", "")
    
    # Ensure project is set from project_name
    if "project" not in data or not data["project"]:
        data["project"] = data.get("project_name", "")
    
    # Write back
    with open(profile_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated {profile_path.name}")

def main():
    profiles_dir = Path("C:/Azazael/azazael/Project_Scribe/profiles")
    for profile_path in profiles_dir.glob("*_profile.json"):
        update_profile(profile_path)
    print("All profiles updated!")

if __name__ == "__main__":
    main()