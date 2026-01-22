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
    # "A3_account2cache4.db",
    # "A3_account3cache4.db",
    # "A4_gmm_myplaces.db",
    # "A4_gmm_storage.db",
    # "A4_peopleCache_sharononeil368@gmail.com_com.google_14.db",
    # "A5_SBrowser.db",
    # "A5_SBrowser2.db",
    # "A5_searchengine.db",
    # "I1_CallHistory.sqlite",
    # "I1_ChatStorage.sqlite",
    # "I1_ContactsV2.sqlite",
    # "I2_AddressBook.sqlitedb",
    # "I2_AddressBookImages.sqlitedb",
    # "I3_sms.db",
    # "I4_CloudTabs.db",
    # "I4_History.db",
    # "I5_Calendar.sqlitedb",
    # "I5_Extras.db",
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
        "desc": "a username (also called a login name, user ID, or account name) is a unique string of characters that identifies a user on a computer system, website, application, or online platform"
    },
    "PERSON_NAME": {
        "type":"person's name",
        "regex": r"[A-Za-z][A-Za-z\s\.\-]{1,50}",
        "desc": "a loosely structured human name-like strings that typically consist of a first name, a first name and a last name, and may also include middle names, initials, prefixes (e.g., Mr., Dr.), and suffixes (e.g., Jr., Sr.)"
    }
}

