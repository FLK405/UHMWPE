from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Role, Fibers, Resins, Composites, Literature_Standard, PrecursorResin_SpinningProcess # Assuming EndProduct will be added or handled
# Placeholder for EndProduct if not yet in models, actual import needed when model exists
try:
    from .models import EndProduct
except ImportError:
    # Define a dummy EndProduct for now if it does not exist, so the code doesn't break
    # This should be replaced by the actual model definition.
    class EndProduct:
        pass

from sqlalchemy import or_, func
from datetime import datetime
from .decorators import roles_required # Import the decorator

# --- Helper Functions ---
def user_to_dict(user):
    if not user:
        return None
    return {
        'UserID': user.UserID,
        'Username': user.Username,
        'Email': user.Email,
        'FirstName': user.FirstName,
        'LastName': user.LastName,
        'RoleID': user.RoleID,
        'RoleName': user.role.RoleName if user.role else None, # Include role name
        'IsActive': user.IsActive,
        'LastLoginDate': user.LastLoginDate.isoformat() if user.LastLoginDate else None,
        'DateCreated': user.DateCreated.isoformat() if user.DateCreated else None,
        'DateModified': user.DateModified.isoformat() if user.DateModified else None
    }

def role_to_dict(role):
    if not role:
        return None
    return {
        'RoleID': role.RoleID,
        'RoleName': role.RoleName,
        'Description': role.Description
    }

# --- Main Blueprint ---
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route('/')
def index():
    return render_template('uhmwpe_db_prototype_v4_2.html')

# --- API Blueprint (for CRUD operations etc.) ---
# This is a placeholder for where other API endpoints would go (Users, Roles, etc.)
# Based on previous subtasks, User and Role CRUD should be here.
api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

# Example: User CRUD (assuming these were added in a previous step)
@api_bp.route('/users', methods=['POST'])
@roles_required(['Administrator'])
def create_user():
    data = request.get_json()
    if not data or not data.get('Username') or not data.get('PasswordHash') or not data.get('Email'):
        return jsonify({'error': 'Missing required fields (Username, PasswordHash, Email)'}), 400

    if User.query.filter_by(Username=data['Username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(Email=data['Email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(data['PasswordHash']) # Assuming PasswordHash is the plain password for creation
    new_user = User(
        Username=data['Username'],
        PasswordHash=hashed_password,
        Email=data['Email'],
        FirstName=data.get('FirstName'),
        LastName=data.get('LastName'),
        RoleID=data.get('RoleID'),
        IsActive=data.get('IsActive', True)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_to_dict(new_user)), 201

@api_bp.route('/users', methods=['GET'])
@roles_required(['Administrator'])
def get_users():
    users = User.query.all()
    return jsonify([user_to_dict(user) for user in users]), 200

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@roles_required(['Administrator'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_to_dict(user)), 200

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@roles_required(['Administrator'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'Username' in data and data['Username'] != user.Username:
        if User.query.filter_by(Username=data['Username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.Username = data['Username']

    if 'Email' in data and data['Email'] != user.Email:
        if User.query.filter_by(Email=data['Email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user.Email = data['Email']

    if 'PasswordHash' in data and data['PasswordHash']: # Assuming PasswordHash is the new plain password
        user.PasswordHash = generate_password_hash(data['PasswordHash'])

    user.FirstName = data.get('FirstName', user.FirstName)
    user.LastName = data.get('LastName', user.LastName)
    user.RoleID = data.get('RoleID', user.RoleID)
    user.IsActive = data.get('IsActive', user.IsActive)
    user.DateModified = datetime.utcnow()

    db.session.commit()
    return jsonify(user_to_dict(user)), 200

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@roles_required(['Administrator'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

# Example: Role CRUD
@api_bp.route('/roles', methods=['POST'])
@roles_required(['Administrator'])
def create_role():
    data = request.get_json()
    if not data or not data.get('RoleName'):
        return jsonify({'error': 'Missing RoleName'}), 400
    if Role.query.filter_by(RoleName=data['RoleName']).first():
        return jsonify({'error': 'RoleName already exists'}), 400

    new_role = Role(
        RoleName=data['RoleName'],
        Description=data.get('Description')
    )
    db.session.add(new_role)
    db.session.commit()
    return jsonify(role_to_dict(new_role)), 201

@api_bp.route('/roles', methods=['GET'])
@roles_required(['Administrator'])
def get_roles():
    roles = Role.query.all()
    return jsonify([role_to_dict(role) for role in roles]), 200

@api_bp.route('/roles/<int:role_id>', methods=['GET'])
@roles_required(['Administrator'])
def get_role(role_id):
    role = Role.query.get_or_404(role_id)
    return jsonify(role_to_dict(role)), 200

@api_bp.route('/roles/<int:role_id>', methods=['PUT'])
@roles_required(['Administrator'])
def update_role(role_id):
    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'RoleName' in data and data['RoleName'] != role.RoleName:
        if Role.query.filter_by(RoleName=data['RoleName']).first():
            return jsonify({'error': 'RoleName already exists'}), 400
        role.RoleName = data['RoleName']

    role.Description = data.get('Description', role.Description)
    db.session.commit()
    return jsonify(role_to_dict(role)), 200

@api_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@roles_required(['Administrator'])
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    # Add check for existing users with this role before deleting
    if User.query.filter_by(RoleID=role_id).first():
        return jsonify({'error': 'Cannot delete role: Users are currently assigned to this role.'}), 400
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted successfully'}), 200


@api_bp.route('/search', methods=['GET'])
@roles_required(['Administrator', 'User', 'Viewer']) # Or adjust roles as needed for search access
def global_search():
    query_term = request.args.get('q', '').strip()

    if not query_term or len(query_term) < 2: # Minimum query length
        return jsonify({'message': 'Search term must be at least 2 characters long.', 'results': []}), 400

    search_pattern = f"%{query_term}%"
    results = []

    # Search Fibers
    # Specified fields: BatchNo, Grade, Manufacturer, Source, Remarks. (Using FiberName as primary label)
    # Actual fields in Fibers model: FiberName, LinearDensity, Diameter, ProductionDate, Manufacturer_ResearchGroup, Notes
    # Will adapt to available fields. Assuming FiberName and Manufacturer_ResearchGroup, Notes are relevant.
    fibers = Fibers.query.filter(
        or_(
            Fibers.FiberName.ilike(search_pattern),
            Fibers.Manufacturer_ResearchGroup.ilike(search_pattern),
            Fibers.Notes.ilike(search_pattern)
        )
    ).limit(10).all()
    for item in fibers:
        results.append({
            'type': 'Fiber',
            'id': item.FiberID,
            'label': f"Fiber: {item.FiberName}",
            'match_context': f"Name: {item.FiberName}, Manufacturer: {item.Manufacturer_ResearchGroup}", # Simplified context
            'view_path_hint': f"#/fiber_performance?fiber_id={item.FiberID}"
        })

    # Search Resins
    # Specified: Manufacturer, Grade, BatchNo, ResinType, Supplier, Remarks. (Using ResinName as primary label)
    # Actual: ResinName, Manufacturer, IntrinsicViscosity, MolecularWeight_Mn, Mw, Mz, ComonomerType, AdditiveType, Notes
    resins = Resins.query.filter(
        or_(
            Resins.ResinName.ilike(search_pattern),
            Resins.Manufacturer.ilike(search_pattern),
            Resins.ComonomerType.ilike(search_pattern),
            Resins.AdditiveType.ilike(search_pattern),
            Resins.Notes.ilike(search_pattern)
        )
    ).limit(10).all()
    for item in resins:
        results.append({
            'type': 'Resin',
            'id': item.ResinID,
            'label': f"Resin: {item.ResinName}",
            'match_context': f"Name: {item.ResinName}, Manufacturer: {item.Manufacturer}",
            'view_path_hint': f"#/resin_interface?tab=resin_basic&resin_id={item.ResinID}"
        })

    # Search PrecursorResin_SpinningProcess
    # Specified: FiberBatchNo (target fiber), ResinGrade_Used, Remarks
    # Actual: ProcessName, Solvent, Notes. Links to Resin.
    spinning_processes = PrecursorResin_SpinningProcess.query.join(Resins).filter(
        or_(
            PrecursorResin_SpinningProcess.ProcessName.ilike(search_pattern),
            PrecursorResin_SpinningProcess.Solvent.ilike(search_pattern),
            PrecursorResin_SpinningProcess.Notes.ilike(search_pattern),
            Resins.ResinName.ilike(search_pattern) # Search by linked resin name
        )
    ).limit(10).all()
    for item in spinning_processes:
        results.append({
            'type': 'Spinning Process',
            'id': item.SpinningProcessID,
            'label': f"Spinning: {item.ProcessName}",
            'match_context': f"Process: {item.ProcessName}, Resin: {item.resin.ResinName if item.resin else 'N/A'}",
            'view_path_hint': f"#/resin_spinning?spinning_process_id={item.SpinningProcessID}"
        })

    # Search Composites
    # Specified: CompositeName, ReinforcementStructure, ManufacturingProcess_Detail, LayupSequence, Remarks.
    # Actual: CompositeName, ManufacturingProcess, FiberVolumeFraction, PlyStackingSequence, CuringCycleDetails, Notes
    composites = Composites.query.filter(
        or_(
            Composites.CompositeName.ilike(search_pattern),
            Composites.ManufacturingProcess.ilike(search_pattern),
            Composites.PlyStackingSequence.ilike(search_pattern),
            Composites.Notes.ilike(search_pattern)
        )
    ).limit(10).all()
    for item in composites:
        results.append({
            'type': 'Composite',
            'id': item.CompositeID,
            'label': f"Composite: {item.CompositeName}",
            'match_context': f"Name: {item.CompositeName}, Process: {item.ManufacturingProcess}",
            'view_path_hint': f"#/composite_performance?composite_id={item.CompositeID}"
        })

    # Search Literature_Standard
    # Specified: Title_StandardNo, Authors_IssuingBody, Keywords, Abstract_Scope_Description, Remarks.
    # Actual: DocumentType, Title_StandardNo, Authors_IssuingBody, PublicationYear, Journal_Publisher, Keywords, Abstract_Scope, Notes
    literature = Literature_Standard.query.filter(
        or_(
            Literature_Standard.Title_StandardNo.ilike(search_pattern),
            Literature_Standard.Authors_IssuingBody.ilike(search_pattern),
            Literature_Standard.Keywords.ilike(search_pattern),
            Literature_Standard.Abstract_Scope.ilike(search_pattern),
            Literature_Standard.Notes.ilike(search_pattern),
            Literature_Standard.Journal_Publisher.ilike(search_pattern)
        )
    ).limit(10).all()
    for item in literature:
        results.append({
            'type': 'Literature/Standard',
            'id': item.DocumentID,
            'label': f"Doc: {item.Title_StandardNo}",
            'match_context': f"Title: {item.Title_StandardNo}, Authors: {item.Authors_IssuingBody}",
            'view_path_hint': f"#/literature_standard?doc_id={item.DocumentID}" # Assuming a way to link
        })

    # Search EndProducts (if model exists and has been imported)
    # Specified: ProductName, Manufacturer, ProductType, ProtectionLevel_Claimed, StructureDescription_ArealDensity, Remarks.
    if EndProduct and hasattr(EndProduct, 'query'): # Check if EndProduct is a valid SQLAlchemy model
        try:
            end_products = EndProduct.query.filter(
                or_(
                    EndProduct.ProductName.ilike(search_pattern) if hasattr(EndProduct, 'ProductName') else False,
                    EndProduct.Manufacturer.ilike(search_pattern) if hasattr(EndProduct, 'Manufacturer') else False,
                    EndProduct.ProductType.ilike(search_pattern) if hasattr(EndProduct, 'ProductType') else False,
                    EndProduct.ProtectionLevel_Claimed.ilike(search_pattern) if hasattr(EndProduct, 'ProtectionLevel_Claimed') else False,
                    EndProduct.StructureDescription_ArealDensity.ilike(search_pattern) if hasattr(EndProduct, 'StructureDescription_ArealDensity') else False,
                    EndProduct.Remarks.ilike(search_pattern) if hasattr(EndProduct, 'Remarks') else False
                )
            ).limit(10).all()
            for item in end_products:
                results.append({
                    'type': 'End Product',
                    'id': item.ProductID if hasattr(item, 'ProductID') else item.id, # Assuming ProductID or id
                    'label': f"Product: {item.ProductName}" if hasattr(item, 'ProductName') else "End Product",
                    'match_context': f"Product: {item.ProductName if hasattr(item, 'ProductName') else 'N/A'}, Manufacturer: {item.Manufacturer if hasattr(item, 'Manufacturer') else 'N/A'}",
                    'view_path_hint': f"#/ballistic_performance?tab=end_products&product_id={item.ProductID if hasattr(item, 'ProductID') else item.id}"
                })
        except Exception as e:
            print(f"Error searching EndProducts (model might be a placeholder or schema mismatch): {e}")


    # Optional: Search Users (Username, FirstName, LastName, Email)
    # users = User.query.filter(
    #     or_(
    #         User.Username.ilike(search_pattern),
    #         User.FirstName.ilike(search_pattern),
    #         User.LastName.ilike(search_pattern),
    #         User.Email.ilike(search_pattern)
    #     )
    # ).limit(5).all()
    # for item in users:
    #     results.append({
    #         'type': 'User',
    #         'id': item.UserID,
    #         'label': f"User: {item.Username}",
    #         'match_context': f"Name: {item.FirstName} {item.LastName}, Email: {item.Email}",
    #         'view_path_hint': f"#/user_management?user_id={item.UserID}" # Fictional path
    #     })

    # Sort results, perhaps by type then label, or by a relevance score if implemented
    results.sort(key=lambda x: (x['type'], x['label']))

    return jsonify(results), 200

# --- Auth Blueprint ---
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or (not data.get('username') and not data.get('email')) or not data.get('password'):
        return jsonify({'error': 'Missing username/email or password'}), 400

    user = None
    if data.get('username'):
        user = User.query.filter_by(Username=data['username']).first()
    elif data.get('email'):
        user = User.query.filter_by(Email=data['email']).first()

    if user and check_password_hash(user.PasswordHash, data['password']):
        if not user.IsActive:
            return jsonify({'error': 'User account is inactive'}), 401

        session['user_id'] = user.UserID
        session['username'] = user.Username
        session['role_id'] = user.RoleID # Assuming RoleID exists on User model

        user.LastLoginDate = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'user': user_to_dict(user)
        }), 200

    return jsonify({'error': 'Invalid username/email or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role_id', None)
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/status', methods=['GET'])
def status():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'logged_in': True,
                'user': user_to_dict(user)
            }), 200
        else: # Should not happen if session user_id is valid
            session.clear() # Clear invalid session
            return jsonify({'logged_in': False, 'error': 'User not found for session ID'}), 404

    return jsonify({'logged_in': False}), 200

# Registration can still be POST /api/users
# If an alias is desired:
# @auth_bp.route('/register', methods=['POST'])
# def register_alias():
#     # This can simply call create_user or re-implement logic
#     # For now, let's assume POST /api/users is sufficient
#     return create_user()
