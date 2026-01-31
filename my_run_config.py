db_files = [
    # "test2.db",
    # "users.db",
    # "A1_commerce.db",
    # "A1_msgstore.db",
    # "A1_wa.db",
    # "A2_core.db",
    # "A2_journal.db",
    # "A2_main.db",
    # "A3_account1cache4.db",
    "A3_account2cache4.db",
    "A3_account3cache4.db",
    "A4_gmm_myplaces.db",
    "A4_gmm_storage.db",
    "A4_peopleCache_sharononeil368@gmail.com_com.google_14.db",
    "A5_SBrowser.db",
    "A5_SBrowser2.db",
    "A5_searchengine.db",
    "I1_CallHistory.sqlite",
    "I1_ChatStorage.sqlite",
    "I1_ContactsV2.sqlite",
    "I2_AddressBook.sqlitedb",
    "I2_AddressBookImages.sqlitedb",
    "I3_sms.db",
    "I4_CloudTabs.db",
    "I4_History.db",
    "I5_Calendar.sqlitedb",
    "I5_Extras.db", 
]

PII_CONFIG = {
    "EMAIL": {
        "type":"email address",
        "regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "desc": "a unique identifier for a destination to which electronic mail (email) can be sent and received over the internet; examples include jane.doe@example.com, john.smith@provider.net, dev-team@startup.io, and user.name+label@domain.org"
        },
    "PHONE": {
        "type":"US phone number",
        "regex": r"\+?[0-9]{1,4}[- .]?\(?[0-9]{1,3}?\)?[- .]?[0-9]{1,4}[- .]?[0-9]{1,4}[- .]?[0-9]{1,9}",
        "desc": "a US phone number is a 10-digit NANP number (area code + exchange + line) that may be written as 2023133725, 202-313-3725, (202) 313-3725, 202.313.3725, +1 202 313 3725, or 1-202-313-3725"
    },
    "USERNAME": {
        "type":"username",
        "regex": r"\b[a-zA-Z][a-zA-Z0-9._-]{2,51}\b",
        "desc": "a username is a short textual identifier chosen by a user to represent their account or public handle within an application or service it is stored as plain text contains no whitespace does not include a domain component and is intended for human recognition rather than internal system uniqueness"

    },
    "PERSON_NAME": {
        "type":"person name",
        "regex": r"[A-Za-z][A-Za-z\s\.\-]{1,50}",
        "desc": "a loosely structured human name-like strings that typically consist of a first name, a first name and a last name, and may also include middle names, initials, prefixes (e.g., Mr., Dr.), and suffixes (e.g., Jr., Sr.)"
    },
    "POSTAL_ADDRESS": {
    "type": "US postal address",
    # MAX RECALL prefilter (street number optional).
    # Matches either:
    #  (1) PO Box patterns, OR
    #  (2) optional street number + some tokens + a street suffix, OR
    #  (3) street suffix with nearby tokens (even without a number).
    "regex": (
        r"(?i)\b(?:"
        r"p\.?\s*o\.?\s*box|post\s+office\s+box|"
        r"ave\.?|avenue|"
        r"st\.?|street|"
        r"rd\.?|road|"
        r"blvd\.?|boulevard|"
        r"dr\.?|drive|"
        r"ln\.?|lane|"
        r"ct\.?|court|"
        r"pl\.?|place|"
        r"way|"
        r"pkwy\.?|parkway|"
        r"cir\.?|circle|"
        r"ter\.?|terrace|"
        r"hwy\.?|highway|"
        r"trl\.?|trail|"
        r"sq\.?|square|"
        r"pike|"
        r"loop|"
        r"run|"
        r"walk|"
        r"path|"
        r"byp\.?|bypass|"
        r"(?:n|s|e|w|ne|nw|se|sw)\b"
        r")\b"
    ),
    "desc": "a US postal address is a street-level mailing location in the United States, commonly appearing as a street name and suffix (e.g., 'Market St') optionally with a street number (e.g., '1500 Market St'), unit, city/state, ZIP, or a PO Box (e.g., 'P.O. Box 123')"
}
}

