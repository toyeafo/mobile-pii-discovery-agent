db_files = [
    "test2.db",
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
        "type":"email",
        "regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "desc": "valid email addresses. For example: username@domain.tld"
    },
    "PHONE": {
        "type":"phone number",
        "regex": r"\+?[0-9]{1,4}[- .]?\(?[0-9]{1,3}?\)?[- .]?[0-9]{1,4}[- .]?[0-9]{1,4}[- .]?[0-9]{1,9}",
        "desc": "international or local telephone numbers"
    },
    "USERNAME": {
        "type":"username",
        "regex": r"\b[a-zA-Z][a-zA-Z0-9._-]{2,51}\b",
        "desc": "application-specific login usernames created by users for login purposes"
    },
    "PERSON_NAME": {
        "type":"person name",
        "regex": r"[A-Za-z][A-Za-z\s\.\-]{1,50}",
        "desc": "loosely structured human name-like strings"
    }
}

