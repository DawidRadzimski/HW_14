from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_
from src.database.models import Contact
from src.schemas import ContactIn, ContactUpdate
from datetime import date, datetime, timedelta


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    """
        Retrieves a list of contacts for a specific user with specified pagination parameters.

        :param skip: The number of contacts to skip.
        :type skip: i nt
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param user: The user to retrieve contacts for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: A list of contacts.
        :rtype: List[Contact]
        """
    return db.query(Contact).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, db: Session) -> Contact:
    """
        Retrieves a single contact with the specified ID for a specific user.

        :param contact_id: The ID of the contact to retrieve.
        :type contact_id: int
        :param user: The user to retrieve the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The contact with the specified ID, or None if it does not exist.
        :rtype: Contact | None
        """
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def find_contact(keyword: str, skip: int, limit: int, db: Session) -> List[Contact]:
    """
        Retrieves a list of contacts with entered keyword for a specified user.

        :param body: The data for the contact to create.
        :type body: ContactIn
        :param user: The user to retrieve the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The list of contacts with the specified keyword.
        :rtype: List[Contact]
        """
    word = f"%{keyword}%"
    query = db.query(Contact).filter(or_(Contact.first_name.ilike(word), Contact.last_name.ilike(
        word), Contact.email.ilike(word))).offset(skip).limit(limit).all()
    return query


async def create_contact(body: ContactIn, db: Session) -> Contact:
    """
        Creates a new contact for a specific user.

        :param body: The data for the contact to create.
        :type body: ContactIn
        :param user: The user to create the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The newly created contact.
        :rtype: Contact
        """
    contact = Contact(name=body.first_name, lastname=body.last_name, email=body.email,
                      phone=body.phone_number, birthday=body.date_of_birth, notes=body.additional_data)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    """
        Removes a single contact with the specified ID for a specific user.

        :param contact_id: The ID of the contact to remove.
        :type contact_id: int
        :param user: The user to remove the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The removed contact, or None if it does not exist.
        :rtype: Contact | None
        """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, db: Session) -> Contact | None:
    """
        Updates a single contact with the specified ID for a specific user.

        :param contact_id: The ID of the contact to update.
        :type contact_id: int
        :param body: The updated data for the contact.
        :type body: ContactUpdate
        :param user: The user to update the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The updated contact, or None if it does not exist.
        :rtype: Contact | None
        """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        if body.name:
            contact.first_name = body.first_name
        if body.lastname:
            contact.last_name = body.last_name
        if body.email:
            contact.email = body.email
        if body.phone:
            contact.phone_number = body.phone_number
        if body.birthday:
            contact.date_of_birth = body.date_of_birth
        if body.notes:
            contact.additional_data = body.additional_data
        db.commit()
        db.refresh(contact)
    return contact


async def get_contacts_birthday_for_next_week(skip: int, limit: int, db: Session) -> List[Contact]:
    """
        Retrieves a list of contacts for a specific user with specified pagination parameters, which have birthdays within the next seven days.

        :param skip: The number of contacts to skip.
        :type skip: int
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param user: The user to retrieve the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: List of contacts who have a birthday in the next seven days, in ascending order by 'birthday'.
        :rtype: List[Contact]
        """
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    query = db.query(Contact).filter(
        or_(
            and_(
                extract("month", today) == extract("month", next_week),
                extract("month", Contact.date_of_birth) == extract("month", today),
                extract("day", Contact.date_of_birth) >= extract("day", today),
                extract("day", Contact.date_of_birth) <= extract("day", next_week)
            ),
            and_(
                extract("month", today) != extract("month", next_week),
                extract("month", Contact.date_of_birth) == extract("month", today),
                extract("day", Contact.date_of_birth) >= extract("day", today)
            ),
            and_(
                extract("month", today) != extract("month", next_week),
                extract("month", Contact.date_of_birth) == extract(
                    "month", next_week),
                extract("day", Contact.date_of_birth) <= extract("day", next_week)
            )
        )).order_by("date_of_birth").offset(skip).limit(limit).all()
    return query