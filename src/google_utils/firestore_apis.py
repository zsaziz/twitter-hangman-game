# local lib
from src.google_utils.common import *

# google lib
from google.cloud import firestore_admin_v1

class FirestoreClient:
    client = None

    def __init__(self):
        self.client = firestore_admin_v1.FirestoreAdminClient()
    
    def create_database(self, database_name):
        # database = firestore_admin_v1.Database(
        #     name=f'{PROJECTS_ID_FULL_PATH}/databases/{DATABASE_ID}',
        #     location=DEFAULT_LOCATION_ID,
        #     type=firestore_admin_v1.Database.DatabaseType.FIRESTORE_NATIVE,

        # )

        request = firestore_admin_v1.CreateDatabaseRequest(
            parent=PROJECTS_ID_FULL_PATH,
            database_id=DATABASE_ID
        )
        operation = self.client.create_database(request=request)
