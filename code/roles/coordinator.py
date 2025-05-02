
# code/roles/coordinator.py

class Coordinator:
    """
    Coordinator class defines actions available to users with the 'coordinator' role.
    Coordinators are responsible for approving or rejecting booking requests
    and managing the list of workers available to be scheduled.
    """

    def __init__(self, db_conn, user_id):
        """
        Initialize the Coordinator object.

        Parameters:
        - db_conn: an active SQLite database connection
        - user_id: the ID of the currently logged-in coordinator
        """
        self.conn = db_conn
        self.user_id = user_id

    # -------------------------
    # Booking Request Handling
    # -------------------------

    def get_pending_bookings(self):
        """
        Retrieve all pending booking requests for approval.

        Returns:
        - List of tuples: (booking_id, worker_name, shift_id, requested_by, request_time)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT b.id, w.name, b.shift_id, b.requested_by, b.request_time
            FROM bookings b
            JOIN workers w ON b.worker_id = w.id
            WHERE b.status = 'pending'
            ORDER BY b.request_time ASC
        """)
        return cursor.fetchall()

    def approve_booking(self, booking_id):
        """
        Approve a pending booking request.

        Parameters:
        - booking_id: ID of the booking to approve
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'approved',
                approved_by = ?,
                decision_time = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
        """, (self.user_id, booking_id))
        self.conn.commit()

    def reject_booking(self, booking_id):
        """
        Reject a pending booking request.

        Parameters:
        - booking_id: ID of the booking to reject
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'rejected',
                approved_by = ?,
                decision_time = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
        """, (self.user_id, booking_id))
        self.conn.commit()

    def cancel_booking(self, booking_id):
        """
        Cancel an already approved booking.

        Parameters:
        - booking_id: ID of the booking to cancel

        Notes:
        - This is different from rejection, which applies to pending requests.
        - This should only be used to cancel previously approved bookings.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'cancelled',
                approved_by = ?,
                decision_time = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'approved'
        """, (self.user_id, booking_id))
        self.conn.commit()

    # -------------------------
    # Worker Management
    # -------------------------

    def add_worker(self, name):
        """
        Add a new worker to the system.

        Parameters:
        - name: Full name of the worker
        - The current coordinator will be recorded as the one who added this worker.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO workers (name, added_by)
            VALUES (?, ?)
        """, (name, self.user_id))
        self.conn.commit()

    def remove_worker(self, worker_id):
        """
        Remove a worker by their ID.

        Parameters:
        - worker_id: ID of the worker to be removed

        Notes:
        - Only possible if the worker is not currently booked or assigned
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
        self.conn.commit()

    def list_workers(self):
        """
        Retrieve a list of all workers currently in the system.

        Returns:
        - List of tuples: (id, name, added_by)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, added_by FROM workers ORDER BY name")
        return cursor.fetchall()
