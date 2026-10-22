import os
import atexit
from mongoengine import connect
from mongoengine.connection import get_db
from dotenv import load_dotenv
from bson.json_util import dumps, loads

load_dotenv()

def dump_mock_db():
    try:
        db = get_db()
        data = {}
        # mongomock might not support list_collection_names perfectly, so we use known collections
        for coll_name in ['users', 'prediction_history']:
            data[coll_name] = list(db[coll_name].find())
        target_path = '/tmp/mock_db.json' if os.environ.get('VERCEL') else 'mock_db.json'
        with open(target_path, 'w') as f:
            f.write(dumps(data))
    except Exception as e:
        pass

def load_mock_db():
    try:
        target_path = '/tmp/mock_db.json' if os.environ.get('VERCEL') else 'mock_db.json'
        if not os.path.exists(target_path) and os.path.exists('mock_db.json'):
            target_path = 'mock_db.json'
            
        if os.path.exists(target_path):
            with open(target_path, 'r') as f:
                data = loads(f.read())
            db = get_db()
            for coll_name, docs in data.items():
                if docs:
                    db[coll_name].insert_many(docs)
    except Exception as e:
        pass

def init_db():
    mongo_uri = os.environ.get('MONGO_URI')

    if not mongo_uri or mongo_uri == 'mongodb://localhost:27017/disease_prediction':
        print("Warning: MONGO_URI not properly set. Falling back to in-memory mongomock with local file persistence.")
        try:
            import mongomock
        except ModuleNotFoundError:
            raise RuntimeError(
                "mongomock is required for local fallback mode. Install it with: pip install mongomock"
            )
        connect('disease_prediction', host='localhost', mongo_client_class=mongomock.MongoClient)
        load_mock_db()
    else:
        try:
            connect(host=mongo_uri, serverSelectionTimeoutMS=4000)
            print("Connected to MongoDB Atlas")
        except Exception as e:
            print(f"Warning: Failed to connect to MongoDB Atlas ({e}). Falling back to in-memory mongomock.")
            try:
                import mongomock
                connect('disease_prediction', host='localhost', mongo_client_class=mongomock.MongoClient)
                load_mock_db()
            except Exception as e2:
                print(f"Fallback error: {e2}")
