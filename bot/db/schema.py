from models import Resident, Visitor, Admin
from models import Session

def create_resident(cpf, block, apartment, chat_id):
    session = Session()

    resident = Resident()

    resident.cpf = cpf
    resident.block = block
    resident.apartment = apartment
    resident.chat_id = chat_id

    session.add(resident)
    session.commit()
    session.close()

def create_visitor(cpf, chat_id):
    session = Session()

    visitor = Visitor()

    visitor.cpf = cpf
    visitor.chat_id = chat_id

    session.add(visitor)
    session.commit()
    session.close()

def create_admin(email, chat_id):
    session = Session()

    admin = Admin()

    admin.email = email
    admin.chat_id = chat_id

    session.add(admin)
    session.commit()
    session.close()

def delete_resident(cpf):
    session = Session()

    resident = session.query(Resident).\
            filter_by(cpf=cpf).first()

    session.delete(resident)
    session.commit()
    session.close()
    
def delete_visitor(cpf):
    session = Session()

    visitor = session.query(Visitor).\
            filter_by(cpf=cpf).first()

    session.delete(visitor)
    session.commit()
    session.close()

def delete_admin(email):
    session = Session()

    admin = session.query(Admin).\
            filter_by(email=email).first()

    session.delete(admin)
    session.commit()
    session.close()

def update_resident(cpf, **kwargs):
    new_cpf = kwargs.get('new_cpf')
    block = kwargs.get('blcok')
    apartment = kwargs.get('apartment')
    chat_id = kwargs.get('chat_id')

    session = Session()

    resident = session.query(Resident).\
            filter_by(cpf=cpf).first()

    if resident:

        if new_cpf:
            resident.cpf = new_cpf
    
        if apartment:
            resident.apartment = apartment
    
        if block:
            resident.block = block
    
        if chat_id:
            resident.chat_id = chat_id

    session.commit()
    session.close()

def update_visitor(cpf, **kwargs):
    new_cpf = kwargs.get('new_cpf')
    chat_id = kwargs.get('chat_id')

    session = Session()

    visitor = session.query(Visitor).\
            filter_by(cpf=cpf).first()

    if visitor:

        if new_cpf:
            visitor.cpf = new_cpf
    
        if chat_id:
            visitor.chat_id = chat_id

    session.commit()
    session.close()

def update_admin(email, **kwargs):
    new_email = kwargs.get('new_email')
    chat_id = kwargs.get('chat_id')

    session = Session()

    admin = session.query(Admin).\
            filter_by(email=email).first()
    
    if admin:

        if new_email:
            admin.email = new_email
    
        if chat_id:
            admin.chat_id = chat_id

    session.commit()
    session.close()

def get_resident_chat_id(cpf):
    session = Session()

    resident = session.query(Resident).\
            filter_by(
                    cpf=cpf).first()

    session.close()

    if resident:
        return resident.chat_id
    else:
        return None

def get_visitor_chat_id(cpf):
    session = Session()

    visitor = session.query(Visitor).\
            filter_by(
                    cpf=cpf).first()

    session.close()

    if visitor:
        return visitor.chat_id
    else:
        return None

def get_admin_chat_id(email):
    session = Session()

    admin = session.query(Admin).\
            filter_by(
                    email=email).first()

    session.close()

    if admin:
        return admin.chat_id
    else:
        return None

def get_all_admins_chat_ids():
    session = Session()

    vector = [admin.chat_id for admin in session.query(Admin)]

    session.close()

    return vector
