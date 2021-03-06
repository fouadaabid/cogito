# https://console.cloud.google.com/firestore/data/{collection_name}/{document_name}?project={project_id}
# https://console.developers.google.com/apis/api/firestore.googleapis.com/metrics?project={project_id}&authuser=1
from typing import Callable, Dict, Any
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase.member import Member
import enums.class_enumerators as class_enumerators
from pathlib import Path


class Database():
  """
  Google Firebase DB client object
  """
  db: Callable

  def __init__(self, key: str):
    """
    Args:
        key (str): Google Firebase DB's key file location (full path)
    """
    self.key = key
    self.db_client()

  def db_client(self) -> None:
    """
    Use a service account with Firebase DB
    """
    cred = credentials.Certificate(self.key)
    firebase_admin.initialize_app(cred)
    self.db = firestore.client()

  def insert_db(
    self,
    schema: str,
    invoice_id: int,
    id: int,
    name: str,
  ) -> None:
    """
    Insert into Firebase DB
    Use member.Member object to inject client's data in the right table
    Args:
      schema (str): Name of the table to write into in Firebase
      invoice_id (int): Invoice number of the current client
      id (int): Unique identifier of the current client
      name (str): Name of the current client
    """
    _collection = self.db.collection(f'{schema}')
    _collection.document(f'{invoice_id}').set(
        Member(
            f'{id}',
            f'{name}',
        ).to_dict()
    )

  def collect_from_db(self, schema: str = class_enumerators.FireBase.SCHEMA_SENT) -> Dict[int, Dict[str, Any]]:
    """
    Collect from Firebase DB
    Note: Use of CollectionRef stream() is prefered to get()
    Args:
      schema (str): Name of the table to look up in Firebase
    Returns:
      [Dict[int, Dict[str, Any]]]: the extract from the Firebase DB
      For every item in the Dict:
        - The key is the invoice N° (serving in DB as PK)
        - The value is a Dict containing the client details and timestamp
    """
    _collection = self.db.collection(f'{schema}')
    past_reminders = dict() 
    docs = _collection.where(f'{class_enumerators.FireBase.SENT_SEASON}', u'==', f'{class_enumerators.FireBase.CURRENT_SEASON}').stream()
    for doc in docs:
        past_reminders[int(doc.id)] = doc.to_dict()
    
    return past_reminders


def initialize_firebase() -> Callable:
  """
  Initialize the Firebase DB
  Args:
    [None]
  Returns:
    [Callable]: Firebase DB client
  """
  p = Path(f'./{class_enumerators.PathNames.FIREBASE_FOLDER}')
  matches = p.glob(f'{class_enumerators.FireBase.PROJECT_ID}*.json')
  for i, match in enumerate(matches):
      if i > 0:
          raise(ValueError(f"Too many json files matching name of Firebase key for project {class_enumerators.FireBase.PROJECT_ID}"))
      key = match
  try:
      firebase = Database(key)
  except Exception:
      raise NameError(f"No match found for Firebase's key -> Verify the json file is in folder ./{class_enumerators.PathNames.FIREBASE_FOLDER}")
  
  return firebase