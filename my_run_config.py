db_files = [
    # "test2.db",
    # "users.db",
    "A1_commerce.db",
    "A1_msgstore.db",
    "A1_wa.db",
    "A2_core.db",
    "A2_journal.db",
    "A2_main.db",
    "A3_account1cache4.db",
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
        "desc": "a unique identifier for a destination to which electronic mail (email) can be sent and received over the internet or a private network"
    },
    "PHONE": {
        "type":"US phone number",
        "regex": r"\+?[0-9]{1,4}[- .]?\(?[0-9]{1,3}?\)?[- .]?[0-9]{1,4}[- .]?[0-9]{1,4}[- .]?[0-9]{1,9}",
        "desc": "a US phone number is a 10-digit NANP number (area code + exchange + line) that may be written as 2023133725, 202-313-3725, (202) 313-3725, 202.313.3725, +1 202 313 3725, or 1-202-313-3725"
    },
    "USERNAME": {
        "type":"username",
        "regex": r"\b[a-zA-Z][a-zA-Z0-9._-]{2,51}\b",
        "desc": "a username (also called a login name, user ID, or account name) is a unique string of characters that identifies a user on a computer system, website, application, or online platform. It is often created by the user during the registration process and is used in combination with a password to authenticate the user's identity"
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
    "regex": r"(?is)\b("
             r"(?:P\.?\s*O\.?\s*BOX|POST\s+OFFICE\s+BOX)\s*\d{1,6}"
             r"|"
             r"(?:\d{1,7}\s*)?"                                  # OPTIONAL street number
             r"(?:[A-Z0-9][A-Z0-9'.,/#\-]*\s*){1,25}?"            # optional-ish tokens before suffix
             r"(?:AVE|AVENUE|ST|STREET|RD|ROAD|BLVD|BOULEVARD|DR|DRIVE|LN|LANE|CT|COURT|PL|PLACE|WAY|"
             r"PKWY|PARKWAY|CIR|CIRCLE|TER|TERRACE|HWY|HIGHWAY|TRL|TRAIL|SQ|SQUARE|PIKE|LOOP|RUN|WALK|PATH|BYP|BYPASS)\b"
             r"(?:\s*(?:,|\s)\s*(?:N|S|E|W|NE|NW|SE|SW))?"        # optional directional
             r"(?:.{0,60}?\b\d{5}(?:-\d{4})?\b)?"                 # optional ZIP nearby
             r")\b",
    "desc": "a US postal address is a street-level mailing location in the United States, commonly appearing as a street name and suffix (e.g., 'Market St') optionally with a street number (e.g., '1500 Market St'), unit, city/state, ZIP, or a PO Box (e.g., 'P.O. Box 123')"
}
}

