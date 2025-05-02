# code/roles/local_manager.py

class LocalManager:
    """
    LocalManager class encapsulates actions available to users with the 'local_manager' role.
    Local managers are responsible for viewing available shifts, selecting workers,
    and creating booking requests (which must be approved by a coordinator).
    """

    def __init__(self, db_conn, user_id):
        """
        Initialize the LocalManager object.

        Parameters:
        - db_conn: an active SQLite database connection
        - user_id: the ID of the currently logged-in local manager
        """
        self.conn = db_conn
        self.user_id = user_id

    # -------------------------
    # Booking Creation
    # -------------------------

    def create_booking_request(self, worker_id, shift_id):
        """
        Submit a booking request to assign a worker to a shift.

        Parameters:
        - worker_id: ID of the worker to book
        - shift_id: ID of the shift to assign

        Notes:
        - All requests are stored with status 'pending' until reviewed by a coordinator.
        - Duplicate bookings are prevented by the UNIQUE(worker_id, shift_id) constraint.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO bookings (worker_id, shift_id, requested_by)
            VALUES (?, ?, ?)
        """, (worker_id, shift_id, self.user_id))
        self.conn.commit()

    def view_my_requests(self):
        """
        Retrieve all booking requests made by this local manager.

        Returns:
        - List of tuples: (booking_id, worker_name, shift_id, status, request_time, decision_time)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT b.id, w.name, b.shift_id, b.status, b.request_time, b.decision_time
            FROM bookings b
            JOIN workers w ON b.worker_id = w.id
            WHERE b.requested_by = ?
            ORDER BY b.request_time DESC
        """, (self.user_id,))
        return cursor.fetchall()

    # -------------------------
    # Shift Lookup
    # -------------------------

    def list_available_shifts(self):
        """
        List all shifts currently in the system.

        Returns:
        - List of tuples: (id, location_id, start_time, end_time)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, location_id, start_time, end_time
            FROM shifts
            ORDER BY start_time ASC
        """)
        return cursor.fetchall()

    def list_workers(self):
        """
        Retrieve all workers in the system.
        This allows local managers to see who can be scheduled.

        Returns:
        - List of tuples: (id, name)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM workers ORDER BY name")
        return cursor.fetchall()

