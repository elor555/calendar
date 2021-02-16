from datetime import datetime
from typing import Dict, Optional, List

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.database.models import Parasha


router = APIRouter()


def create_parasha_object(parashot_fields: Dict[str, Optional[str]])\
        -> Parasha:
    """This function create a parasha object from given fields dictionary.
    It is used for adding the data from the json into the db"""
    return Parasha(
        name=parashot_fields['name'],
        hebrew_name=parashot_fields['hebrew'],
        link=parashot_fields['link'],
        date=datetime.strptime(parashot_fields['date'], '%Y-%m-%d').date()
    )


def get_all_parahot_list(db_session: Session) \
        -> List[Dict[str, Optional[str]]]:
    """This function return all parashot object in list"""
    return db_session.query(Parasha).all()