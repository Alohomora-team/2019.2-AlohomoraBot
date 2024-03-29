"""
Util functions that create information in database
"""
try:
    from models import Resident, Visitor, Admin
    from models import Session
except:
    from db.models import Resident, Visitor, Admin
    from db.models import Session

# Create
def create_resident(cpf, block, apartment, chat_id, token):
    """
    Insert a resident in database
    """
    session = Session()

    resident = Resident(
            cpf=cpf,
            block=block,
            apartment=apartment,
            chat_id=chat_id,
            token=token
            )

    session.add(resident)

    try:
        session.commit()
    except:
        print("[ERROR]: Resident already exists in database")

    session.close()

def create_visitor(cpf, chat_id):
    """
    Insert a visitor in database
    """
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

def create_admin(email, chat_id, token):
    """
    Insert a administrador in database
    """
    session = Session()

    admin = Admin(
            email=email,
            chat_id=chat_id,
            token=token
            )

    session.add(admin)

    try:
        session.commit()
    except:
        print("[ERROR]: Admin already exists in database")

    session.close()

# Delete
def delete_resident(cpf):
    """
    Remove a resident from database
    """
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
    """
    Remove a visitor from database
    """
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
    """
    Remove a admin from database
    """
    session = Session()

    admin = session.query(Admin).\
            filter_by(email=email).first()

    try:
        session.delete(admin)
        session.commit()
    except:
        print("[ERROR]: Admin not found in database")

    session.close()

# Update
def update_resident(cpf, **kwargs):
    """
    Update resident information
    """
    new_cpf = kwargs.get('new_cpf')
    block = kwargs.get('blcok')
    apartment = kwargs.get('apartment')
    chat_id = kwargs.get('chat_id')
    token = kwargs.get('token')

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

        if token:
            resident.token = token

    session.commit()
    session.close()

def update_visitor(cpf, **kwargs):
    """
    Update visitor information from database
    """
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
    """
    Update admin information
    """
    new_email = kwargs.get('new_email')
    chat_id = kwargs.get('chat_id')
    token = kwargs.get('token')

    session = Session()

    admin = session.query(Admin).\
            filter_by(email=email).first()

    if admin:

        if new_email:
            admin.email = new_email

        if chat_id:
            admin.chat_id = chat_id

        if token:
            admin.token = token

    session.commit()
    session.close()

# Query

# Resident
def get_resident_chat_id(cpf):
    """
    Get a chat_id of a resident
    """
    session = Session()

    resident = session.query(Resident).\
            filter_by(
                    cpf=cpf).first()

    session.close()

    if resident:
        return resident.chat_id
    else:
        return None

def get_resident_apartment(chat_id):
    """
    Get the apartment of a resident
    """
    session = Session()

    resident = session.query(Resident).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if resident:
        return [resident.block, resident.apartment]
    else:
        return None

def get_residents_chat_ids(block, apartment):
    """
    List resident chat ids
    """
    session = Session()

    residents_chat_ids = [resident.chat_id for resident in session.query(Resident).\
            filter_by(block=block, apartment=apartment).all()]

    session.close()

    return residents_chat_ids

def get_resident_cpf(chat_id):
    """
    Get a chat_id of a resident
    """
    session = Session()

    resident = session.query(Resident).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if resident:
        return resident.cpf
    else:
        return None

def get_resident_token(chat_id):
    """
    Get a chat_id of a resident
    """
    session = Session()

    resident = session.query(Resident).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if resident:
        return resident.token
    else:
        return None

def resident_exists(chat_id):
    """
    Check if a resident exists in database
    """
    session = Session()

    resident = session.query(Resident).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if resident:
        return True
    else:
        return False

# Visitor
def get_visitor_chat_id(cpf):
    """
    Get a chat_id of a visitor
    """
    session = Session()

    visitor = session.query(Visitor).\
            filter_by(
                    cpf=cpf).first()

    session.close()

    if visitor:
        return visitor.chat_id
    else:
        return None

def get_visitor_cpf(chat_id):
    """
    Get the cpf of a visitor
    """
    session = Session()

    visitor = session.query(Visitor).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if visitor:
        return visitor.cpf
    else:
        return None

def visitor_exists(chat_id):
    """
    Check if a visitor exists in database
    """
    session = Session()

    visitor = session.query(Visitor).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if visitor:
        return True
    else:
        return False

# Admin
def get_admin_chat_id(email):
    """
    Get a administrador chat_id
    """

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
    """
    List all chat ids of admin
    """

    session = Session()

    admins_chat_ids = [admin.chat_id for admin in session.query(Admin)]

    session.close()

    return admins_chat_ids

def get_admin_token(chat_id):
    """
    Get a administrador chat_id
    """

    session = Session()

    admin = session.query(Admin).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if admin:
        return admin.token
    else:
        return None

def admin_exists(chat_id):
    """
    Check if a admin exists in database
    """
    session = Session()

    admin = session.query(Admin).\
            filter_by(
                    chat_id=chat_id).first()

    session.close()

    if admin:
        return True
    else:
        return False
