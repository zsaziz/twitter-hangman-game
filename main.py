from src.game.controller import main
from src.google_utils.firestore_apis import FirestoreClient

DELETE_ALL_PARAM = 'deleteAll'


def invoke(event, context):
    delete_all = False
    # content_type = request.headers['content-type']
    # if content_type == 'application/json':
    #     request_json = request.get_json(silent=True)
    #     if request_json and DELETE_ALL_PARAM in request_json:
    #         delete_all = request_json[DELETE_ALL_PARAM]
    main(delete_all)


if __name__ == '__main__':
    client = FirestoreClient()
    client.create_database('zsaziz-test')