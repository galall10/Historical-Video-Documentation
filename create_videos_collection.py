import sys
sys.path.append('c:\\Users\\maram\\CascadeProjects\\omran-repo\\Historical-Video-Documentation')
from utils.database import connect_to_db

# Connect and create videos collection manually
connect_to_db()

try:
    from utils.database import db
    if db is not None:
        # Create videos collection if it doesn't exist
        collections = db.list_collection_names()
        print(f'Current collections: {collections}')

        if 'cached_videos' not in collections:
            print('Creating cached_videos collection...')
            db.create_collection('cached_videos')
            print('Videos collection created successfully')
        else:
            print('Videos collection already exists')

        # Test inserting a document
        test_video = {
            'landmark_name': 'test_landmark',
            'story_type': 'test',
            'video_path': '/test/path.mp4',
            'metadata': {'test': True}
        }

        result = db.cached_videos.insert_one(test_video)
        print(f'Test document inserted with ID: {result.inserted_id}')

        # Count documents in videos collection
        videos_count = db.cached_videos.count_documents({})
        print(f'Videos collection now has {videos_count} documents')

        # Clean up test document
        db.cached_videos.delete_one({'_id': result.inserted_id})
        print('Test document cleaned up')

        # Final check
        final_collections = db.list_collection_names()
        print(f'Final collections: {final_collections}')

    else:
        print('ERROR: Database is None')

except Exception as e:
    print(f'Error: {e}')
    print(f'Error type: {type(e).__name__}')
