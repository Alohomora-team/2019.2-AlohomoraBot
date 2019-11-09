try:
    from models import Resident, Visitor, Admin
    from models import Session
except:
    from db.models import Resident, Visitor, Admin
    from db.models import Session

def create_resident(cpf, block, apartment, chat_id):
    session = Session()

    resident = Resident(
            cpf=cpf,
            block=block,
            apartment=apartment,
            chat_id=chat_id
            )

    session.add(resident)

    try:
        session.commit()
    except:
        print("[ERROR]: Resident already exists in database")

    session.close()

def create_visitor(cpf, chat_id):
    session = Session()

    visitor = Visitor(
            cpf=cpf,
            chat_id=chat_id
            )

    session.add(visitor)

    try:
        session.commit()
    except:
        print("[ERROR]: Visitor already exists in database")

    session.close()

def create_admin(email, chat_id):
    session = Session()

    admin = Admin(
            email=email,
            chat_id=chat_id
            )

    session.add(admin)

    try:
        session.commit()
    except:
        print("[ERROR]: Admin already exists in database")

    session.close()

def delete_resident(cpf):
    session = Session()

    resident = session.query(Resident).\
            filter_by(cpf=cpf).first()

    try:
        session.delete(resident)
        session.commit()
    except:
        print("[ERROR]: Resident not found in database")

    session.close()

def delete_visitor(cpf):
    session = Session()

    visitor = session.query(Visitor).\
            filter_by(cpf=cpf).first()

    try:
        session.delete(visitor)
        session.commit()
    except:
        print("[ERROR]: Visitor not found in database")

    session.close()

def delete_admin(email):
    session = Session()

    admin = session.query(Admin).\
            filter_by(email=email).first()

    try:
        session.delete(admin)
        session.commit()
    except:
        print("[ERROR]: Admin not found in database")

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

def get_residents_chat_ids(block, apartment):
    session = Session()

    residents_chat_ids = [resident.chat_id for resident in session.query(Resident).\
            filter_by(block=block, apartment=apartment).all()]

    session.close()

    return residents_chat_ids

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

    admins_chat_ids = [admin.chat_id for admin in session.query(Admin)]

    session.close()

    return admins_chat_ids
