# code/roles/admin.py

class Admin:
    """
    Admin class encapsulates actions that can only be performed by system administrators.
    Admins are responsible for managing user accounts (coordinators and local managers),
    but cannot delete themselves or other admins.
    """

    def __init__(self, db_conn, user_id):
        """
        Initialize the Admin object.

        Parameters:
        - db_conn: an active SQLite database connection
        - user_id: the ID of the currently logged-in admin account
        """
        self.conn = db_conn
        self.user_id = user_id

    def add_account(self, name, username, email, password, role):
        """
        Create a new user account in the system.

        Parameters:
        - name: full name of the new user
        - username: unique login username
        - email: user's email address (must be unique)
        - password: plaintext password (will be hashed)
        - role: must be one of 'coordinator' or 'local_manager'

        Notes:
        - Admin creation is handled separately on first-run.
        - Passwords are hashed before storage.
        """
        from code.utils.db import hash_password
        cursor = self.conn.cursor()
        hashed = hash_password(password)
        cursor.execute("""
            INSERT INTO accounts (name, username, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, (name, username, email, hashed, role))
        self.conn.commit()

    def remove_account(self, account_id):
        """
        Remove an account by its ID.

        Parameters:
        - account_id: the ID of the account to delete

        Rules:
        - Admins cannot remove accounts with the role 'admin'
        - Admins cannot remove themselves

        Raises:
        - Exception if the target account is also an admin
        """
        cursor = self.conn.cursor()

        # Check the role of the account to delete
        cursor.execute("SELECT role FROM accounts WHERE id = ?", (account_id,))
        result = cursor.fetchone()

        if not result:
            raise Exception("Account not found.")

        role = result[0]

        if role == 'admin':
            raise Exception("Admin accounts cannot be removed.")

        if account_id == self.user_id:
            raise Exception("You cannot remove your own account.")

        # Proceed with deletion
        cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self.conn.commit()

    def list_accounts(self):
        """
        Retrieve a list of all user accounts (excluding the currently logged-in admin).

        Returns:
        - List of tuples: (id, name, username, email, role)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, username, email, role
            FROM accounts
            WHERE id != ?
            ORDER BY role, name
        """, (self.user_id,))
        return cursor.fetchall()

